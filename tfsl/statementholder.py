from collections import defaultdict
from copy import deepcopy
from functools import singledispatchmethod
from textwrap import indent

import tfsl.statement

class StatementHolder(object):
    def __init__(self, statements=None):
        super().__init__()

        if statements is None:
            self.statements = defaultdict(list)
        elif isinstance(statements, list):
            self.statements = defaultdict(list)
            for arg in statements:
                self.statements[arg.property].append(arg)
        else:
            self.statements = deepcopy(statements)

    def get_statements(self, property_in):
        return self.statements.get(property_in, [])

    def has_property_value_pair(self, property_in, value):
        return any(statement.value == value for statement in self.statements[property_in])

    def __jsonout__(self):
        statement_dict = defaultdict(list)
        for stmtprop, stmtval in self.statements.items():
            statement_dict[stmtprop].extend([stmt.__jsonout__() for stmt in stmtval])
        return dict(statement_dict)

    def __len__(self):
        return len(self.statements)

    def __eq__(self, rhs):
        return self.eq(rhs)

    @singledispatchmethod
    def eq(self, rhs):
        return self.statements == rhs.statements

    @eq.register
    def _(self, rhs: dict):
        return self.statements == rhs

    def __contains__(self, arg):
        return self.contains(arg)

    @singledispatchmethod
    def contains(self, arg):
        raise TypeError(f"Can't check for {type(arg)} in StatementHolder")

    @contains.register
    def _(self, arg: str):
        if tfsl.utils.matches_property(arg):
            return arg in self.statements
        raise TypeError(f"String {arg} is not a property")

    @contains.register
    def _(self, arg: tfsl.claim.Claim):
        return any((arg in self.statements[prop]) for prop in self.statements)

    @contains.register
    def _(self, arg: tfsl.statement.Statement):
        return arg in self.statements[arg.property]

    def __getitem__(self, arg):
        return self.get_st(arg)

    @singledispatchmethod
    def get_st(self, arg):
        raise TypeError(f"Can't get {type(arg)} from StatementHolder")

    @get_st.register
    def _(self, arg: str):
        if tfsl.utils.matches_property(arg):
            return self.statements.get(arg, [])
        raise KeyError(f"String {arg} is not a property")

    def __str__(self):
        if self.statements:
            stmt_list = [str(stmt) for prop in self.statements for stmt in self.statements[prop]]
            return "<\n"+indent("\n".join(stmt_list), tfsl.utils.DEFAULT_INDENT)+"\n>"
        return ""

    def __add__(self, rhs):
        return self.add(rhs)

    @singledispatchmethod
    def add(self, rhs):
        raise TypeError(f"Can't add {type(rhs)} to StatementHolder")

    @add.register
    def _(self, rhs: tfsl.statement.Statement):
        newstmts = deepcopy(self.statements)
        newstmts[rhs.property].append(rhs)
        return newstmts

    def __sub__(self, rhs):
        return self.sub(rhs)

    @singledispatchmethod
    def sub(self, rhs):
        raise TypeError(f"Can't subtract {type(rhs)} from StatementHolder")

    @sub.register
    def _(self, rhs: str):
        newstmts = deepcopy(self.statements)
        if rhs in newstmts:
            del newstmts[rhs]
        return newstmts

    @sub.register
    def _(self, rhs: tfsl.statement.Statement):
        newstmts = deepcopy(self.statements)
        newstmts[rhs.property] = [stmt for stmt in newstmts[rhs.property] if stmt != rhs]
        if not newstmts[rhs.property]:
            del newstmts[rhs.property]
        return newstmts

def build_statement_list(claims_dict):
    claims = defaultdict(list)
    for prop in claims_dict:
        for claim in claims_dict[prop]:
            claims[prop].append(tfsl.statement.build_statement(claim))
    return claims
