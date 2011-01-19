# encoding: utf-8
# vim: ts=4 noexpandtab

from re import sub as rsub, match as rmatch, search as rsearch, findall as rfind
from pyparsing import nestedExpr
from utils import singleton

@singleton
class Mapper:
    args = ['controller', 'action', 'id', 'lang']
    names = []
    routes = []

    def connect(self, route, map=None, **args):
        route = Route(route, map, **args)
        self.names.append(route.name)
        self.routes.append(route)

class Route:
    name = None
    route = None
    map = None
    regex = None
    code = None
    defaults = {}
    constraints = {}
    formats = {}
    limits = {}
    parameters = []
    required = []
    multiple = []


    def __init__(self, route, map=None, **args):
        self.route = route

        # map ourself out
        if map is not None:
            if type(map) == dict:
                self.map = map
            elif type(map) == str:
                self.map = dict(zip(Mapper().args[:map.count('#') + 1], map.split('#')))
            else:
                raise TypeError('map should be either dict or str')
        else:
            self.map = {}

        # set/generate name
        if 'name' in args:
            self.name = name
        elif self.map:
            self.name = '_'.join(self.map.keys())
        else:
            self.name = id(self)

        # set common options
        if 'defaults' in args:
            self.defaults = args['defaults']
        if 'constraints' in args:
            self.constraints = args['constraints']
        if 'formats' in args:
            self.formats = args['formats']
        if 'limits' in args:
            self.limits = args['limits']

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

                self.parameters.append(name)

                if not paren:
                    self.required.append(name)

                if c == '*':
                    self.multiple.append(name)

        # set defaults for action and format
        if 'action' in self.parameters and not 'action' in self.defaults:
            self.defaults['action'] = 'index'
        if 'format' in self.parameters and not 'format' in self.defaults:
            self.defaults['format'] = 'html'

        # build the regular expression with a regular expression (and a couple of string substitutions, though)
        self.regex = rsub('[:*](\\w+)', self._constraintize, route.replace('(', '(?:').replace(')', ')?').replace('.', '\\.'))

        expr = nestedExpr('(', ')')
        parsed = expr.parseString('(' + route + ')')[0]
        self.code = 'return ' + self._conditionalize(parsed)
        print self.code

    def _conditionalize(self, args):
        part = args[0]

        next = []
        segments = args[1:]
        for segment in segments:
            print segment
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

    def _constraintize(self, match):
        name = match.group(1)

        if name in self.multiple:
            if name in self.constraints:
                constraint = self.constraints[name]
            else:
                constraint = '[^/]+'

            if name in self.limits:
                limit = ''.join(['{', self.limits[name], '}'])
            else:
                limit = '+'

            return ''.join(['(?P<', name, '>(?:', constraint, '/?)', limit, ')'])

        if name in self.constraints:
            constraint = self.constraints[name]
        else:
            constraint = '[^/.]+'

        return ''.join(['(?P<', name, '>', constraint, ')'])
