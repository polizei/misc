# encoding: utf-8
# vim: ts=4 noexpandtab

from re import sub as rsub, match as rmatch, search as rsearch, findall as rfind
from pyparsing import nestedExpr
from utils import singleton

@singleton
class Mapper:
    _args = ['controller', 'action', 'id', 'lang']
    _names = []
    _routes = []

    def connect(self, route, map=None, **args):
        route = Route(route, map, **args)
        self._names.append(route.name())
        self._routes.append(route)

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

        expr = nestedExpr('(', ')')
        parsed = expr.parseString('(' + route + ')')[0]
        self._code = 'return ' + self._conditionalize(parsed)

    def name(self):
        return self._name

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
        next = ' + '.join(next)
        if next:
            next = ' + ' + next;

        conditions = []
        for name in rfind('[:*](\\w+)', part):
            conditions.append('"' + name + '" in parameters')
        if conditions:
            conditions = ' and '.join(conditions)
        else:
            conditions = 'true'

        return '((' + conditions + ') and ("' + rsub('[:*](\\w+)', '" + parameters["\\1"] + "', part) + '"' + next + ') or "")'

    def urlize(self, **args):
        exec self._code
