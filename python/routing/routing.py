# encoding: utf-8
# vim: ts=4 noexpandtab

from re import sub as rsub, match as rmatch, search as rsearch, findall as rfind
from urllib import urlencode
from pyparsing import nestedExpr


def singleton(klass):
    instances = {}

    def get_instance():
        if not klass in instances:
            instances[klass] = klass()

        return instances[klass]

    return get_instance





@singleton
class Mapper:
    _root = None
    _error = None

    _names = []
    _routes = []

    def root(self, **kwargs):
        if kwargs:
            self._root = kwargs
        return self._root

    def error(self, **kwargs):
        if kwargs:
            self._error = kwargs
        return self._error

    def connect(self, route, map=None, **kwargs):
        route = Route(route, map, **kwargs)
        self._names.append(route.name())
        self._routes.append(route)

    def parameterize(self, url):
        # try to find a suitable one
        for route in self._routes:
            parameters = route.parameterize(url)
            if parameters:
                return parameters

        # 404
        return self._error

    def urlize(self, route=None, **kwargs):
        # if urlizing a named route
        if route:
            return self._routes[self._names.index(route)].urlize(**kwargs)

        # if it's the root route
        if kwargs == dict([ (key, kwargs[key]) for key in self._root if key in kwargs ]):
            return '/'

        # try to find suitable one
        for route in self._routes:
            url = route.urlize(**kwargs)
            if url:
                return url

        # bail out
        raise Exception('No route found to generate url')


class Route:
    _name = None
    _route = None
    _map = None
    _regex = None
    _code = None
    _defaults = {}
    _constraints = {}
    _formats = {}
    _limits = {}
    _parameters = []
    _required = []
    _multiple = []

    def __init__(self, route, map=None, **args):
        self._route = route

        # map ourself out
        if map is not None:
            if type(map) == dict:
                self._map = map
            elif type(map) == str:
                self._map = dict(zip(Mapper().args[:map.count('#') + 1], map.split('#')))
            else:
                raise TypeError('map should be either dict or str')
        else:
            self._map = {}

        # set/generate name
        if 'name' in args:
            self._name = name
        elif self._map:
            self._name = '_'.join(self._map.keys())
        else:
            self._name = id(self)

        # set common options
        if 'defaults' in args:
            self._defaults = args['defaults']
        if 'constraints' in args:
            self._constraints = args['constraints']
        if 'formats' in args:
            self._formats = args['formats']
        if 'limits' in args:
            self._limits = args['limits']

        # scan parameter names and parameter types (optional/required, single/multiple)
        l = len(route)
        x = paren = 0
        while x < l:
            c = route[x]
            x += 1

            if c == '(':
                paren += 1
            elif c == ')':
                paren -= 1
            elif c == ':' or c == '*':
                name = []
                while x < l and route[x].isalnum():
                    name.append(route[x])
                    x += 1
                name = ''.join(name)

                self._parameters.append(name)

                if not paren:
                    self._required.append(name)

                if c == '*':
                    self._multiple.append(name)

        # set defaults for action and format
        if 'action' in self._parameters and not 'action' in self._defaults:
            self._defaults['action'] = 'index'
        if 'format' in self._parameters and not 'format' in self._defaults:
            self._defaults['format'] = 'html'

        # build the regular expression with a regular expression (and a couple of string substitutions, though)
        self._regex = rsub('[:*](\\w+)', self._constraintize, route.replace('(', '(?:').replace(')', ')?').replace('.', '\\.'))

        # build the evaluated urlize code with nested expression and a couple of regular expression substitutions
        expr = nestedExpr('(', ')')
        parsed = expr.parseString(''.join(['(', route, ')']))[0]
        self._code = ''.join(['result = ', self._conditionalize(parsed).replace(', ""', '')])

    def name(self):
        return self._name

    def parameterize(self, url):
        match = rmatch(self._regex, url)
        if match:
            return match.groupdict()

    def urlize(self, **parameters):
        # merge required parameters default values if not present
        parameters.update(dict([ (key, self._defaults[key]) for key in self._defaults if key in self._required and key not in parameters ]))

        # check mapping
        if self._map and self._map != dict([ (key, parameters[key]) for key in self._map if key in parameters ]):
            return None

        # check required parameters
        if len([ key for key in self._required if key in parameters ]) < len(self._required):
            return None

        # format values
        for key in parameters:
            if type(parameters[key]) == list:
                if key in self._formats:
                    parameters[key] = [ self._formats[key] % (part) for part in parameters[key] ]

                parameters[key] = '/'.join(parameters[key])
            elif key in self._formats:
                parameters[key] = self._formats[key] % parameters[key]

        # do some evil
        exec self._code

        # check optional query parameters
        query = dict([ (key, parameters[key]) for key in parameters if key not in self._parameters ])

        return ''.join([result, query and '?' or '', query and urlencode(query) or ''])

    def _constraintize(self, match):
        name = match.group(1)

        if name in self._multiple:
            if name in self._constraints:
                constraint = self._constraints[name]
            else:
                constraint = '[^/]+'

            if name in self._limits:
                limit = ''.join(['{', self._limits[name], '}'])
            else:
                limit = '+'

            return ''.join(['(?P<', name, '>(?:', constraint, '/?)', limit, ')'])

        if name in self._constraints:
            constraint = self._constraints[name]
        else:
            constraint = '[^/.]+'

        return ''.join(['(?P<', name, '>', constraint, ')'])

    def _conditionalize(self, args):
        part = args[0]

        next = []
        segments = args[1:]
        for segment in segments:
            next.append(self._conditionalize(segment))
        next = ', '.join(next)
        if next:
            next = ''.join([', ', next]);

        conditions = []
        for name in rfind('[:*](\\w+)', part):
            conditions.append(''.join(['"', name, '" in parameters']))
        if conditions:
            conditions = ' and '.join(conditions)
        else:
            conditions = 'true'

        return ''.join(['((', conditions, ') and "".join(["', rsub('[:*](\\w+)', '", parameters["\\1"], "', part), '"', next, ']) or "")'])
