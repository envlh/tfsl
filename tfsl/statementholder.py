""" Holds the StatementHolder class and a function to build one given a JSON representation of it. """

from collections import defaultdict
from copy import deepcopy
from textwrap import indent
from typing import Optional

import tfsl.interfaces as I
import tfsl.statement
import tfsl.utils as U

class StatementHolder(object):
    """ Holds a set of statements. """
    def __init__(self, statements: Optional[I.StatementHolderInput]=None):
        super().__init__()

        self.statements = defaultdict(list)
        if isinstance(statements, defaultdict):
            for prop in statements:
                for arg in statements[prop]:
                    self.statements[arg.property].append(arg)
        elif isinstance(statements, list):
            for arg in statements:
                self.statements[arg.property].append(arg)

    def get_statements(self, property_in: I.Pid) -> I.StatementList:
        """ Returns a list of statements with the provided property. """
        return self.statements.get(property_in, [])

    def haswbstatement(self, property_in: I.Pid, value_in: Optional[I.ClaimValue]=None) -> bool:
        """Shamelessly named after the keyword used on Wikidata to look for a statement."""
        if value_in is None:
            return property_in in self.statements
        elif U.is_novalue(value_in):
            def compare_function(stmt: tfsl.Statement) -> bool:
                return U.is_novalue(stmt.value)
        elif U.is_somevalue(value_in):
            def compare_function(stmt: tfsl.Statement) -> bool:
                return U.is_somevalue(stmt.value)
        else:
            def compare_function(stmt: tfsl.statement.Statement) -> bool:
                return stmt.value == value_in
        return any(map(compare_function, self.statements[property_in]))

    def __jsonout__(self) -> I.StatementDictSet:
        statement_dict = defaultdict(list)
        for stmtprop, stmtval in self.statements.items():
            statement_dict[stmtprop].extend([stmt.__jsonout__() for stmt in stmtval])
        return dict(statement_dict)

    def __len__(self) -> int:
        return len(self.statements)

    def __eq__(self, rhs: object) -> bool:
        if isinstance(rhs, StatementHolder):
            return self.statements == rhs.statements
        elif isinstance(rhs, dict):
            return self.statements == rhs
        return NotImplemented

    def __contains__(self, arg: object) -> bool:
        if isinstance(arg, str):
            if I.is_Pid(arg):
                return arg in self.statements
            raise TypeError(f"String {arg} is not a property")
        elif isinstance(arg, tfsl.claim.Claim):
            for prop in self.statements:
                for stmt in self.statements[prop]:
                    if stmt == arg:
                        return True
        elif isinstance(arg, tfsl.statement.Statement):
            return arg in self.statements[arg.property]
        raise TypeError(f"Can't check for {type(arg)} in StatementHolder")

    def __getitem__(self, arg: object) -> I.StatementList:
        if isinstance(arg, str):
            if I.is_Pid(arg):
                return self.statements[arg]
        raise KeyError(f"String {arg} is not a property")

    def __str__(self) -> str:
        if self.statements:
            stmt_list = [str(stmt) for prop in self.statements for stmt in self.statements[prop]]
            return "<\n"+indent("\n".join(stmt_list), tfsl.utils.DEFAULT_INDENT)+"\n>"
        return ""

    def __add__(self, rhs: object) -> 'StatementHolder':
        if not isinstance(rhs, tfsl.statement.Statement):
            raise TypeError(f"Can't add {type(rhs)} to StatementHolder")
        newstmts = deepcopy(self.statements)
        newstmts[rhs.property].append(rhs)
        return StatementHolder(newstmts)

    def __sub__(self, rhs: object) -> 'StatementHolder':
        if isinstance(rhs, str):
            if I.is_Pid(rhs):
                newstmts = deepcopy(self.statements)
                if rhs in newstmts:
                    del newstmts[rhs]
                return StatementHolder(newstmts)
            raise TypeError(f"String {rhs} is not a property")
        elif isinstance(rhs, tfsl.statement.Statement):
            newstmts = deepcopy(self.statements)
            newstmts[rhs.property] = [stmt for stmt in newstmts[rhs.property] if stmt != rhs]
            if not newstmts[rhs.property]:
                del newstmts[rhs.property]
            return StatementHolder(newstmts)
        raise TypeError(f"Can't subtract {type(rhs)} from StatementHolder")

def build_statement_list(claims_dict: I.StatementDictSet) -> I.StatementSet:
    """ Builds a statement set from a JSON dictionary of statements. """
    claims: I.StatementSet = defaultdict(list)
    for prop in claims_dict:
        for claim in claims_dict[prop]:
            claims[prop].append(tfsl.statement.build_statement(claim))
    return claims
