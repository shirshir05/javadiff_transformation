import operator
import javalang
from collections import Counter
try:
    from .commented_code_detector import Halstead
except:
    from commented_code_detector import Halstead

def get_decles_names():
    def all_subclasses(cls):
        return set(cls.__subclasses__()).union(
            [s for c in cls.__subclasses__() for s in all_subclasses(c)])

    return list(map(lambda c: c.__name__, all_subclasses(javalang.ast.Node)))


class SourceLine(object):
    DECALS_LIST = get_decles_names()

    def __init__(self, line, halstead_line, line_number, is_changed, ordinal, decls, tokens, indent_level):
        self.line = line.strip()
        self.halstead_line = halstead_line
        self.halstead = self.halstead_line.getValuesVector()
        self.line_number = line_number
        self.is_changed = is_changed
        self.ordinal = ordinal
        self.decls = decls
        self.decls_count = sum(self.decls.values())
        self.tokens = tokens
        self.indent_level = indent_level

    def __repr__(self):
        start = "  "
        if self.is_changed:
            start = "* "
        return "{0}{1}: {2}".format(start, str(self.line_number), self.line)

    @staticmethod
    def get_source_lines(start_line, end_line, contents, halstead_lines, changed_indices, method_used_lines, parsed_body, tokens):
        source_lines = []
        used_lines = []
        for line_number in range(start_line - 1, end_line):
            if line_number not in method_used_lines:
                continue
            used_lines.append(line_number)
        decls, indent_level = SourceLine.get_decls_by_lines(parsed_body, list(map(lambda x: x + 1, used_lines)))
        tokens_types = SourceLine.get_tokens_by_lines(tokens, list(map(lambda x: x + 1, used_lines)))
        for line_number in used_lines:
            line = contents[line_number]
            halstead_line = halstead_lines[line_number]
            is_changed = line_number in changed_indices
            source_lines.append(SourceLine(line, halstead_line, line_number, is_changed, line_number-start_line, decls[line_number + 1], tokens_types[line_number + 1], indent_level[line_number + 1]))
        return source_lines


    @staticmethod
    def get_decles_empty_dict():
        return dict.fromkeys(SourceLine.DECALS_LIST, 0)

    @staticmethod
    def get_decls_by_lines(parsed_body, lines):
        def helper(x):
            return x.position and x.position.line in lines
        def getter(x):
            return x[1]
        base_column = parsed_body[0].position.column
        cols = set([base_column])
        ans = {}
        indentetions = {}
        indent_level = {}
        for l in lines:
            ans[l] = []
            indentetions[l] = []
        for e in parsed_body:
            for path, x in e.filter(javalang.ast.Node):
                # for x in list(filter(helper, map(getter, e2.filter()))):
                position = x.position
                if position is None:
                    position = list(filter(helper, map(getter, x.filter(javalang.ast.Node))))
                    if position:
                        position = position[0].position
                    else:
                        continue
                cols.add(position.column)
                indentetions.setdefault(position.line, []).append(position.column)
                ans.setdefault(position.line, []).append(x)
        levels = dict(map(reversed, enumerate(sorted(cols))))
        for line in indentetions:
            if indentetions[line]:
                indent_level[line] = min(list(map(levels.get, indentetions[line])))
            else:
                indent_level[line] = 0
        decls = {}
        for l in ans:
            decls[l] = SourceLine.get_decles_empty_dict()
            for k, v in dict(Counter(map(lambda x: type(x).__name__, ans[l]))).items():
                decls[l][k] = v
        return decls, indent_level

    @staticmethod
    def get_tokens_by_lines(tokens, lines):
        return dict(map(lambda l: (l, {}), lines))
        def get_name(t):
            if type(t).__name__ not in ['String', 'Identifier', 'DecimalFloatingPoint', 'DecimalInteger', 'HexInteger', 'OctalInteger' ]:
                # return type(t).__name__
                return "{0}_{1}".format(type(t).__name__, t.value)
            else:
                # return "{0}_{1}".format(type(t).__name__, t.value)
                return type(t).__name__
        ans = {}
        for l in lines:
            ans[l] = []
        for t in tokens:
            if t.position.line in lines:
                    ans[t.position.line].append(get_name(t))
        res = {}
        for l in ans:
            res[l] = dict(Counter(ans[l]))
        return res


class MethodData(object):
    def __init__(self, method_name, start_line, end_line, contents, halstead_lines, changed_indices, method_used_lines, parameters, file_name, method_decl, tokens, analyze_source_lines=True, lizard_method=None):
        self.method_name = method_name
        self.start_line = int(start_line)
        self.end_line = int(end_line)
        self.implementation = contents[self.start_line - 1: self.end_line]
        self.method_used_lines = method_used_lines
        self.parameters = parameters
        self.file_name = file_name
        self.method_decl = method_decl
        self.return_type = None
        if hasattr(self.method_decl, 'return_type'):
            self.return_type = getattr(self.method_decl, 'return_type')
        self.method_name_parameters = self.method_name + "(" + ",".join(self.parameters) + ")"
        self.id = self.file_name + "@" + self.method_name_parameters
        self.source_lines = None
        self.changed = self._is_changed(changed_indices)
        self.lizard_method = lizard_method
        self.lizard_values = {}
        if lizard_method:
            for att in ['cyclomatic_complexity', 'nloc', 'token_count', 'name', 'long_name', 'start_line', 'end_line', 'full_parameters', 'filename', 'top_nesting_level', 'length', 'fan_in', 'fan_out', 'general_fan_out']:
                setattr(self, 'lizard_'+att, getattr(self.lizard_method, att))
            for att in ['cyclomatic_complexity', 'nloc', 'token_count', 'top_nesting_level', 'length', 'fan_in', 'fan_out', 'general_fan_out']:
                self.lizard_values[att] = getattr(self.lizard_method, att)
        if analyze_source_lines:
            self.source_lines = SourceLine.get_source_lines(start_line, end_line, contents, halstead_lines, changed_indices, method_used_lines, method_decl.body, tokens)
            self.used_lines = list(map(lambda s: s.line_number, self.source_lines))
            self.used_changed_lines = list(map(lambda s: s.line_number, filter(lambda s: s.is_changed, self.source_lines)))
            self.halstead = Halstead(list(map(lambda x: x.halstead_line, self.source_lines))).getValuesVector()
            self.decls = SourceLine.get_decles_empty_dict()
            for k in self.decls:
                self.decls[k] = sum(list(map(lambda s: s.decls[k], self.source_lines)))
            self.decls_count = sum(self.decls.values())

    def _is_changed(self, indices=None):
        if self.source_lines:
            return any(filter(lambda line: line.is_changed, self.source_lines))
        # return any(filter(lambda ind: ind >= self.start_line and ind <= self.end_line, indices))
        return len(set(self.method_used_lines).intersection(set(indices))) > 0

    def __eq__(self, other):
        assert isinstance(other, type(self))
        return self.method_name == other.method_name and self.parameters == other.parameters

    def __repr__(self):
        return self.id

    def get_changed_lines(self):
        return filter(lambda line: line.is_changed, self.source_lines)