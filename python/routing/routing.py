# encoding: utf-8
# vim: ts=4 noexpandtab

from re import sub as rsub, match as rmatch, findall as rfind
from urllib import urlencode
from pyparsing import nestedExpr


def build_query(**args):
    if args:
        return ''.join(['?', urlencode(args)])

    return ''


class Mapper:
    _root = None
    _error = None

    _names = []
    _routes = []

    @classmethod
    def root(cls, **kwargs):
        if kwargs:
            cls._root = kwargs
        return cls._root

    @classmethod
    def error(cls, **kwargs):
        if kwargs:
            cls._error = kwargs
        return cls._error

    @classmethod
    def connect(cls, route, **kwargs):
        route = Route(route, **kwargs)
        cls._names.append(route._name)
        cls._routes.append(route)

    @classmethod
    def parameterize(cls, url):
        # try to find a suitable one
        for route in cls._routes:
            parameters = route.parameterize(url)
            if parameters:
                return parameters

        # 404 perhaps
        return cls._error

    @classmethod
    def urlize(cls, **kwargs):
        # if urlizing a named route
        if 'route' in kwargs:
            route = kwargs.pop('route')
            return cls._routes[cls._names.index(route)].urlize(**kwargs)

        # if it's the root route
        if dict([(key, kwargs[key]) for key in cls._root if key in kwargs]) == cls._root:
            return ''.join(['/', build_query(**dict([(key, kwargs[key]) for key in kwargs if key not in cls._root]))])

        # try to find suitable one
        for route in cls._routes:
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

    def __init__(self, route, **kwargs):
        self._route = route

        # set/generate name
        if 'name' in kwargs:
            self._name = kwargs.pop('name')

        # set common options
        if 'defaults' in kwargs:
            self._defaults = kwargs.pop('defaults')
        if 'constraints' in kwargs:
            self._constraints = kwargs.pop('constraints')
        if 'formats' in kwargs:
            self._formats = kwargs.pop('formats')
        if 'limits' in kwargs:
            self._limits = kwargs('limits')

        # everything else should be map then, unless we hav a map argument passed
        if 'map' in kwargs:
            self._map = kwargs.pop('map')
        else:
            self._map = kwargs

        # check name once again and try to set it against map
        if not self._name:
            if self._map:
                self._name = '_'.join([str(value) for value in self._map.values()])
            else:
                self._name = id(self)

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

    def parameterize(self, url):
        match = rmatch(self._regex, url)
        if match:
            return match.groupdict()

    def urlize(self, **parameters):
        # merge required parameters default values if not present
        parameters.update(dict([(key, self._defaults[key]) for key in self._defaults if key in self._required and key not in parameters]))

        # check mapping
        if self._map and self._map != dict([(key, parameters[key]) for key in parameters if key in self._map]):
            return None

        # check required parameters
        if len([key for key in self._required if key in parameters]) < len(self._required):
            return None

        # format values
        for key in parameters:
            if type(parameters[key]) == list:
                if key in self._formats:
                    parameters[key] = [self._formats[key] % (part) for part in parameters[key]]

                parameters[key] = '/'.join(parameters[key])
            elif key in self._formats:
                parameters[key] = self._formats[key] % parameters[key]
            else:
                parameters[key] = str(parameters[key])

        # do some evil
        exec self._code

        return ''.join([result, build_query(**dict([(key, parameters[key]) for key in parameters if key not in self._parameters]))])

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
