from collections import defaultdict
from copy import deepcopy

import tfsl.statement

class StatementHolder:
    def __init__(self, statements=None, **others):
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

    def build_statement_dict(self):
        statement_dict = defaultdict(list)
        for stmtprop, stmtval in self.statements.items():
            statement_dict[stmtprop].extend([stmt.__jsonout__() for stmt in stmtval])
        return dict(statement_dict)

    def __eq__(self, rhs):
        return self.statements == rhs.statements

def build_statement_list(claims_dict):
    claims = defaultdict(list)
    for prop in claims_dict:
        for claim in claims_dict[prop]:
            claims[prop].append(tfsl.statement.build_statement(claim))
    return claims
