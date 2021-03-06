# (c) This file is part of the course
# Mathematical Logic through Programming
# by Gonczarowski and Nisan.
# File name: predicates/syntax.py

"""Syntactic handling of first-order formulas and terms."""

from __future__ import annotations
from typing import AbstractSet, Mapping, Optional, Sequence, Set, Tuple, Union

from logic_utils import fresh_variable_name_generator, frozen

from propositions.syntax import Formula as PropositionalFormula, \
    is_variable as is_propositional_variable



class ForbiddenVariableError(Exception):
    """Raised by `Term.substitute` and `Formula.substitute` when a substituted
    term contains a variable name that is forbidden in that context."""

    def __init__(self, variable_name: str) -> None:
        """Initializes a `ForbiddenVariableError` from its offending variable
        name.

        Parameters:
            variable_name: variable name that is forbidden in the context in
                which a term containing it was to be substituted.
        """
        assert is_variable(variable_name)
        self.variable_name = variable_name


def is_constant(s: str) -> bool:
    """Checks if the given string is a constant name.

    Parameters:
        s: string to check.

    Returns:
        ``True`` if the given string is a constant name, ``False`` otherwise.
    """
    return (((s[0] >= '0' and s[0] <= '9') or (s[0] >= 'a' and s[0] <= 'd'))
            and s.isalnum()) or s == '_'


def is_variable(s: str) -> bool:
    """Checks if the given string is a variable name.

    Parameters:
        s: string to check.

    Returns:
        ``True`` if the given string is a variable name, ``False`` otherwise.
    """
    return s[0] >= 'u' and s[0] <= 'z' and s.isalnum()


def is_function(s: str) -> bool:
    """Checks if the given string is a function name.

    Parameters:
        s: string to check.

    Returns:
        ``True`` if the given string is a function name, ``False`` otherwise.
    """
    return s[0] >= 'f' and s[0] <= 't' and s.isalnum()


@frozen
class Term:
    """An immutable first-order term in tree representation, composed from
    variable names and constant names, and function names applied to them.

    Attributes:
        root (`str`): the constant name, variable name, or function name at the
            root of the term tree.
        arguments (`~typing.Optional`\\[`~typing.Tuple`\\[`Term`, ...]]): the
            arguments to the root, if the root is a function name.
    """
    root: str
    arguments: Optional[Tuple[Term, ...]]

    def __init__(self, root: str,
                 arguments: Optional[Sequence[Term]] = None) -> None:
        """Initializes a `Term` from its root and root arguments.

        Parameters:
            root: the root for the formula tree.
            arguments: the arguments to the root, if the root is a function
                name.
        """
        if is_constant(root) or is_variable(root):
            assert arguments is None
            self.root = root
        else:
            assert is_function(root)
            assert arguments is not None
            self.root = root
            self.arguments = tuple(arguments)
            assert len(self.arguments) > 0

    def __repr__(self) -> str:
        """Computes the string representation of the current term.

        Returns:
            The standard string representation of the current term.
        """
        # Task 7.1
        # recursively add the string

        # base case: root is a variable name, or constant
        ret_string = ""
        if is_variable(self.root) or is_constant(self.root):
            return self.root

        # case 2 root is a function
        if is_function(self.root):
            if self.arguments:
                arg_str = ""
                for i in range(len(self.arguments)):
                    if i < len(self.arguments) - 1:
                        arg_str += (self.arguments[i].__repr__() + ",")
                    else:
                        arg_str += self.arguments[i].__repr__()
                return self.root + '(' + arg_str + ')'
            else:
                return self.root + '(' + ')'

    def __eq__(self, other: object) -> bool:
        """Compares the current term with the given one.

        Parameters:
            other: object to compare to.

        Returns:
            ``True`` if the given object is a `Term` object that equals the
            current term, ``False`` otherwise.
        """
        return isinstance(other, Term) and str(self) == str(other)

    def __ne__(self, other: object) -> bool:
        """Compares the current term with the given one.

        Parameters:
            other: object to compare to.

        Returns:
            ``True`` if the given object is not a `Term` object or does not
            equal the current term, ``False`` otherwise.
        """
        return not self == other

    def __hash__(self) -> int:
        return hash(str(self))

    @staticmethod
    def parse_prefix(s: str) -> Tuple[Term, str]:
        """Parses a prefix of the given string into a term.

        Parameters:
            s: string to parse, which has a prefix that is a valid
                representation of a term.

        Returns:
            A pair of the parsed term and the unparsed suffix of the string. If
            the given string has as a prefix a constant name (e.g., ``'c12'``)
            or a variable name (e.g., ``'x12'``), then the parsed prefix will be
            that entire name (and not just a part of it, such as ``'x1'``).
        """
        # Task 7.3.1
        # Base Case 1: empty string
        if s == '':
            return Term(''), ''  # TODO check what they want

        cur_token = s[0]
        # Base Case 2: s is a variable
        if is_variable(cur_token):
            return get_variable(s)

        # Base Case 3: s is a constant
        if is_constant(cur_token):
            return get_constant(s)

        # Last case, the term is a function call:
        if is_function(cur_token):
            return get_function(s)








    @staticmethod
    def parse(s: str) -> Term:
        """Parses the given valid string representation into a term.

        Parameters:
            s: string to parse.

        Returns:
            A term whose standard string representation is the given string.
        """
        # Task 7.3.2
        return Term.parse_prefix(s)[0]

    def constants(self) -> Set[str]:
        """Finds all constant names in the current term.

        Returns:
            A set of all constant names used in the current term.
        """
        # Task 7.5.1
        const_set = set()
        if is_constant(self.root):
            const_set |= set([self.root])
            return const_set
        if is_variable(self.root):
            return const_set
        if is_function(self.root):
            for next_set in self.arguments:
                const_set |= next_set.constants()
            return const_set

    def variables(self) -> Set[str]:
        """Finds all variable names in the current term.

        Returns:
            A set of all variable names used in the current term.
        """
        # Task 7.5.2
        variable_set = set()
        if is_variable(self.root):
            variable_set.add(self.root)
            return variable_set
        if is_constant(self.root):
            return variable_set
        if is_function(self.root):
            for next_set in self.arguments:
                variable_set |= next_set.variables()
            return variable_set

    def functions(self) -> Set[Tuple[str, int]]:
        """Finds all function names in the current term, along with their
        arities.

        Returns:
            A set of pairs of function name and arity (number of arguments) for
            all function names used in the current term.
        """
        # Task 7.5.3
        func_set = set()
        if is_variable(self.root) or is_constant(self.root):
            return func_set
        if is_function(self.root):
            for term in self.arguments:
                if is_function(term.root):
                    func_set |= term.functions()
            func_set.add((self.root, len(self.arguments)))
        return func_set



    def substitute(self, substitution_map: Mapping[str, Term],
                   forbidden_variables: AbstractSet[str] = frozenset()) -> Term:
        """Substitutes in the current term, each constant name `name` or
        variable name `name` that is a key in `substitution_map` with the term
        `substitution_map[name]`.

        Parameters:
            substitution_map: mapping defining the substitutions to be
                performed.
            forbidden_variables: variables not allowed in substitution terms.

        Returns:
            The term resulting from performing all substitutions. Only
            constant names and variable names originating in the current term
            are substituted (i.e., those originating in one of the specified
            substitutions are not subjected to additional substitutions).

        Raises:
            ForbiddenVariableError: If a term that is used in the requested
                substitution contains a variable from `forbidden_variables`.

        Examples:
            >>> Term.parse('f(x,c)').substitute(
            ...     {'c': Term.parse('plus(d,x)'), 'x': Term.parse('c')}, {'y'})
            f(c,plus(d,x))
            >>> Term.parse('f(x,c)').substitute(
            ...     {'c': Term.parse('plus(d,y)')}, {'y'})
            Traceback (most recent call last):
              ...
            predicates.syntax.ForbiddenVariableError: y
        """
        for element_name in substitution_map:
            assert is_constant(element_name) or is_variable(element_name)
        for variable in forbidden_variables:
            assert is_variable(variable)
        # Task 9.1

        # recursively change all Term variables (all variables in terms are free variables)

        # base case 1 - term is constant:
        if is_constant(self.root) or is_variable(self.root):
            if self.root in substitution_map.keys():
                to_replace = substitution_map[self.root]
                if to_replace.root in forbidden_variables:
                    raise ForbiddenVariableError(to_replace.root)
                else: # we need to recursively check
                    forbidden_vars = set(to_replace.variables()).union(set(to_replace.constants())).intersection(forbidden_variables)
                    if bool(forbidden_vars):
                        raise ForbiddenVariableError(forbidden_vars.pop())
                    return to_replace
            return self

        # recursive case - Term is a function
        if is_function(self.root):
            new_args = []
            for term in self.arguments:
                new_args.append(term.substitute(substitution_map, forbidden_variables))
            return Term(self.root, new_args)




def get_variable(s: str) -> Tuple[Term, str]:
    """
    Helper function for parse, Checks a string and gets the variable from it
    :param s: current string
    :return: tuple of term of the string and the suffix of the rest without the variable
    """
    # check and see if there is a number after the variable name
    cur_token = s[0]
    i = 1
    cur_variable_num = ''
    while i < len(s):
        if s[i].isalnum():
            cur_variable_num += s[i]
            i += 1
        else:
            break

    # either adds the number to the token, or if it didnt exist, adds an empty string
    cur_token += cur_variable_num
    return Term(cur_token), s[len(cur_token):]

def get_constant(s: str) -> Tuple[Term, str]:
    """
    Helper function for parse prefix, checks a string and returns a constant from it
    :param s: the current string
    :return: return tuple of term of the constant, and the rest of the string
    """

    cur_token = s[0]
    i = 1
    cur_variable_suffix = ''
    if cur_token == '_':
        return Term(cur_token), s[len(cur_token):]
    if cur_token.isdigit() or 'a' <= cur_token <= 'd':
        while i < len(s):
            if s[i].isalnum():
                cur_variable_suffix += s[i]
                i += 1
            else:
                break
        cur_token += cur_variable_suffix
        return Term(cur_token), s[len(cur_token):]

def get_function(s: str) -> Tuple[Term, str]:
    """
    Helper function for parse, takes a string starting from a possible correct function name.
    if the function is correct it returns the entire term of the function, otherwise it returns
    an empty term and the suffix which is all of s
    :param s: the current string
    :return: the term and its' suffix
    """

    # cur_token = s[0]
    cur_suffix = ''
    function_name = s[0]
    arguments = []
    # cur_token was a valid start for a function name, so we'll create the function name
    i = 1
    while s[i].isalnum():
        function_name += s[i]
        i += 1
    if s[i] != '(':
        return Term(''), s  #TODO what to send instead of Term('')
    i += 1

    # After opening the parenthesis we expect n terms.
    while is_variable(s[i]) or is_function(s[i]) or is_constant(s[i]) or s[i] == ')':

        # variable case:
        if is_variable(s[i]):
            cur_term, cur_suffix = get_variable(s[i:])
            arguments.append(cur_term)
            i += len(cur_term.root) + 1 # we do +1 because of the ','
            if cur_suffix[0] == ',':
                continue
            elif cur_suffix[0] == ')':
                break
            else:
                return Term(''), s  #TODO Term('')

        # constant case:
        if is_constant(s[i]):
            cur_term, cur_suffix = get_constant(s[i:])
            arguments.append(cur_term)
            i += len(cur_term.root) + 1 # we do +1 because of the ','
            if cur_suffix[0] == ',':
                continue
            elif cur_suffix[0] == ')':
                break
            else:
                return Term(''), s  #TODO Term('')

        # function case:
        if is_function(s[i]):
            cur_term, cur_suffix = get_function(s[i:])
            arguments.append(cur_term)
            i += len(cur_term.__repr__()) + 1
            if cur_suffix[0] == ',':
                continue
            elif cur_suffix[0] == ')':
                break
            else:
                return Term(''), s

    cur_suffix = s[i:]
    return Term(function_name, arguments), cur_suffix


def is_equality(s: str) -> bool:
    """Checks if the given string is the equality relation.

    Parameters:
        s: string to check.

    Returns:
        ``True`` if the given string is the equality relation, ``False``
        otherwise.
    """
    return s == '='


def is_relation(s: str) -> bool:
    """Checks if the given string is a relation name.

    Parameters:
        s: string to check.

    Returns:
        ``True`` if the given string is a relation name, ``False`` otherwise.
    """
    return s[0] >= 'F' and s[0] <= 'T' and s.isalnum()


def is_unary(s: str) -> bool:
    """Checks if the given string is a unary operator.

    Parameters:
        s: string to check.

    Returns:
        ``True`` if the given string is a unary operator, ``False`` otherwise.
    """
    return s == '~'


def is_binary(s: str) -> bool:
    """Checks if the given string is a binary operator.

    Parameters:
        s: string to check.

    Returns:
        ``True`` if the given string is a binary operator, ``False`` otherwise.
    """
    return s == '&' or s == '|' or s == '->'


def is_quantifier(s: str) -> bool:
    """Checks if the given string is a quantifier.

    Parameters:
        s: string to check.

    Returns:
        ``True`` if the given string is a quantifier, ``False`` otherwise.
    """
    return s == 'A' or s == 'E'


@frozen
class Formula:
    """An immutable first-order formula in tree representation, composed from
    relation names applied to first-order terms, and operators and
    quantifications applied to them.

    Attributes:
        root (`str`): the relation name, equality relation, operator, or
            quantifier at the root of the formula tree.
        arguments (`~typing.Optional`\\[`~typing.Tuple`\\[`Term`, ...]]): the
            arguments to the root, if the root is a relation name or the
            equality relation.
        first (`~typing.Optional`\\[`Formula`]): the first operand to the root,
            if the root is a unary or binary operator.
        second (`~typing.Optional`\\[`Formula`]): the second
            operand to the root, if the root is a binary operator.
        variable (`~typing.Optional`\\[`str`]): the variable name quantified by
            the root, if the root is a quantification.
        predicate (`~typing.Optional`\\[`Formula`]): the predicate quantified by
            the root, if the root is a quantification.
    """
    root: str
    arguments: Optional[Tuple[Term, ...]]
    first: Optional[Formula]
    second: Optional[Formula]
    variable: Optional[str]
    predicate: Optional[Formula]

    def __init__(self, root: str,
                 arguments_or_first_or_variable: Union[Sequence[Term],
                                                       Formula, str],
                 second_or_predicate: Optional[Formula] = None) -> None:
        """Initializes a `Formula` from its root and root arguments, root
        operands, or root quantified variable and predicate.

        Parameters:
            root: the root for the formula tree.
            arguments_or_first_or_variable: the arguments to the the root, if
                the root is a relation name or the equality relation; the first
                operand to the root, if the root is a unary or binary operator;
                the variable name quantified by the root, if the root is a
                quantification.
            second_or_predicate: the second operand to the root, if the root is
                a binary operator; the predicate quantified by the root, if the
                root is a quantification.
        """
        if is_equality(root) or is_relation(root):
            # Populate self.root and self.arguments
            assert second_or_predicate is None
            assert isinstance(arguments_or_first_or_variable, Sequence) and \
                   not isinstance(arguments_or_first_or_variable, str)
            self.root, self.arguments = \
                root, tuple(arguments_or_first_or_variable)
            if is_equality(root):
                assert len(self.arguments) == 2
        elif is_unary(root):
            # Populate self.first
            assert isinstance(arguments_or_first_or_variable, Formula) and \
                   second_or_predicate is None
            self.root, self.first = root, arguments_or_first_or_variable
        elif is_binary(root):
            # Populate self.first and self.second
            assert isinstance(arguments_or_first_or_variable, Formula) and \
                   second_or_predicate is not None
            self.root, self.first, self.second = \
                root, arguments_or_first_or_variable, second_or_predicate
        else:
            assert is_quantifier(root)
            # Populate self.variable and self.predicate
            assert isinstance(arguments_or_first_or_variable, str) and \
                   is_variable(arguments_or_first_or_variable) and \
                   second_or_predicate is not None
            self.root, self.variable, self.predicate = \
                root, arguments_or_first_or_variable, second_or_predicate

    def __repr__(self) -> str:
        """Computes the string representation of the current formula.

        Returns:
            The standard string representation of the current formula.
        """
        # Task 7.2
        # we will print the string recursively:

        # Case 1, base case root is equality
        if is_equality(self.root):
            return self.arguments[0].__repr__() + '=' + self.arguments[1].__repr__()

        # Case 2 base case root is unary operator
        if is_unary(self.root):
            return self.root + self.first.__repr__()

        # Case 3 base case, root is a binary operator
        if is_binary(self.root):
            return '(' + self.first.__repr__() + self.root + self.second.__repr__() + ')'

        # Case 4 relation invocation
        if is_relation(self.root):
            if self.arguments:
                arg_str = ""
                for i in range(len(self.arguments)):
                    if i < len(self.arguments) - 1:
                        arg_str += (self.arguments[i].__repr__() + ",")
                    else:
                        arg_str += self.arguments[i].__repr__()
                        return self.root + '(' + arg_str + ')'
            else:
                return self.root + '(' + ')'

        # Case 5 quantification
        if is_quantifier(self.root):
            return self.root + self.variable + '[' + self.predicate.__repr__() + ']'



    def __eq__(self, other: object) -> bool:
        """Compares the current formula with the given one.

        Parameters:
            other: object to compare to.

        Returns:
            ``True`` if the given object is a `Formula` object that equals the
            current formula, ``False`` otherwise.
        """
        return isinstance(other, Formula) and str(self) == str(other)

    def __ne__(self, other: object) -> bool:
        """Compares the current formula with the given one.

        Parameters:
            other: object to compare to.

        Returns:
            ``True`` if the given object is not a `Formula` object or does not
            equal the current formula, ``False`` otherwise.
        """
        return not self == other

    def __hash__(self) -> int:
        return hash(str(self))

    @staticmethod
    def parse_prefix(s: str) -> Tuple[Formula, str]:
        """Parses a prefix of the given string into a formula.

        Parameters:
            s: string to parse, which has a prefix that is a valid
                representation of a formula.

        Returns:
            A pair of the parsed formula and the unparsed suffix of the string.
            If the given string has as a prefix a term followed by an equality
            followed by a constant name (e.g., ``'c12'``) or by a variable name
            (e.g., ``'x12'``), then the parsed prefix will include that entire
            name (and not just a part of it, such as ``'x1'``).
        """
        # Task 7.4.1
        cur_token = s[0]
        # cur_token is unary
        if is_unary(cur_token):
            cur_term, cur_suffix = Formula.parse_prefix(s[1:])
            return Formula('~', cur_term), cur_suffix

        # cur_token is binary
        if cur_token == '(':
            first_formula, cur_suffix = Formula.parse_prefix(s[1:])
            cur_operator = ''
            # cur_formula returns the first formula, suffix must be the binary operator
            if cur_suffix[0] == '&' or cur_suffix[0] == '|':
                cur_operator = cur_suffix[0]
                second_formula, cur_suffix = Formula.parse_prefix(cur_suffix[1:])
            else:  # operator is ->
                cur_operator = cur_suffix[:2]
                second_formula, cur_suffix = Formula.parse_prefix(cur_suffix[2:])
            binary_formula = Formula(cur_operator, first_formula, second_formula)
            return binary_formula, cur_suffix[1:]  # from the 1st spot because we need to skip the ')'

        # cur_token is the start of an equality
        if is_constant(cur_token) or is_function(cur_token) or is_variable(cur_token):
            first_term, cur_suffix = Term.parse_prefix(s)
            if cur_suffix[0] == '=':
                second_term, cur_suffix = Term.parse_prefix(cur_suffix[1:])
                equality_formula = Formula('=', [first_term, second_term])
                return equality_formula, cur_suffix

        # cur token is the start of a relation
        if is_relation(cur_token):
            arguments = []
            relation_name = cur_token
            i = 1
            while s[i].isalnum():
                relation_name += s[i]
                i += 1
            if s[i] == '(':
                i += 1
                if s[i] == ')':
                    return Formula(relation_name, arguments), s[i+1:]
                while(is_variable(s[i]) or is_function(s[i]) or is_constant(s[i])):
                    cur_term, cur_suffix = Term.parse_prefix(s[i:])
                    arguments.append(cur_term)
                    i += len(str(cur_term)) + 1
                    if cur_suffix[0] == ',':
                        continue
                    if cur_suffix[0] == ')':
                        break
                    # We can assume the +1 is either for a '(' or a ','
                return Formula(relation_name, arguments), s[i:]

        # cur_token is the start of a quantification
        if is_quantifier(cur_token):
            quantifier = cur_token
            if is_variable(s[1]):
                cur_variable, cur_suffix = Term.parse_prefix(s[1:])
                if cur_suffix[0] == '[':
                    cur_formula, cur_suffix = Formula.parse_prefix(cur_suffix[1:])
                    return Formula(quantifier, cur_variable.root, cur_formula), cur_suffix[1:]  # from the 1st place to ignore ']'








    @staticmethod
    def parse(s: str) -> Formula:
        """Parses the given valid string representation into a formula.

        Parameters:
            s: string to parse.

        Returns:
            A formula whose standard string representation is the given string.
        """
        # Task 7.4.2
        return Formula.parse_prefix(s)[0]

    def constants(self) -> Set[str]:
        """Finds all constant names in the current formula.

        Returns:
            A set of all constant names used in the current formula.
        """
        # Task 7.6.1
        ret_set = set()

        # case where root is equality
        if is_equality(self.root):
            first_terms = self.arguments[0].constants()
            second_terms = self.arguments[1].constants()
            ret_set |= first_terms
            ret_set |= second_terms
            return ret_set

        # case where root is unary
        if is_unary(self.root):
            ret_set |= self.first.constants()
            return ret_set

        # Case where root is binary
        if is_binary(self.root):
            first_set = self.first.constants()
            second_set = self.second.constants()
            ret_set |= first_set
            ret_set |= second_set
            return ret_set

        # Case Quantification
        if is_quantifier(self.root):
            ret_set |= self.predicate.constants()
            return ret_set

        # Case of n Array case
        if is_relation(self.root):
            for term in self.arguments:
                ret_set |= (term.constants())
            return ret_set


    def variables(self) -> Set[str]:
        """Finds all variable names in the current formula.

        Returns:
            A set of all variable names used in the current formula.
        """
        # Task 7.6.2
        ret_set = set()

        # case where root is equality
        if is_equality(self.root):
            first_terms = self.arguments[0].variables()
            second_terms = self.arguments[1].variables()
            ret_set = ret_set.union(first_terms)
            ret_set = ret_set.union(second_terms)
            return ret_set

        # case where root is unary
        if is_unary(self.root):
            ret_set = ret_set.union(self.first.variables())
            return ret_set

        # Case where root is binary
        if is_binary(self.root):
            first_set = self.first.variables()
            second_set = self.second.variables()
            ret_set = ret_set.union(first_set)
            ret_set = ret_set.union(second_set)
            return ret_set

        # Case Quantification
        if is_quantifier(self.root):
            ret_set = ret_set.union(self.predicate.variables())
            return ret_set.union(self.variable)

        # Case of n Array case
        if is_relation(self.root):
            for term in self.arguments:
              ret_set = ret_set.union(term.variables())
            return ret_set



    def free_variables(self) -> Set[str]:
        """Finds all variable names that are free in the current formula.

        Returns:
            A set of all variable names used in the current formula not only
            within a scope of a quantification on those variable names.
        """
        # Task 7.6.3
        free_var_set = set()

        if is_equality(self.root):
            first_terms = self.arguments[0].variables()
            second_terms = self.arguments[1].variables()
            free_var_set = free_var_set.union(first_terms, second_terms)
            return free_var_set

        # case where root is unary
        if is_unary(self.root):
            free_var_set |= self.first.free_variables()
            return free_var_set

        # Case where root is binary
        if is_binary(self.root):
            first_set = self.first.free_variables()
            second_set = self.second.free_variables()
            free_var_set |= first_set
            free_var_set |= second_set
            return free_var_set

        # Case Quantification
        if is_quantifier(self.root):
            temp_var_set = self.predicate.free_variables()
            if self.variable in temp_var_set:
                temp_var_set.discard(self.variable)
            free_var_set = free_var_set.union(temp_var_set)
            return free_var_set

        if is_relation(self.root):
            for term in self.arguments:
                free_var_set |= term.variables()
            return free_var_set








    def functions(self) -> Set[Tuple[str, int]]:
        """Finds all function names in the current formula, along with their
        arities.

        Returns:
            A set of pairs of function name and arity (number of arguments) for
            all function names used in the current formula.
        """
        # Task 7.6.4
        func_set = set()

        if is_equality(self.root):
            first_terms = self.arguments[0].functions()
            second_terms = self.arguments[1].functions()
            func_set = func_set.union(first_terms, second_terms)
            return func_set

        # case where root is unary
        if is_unary(self.root):
            func_set |= self.first.functions()
            return func_set

        # Case where root is binary
        if is_binary(self.root):
            first_set = self.first.functions()
            second_set = self.second.functions()
            func_set |= first_set
            func_set |= second_set
            return func_set

        # Case Quantification
        if is_quantifier(self.root):
            func_set |= self.predicate.functions()
            return func_set

        if is_relation(self.root):
            for term in self.arguments:
                func_set |= term.functions()
            return func_set
        

    def relations(self) -> Set[Tuple[str, int]]:
        """Finds all relation names in the current formula, along with their
        arities.

        Returns:
            A set of pairs of relation name and arity (number of arguments) for
            all relation names used in the current formula.
        """
        # Task 7.6.5
        relation_set = set()

        if is_equality(self.root):
            return set()

        # case where root is unary
        if is_unary(self.root):
            relation_set |= self.first.relations()
            return relation_set

        # Case where root is binary
        if is_binary(self.root):
            first_set = self.first.relations()
            second_set = self.second.relations()
            relation_set |= first_set
            relation_set |= second_set
            return relation_set

        # Case Quantification
        if is_quantifier(self.root):
            relation_set |= self.predicate.relations()
            return relation_set

        if is_relation(self.root):
            relation_name = self.root
            tup = relation_name, len(self.arguments)
            temp_set = set([tup])
            relation_set |= temp_set
            return relation_set


    def substitute(self, substitution_map: Mapping[str, Term],
                   forbidden_variables: AbstractSet[str] = frozenset()) -> \
            Formula:
        """Substitutes in the current formula, each constant name `name` or free
        occurrence of variable name `name` that is a key in `substitution_map`
        with the term `substitution_map[name]`.

        Parameters:
            substitution_map: mapping defining the substitutions to be
                performed.
            forbidden_variables: variables not allowed in substitution terms.

        Returns:
            The formula resulting from performing all substitutions. Only
            constant names and variable names originating in the current formula
            are substituted (i.e., those originating in one of the specified
            substitutions are not subjected to additional substitutions).

        Raises:
            ForbiddenVariableError: If a term that is used in the requested
                substitution contains a variable from `forbidden_variables`
                or a variable occurrence that becomes bound when that term is
                substituted into the current formula.

        Examples:
            >>> Formula.parse('Ay[x=c]').substitute(
            ...     {'c': Term.parse('plus(d,x)'), 'x': Term.parse('c')}, {'z'})
            Ay[c=plus(d,x)]
            >>> Formula.parse('Ay[x=c]').substitute(
            ...     {'c': Term.parse('plus(d,z)')}, {'z'})
            Traceback (most recent call last):
              ...
            predicates.syntax.ForbiddenVariableError: z
            >>> Formula.parse('Ay[x=c]').substitute(
            ...     {'c': Term.parse('plus(d,y)')})
            Traceback (most recent call last):
              ...
            predicates.syntax.ForbiddenVariableError: y
        """
        for element_name in substitution_map:
            assert is_constant(element_name) or is_variable(element_name)
        for variable in forbidden_variables:
            assert is_variable(variable)
        # Task 9.2
        # case1 formula is equality
        if is_equality(self.root):
            var1= self.arguments[0].substitute(substitution_map,forbidden_variables)
            var2 =self.arguments[1].substitute(substitution_map,forbidden_variables)
            return Formula("=", [var1,var2])
        # case2 formula is relation
        if is_relation(self.root):
            new_term_array = [term.substitute(substitution_map, forbidden_variables) for term in self.arguments]
            return Formula(self.root,new_term_array)
        if is_unary(self.root):
            return Formula(self.root,self.first.substitute(substitution_map, forbidden_variables))
        if is_binary(self.root):
            return Formula(self.root,self.first.substitute(substitution_map, forbidden_variables), self.second.substitute(substitution_map, forbidden_variables))
        if is_quantifier(self.root):
            # if self.variable in substitution_map.keys():
            #     return Formula(self.root, substitution_map[self.variable].root, self.predicate.substitute(substitution_map, forbidden_variables)).substitute(substitution_map, forbidden_variables)
            forbidden_variables_copy = forbidden_variables.union(set(self.variable))
            sub_map_copy = {k:v for k,v in substitution_map.items()}
            sub_map_copy.pop(str(self.variable), None)
            return Formula(self.root, self.variable, self.predicate.substitute(sub_map_copy, forbidden_variables_copy))






    def propositional_skeleton(self) -> Tuple[PropositionalFormula,
                                              Mapping[str, Formula]]:
        """Computes a propositional skeleton of the current formula.

        Returns:
            A pair. The first element of the pair is a propositional formula
            obtained from the current formula by substituting every (outermost)
            subformula that has a relation or quantifier at its root with an
            atomic propositional formula, consistently such that multiple equal
            such (outermost) subformulas are substituted with the same atomic
            propositional formula. The atomic propositional formulas used for
            substitution are obtained, from left to right, by calling
            `next`\ ``(``\ `~logic_utils.fresh_variable_name_generator`\ ``)``.
            The second element of the pair is a map from each atomic
            propositional formula to the subformula for which it was
            substituted.
        """
        # Task 9.8

        # recursively go down the formula, update a mapping as we go.
        def recursive_skeleton_helper(formula : PropositionalFormula, formula_map : Mapping[str, Formula]):

            # base case: formula is a relation equality or quantifier:
            if is_relation(formula.root) or is_quantifier(formula.root) or is_equality(formula.root):
                # check if the value is in the map
                for key, val in formula_map.items():
                    if str(val) == str(formula):
                        return PropositionalFormula(key), formula_map
                else:
                    new_term = Term(next(fresh_variable_name_generator))
                    formula_map[str(new_term)] = formula
                    return PropositionalFormula(new_term.root), formula_map

            # unary recursive call
            if is_unary(formula.root):
                first_child_term, formula_map_first = recursive_skeleton_helper(formula.first, formula_map)
                return PropositionalFormula(formula.root, first_child_term), formula_map_first

            # binary recursive call
            if is_binary(formula.root):
                first_child_term, formula_map_first = recursive_skeleton_helper(formula.first, formula_map)
                second_child_term, formula_map_second = recursive_skeleton_helper(formula.second, formula_map_first)
                merged_map = formula_map_second
                return PropositionalFormula(formula.root, first_child_term, second_child_term), merged_map


        return recursive_skeleton_helper(self, {})

    @staticmethod
    def from_propositional_skeleton(skeleton: PropositionalFormula,
                                    substitution_map: Mapping[str, Formula]) -> \
            Formula:
        """Computes a first-order formula from a propositional skeleton and a
        substitution map.

        Arguments:
            skeleton: propositional skeleton for the formula to compute.
            substitution_map: a map from each atomic propositional subformula
                of the given skeleton to a first-order formula.

        Returns:
            A first-order formula obtained from the given propositional skeleton
            by substituting each atomic propositional subformula with the formula
            mapped to it by the given map.
        """
        for key in substitution_map:
            assert is_propositional_variable(key)
        # Task 9.10
        # recursively go down the formula and return the predicate formula

        # base case, we reach a term
        if is_propositional_variable(skeleton.root):
            if skeleton.root in substitution_map.keys():
                return substitution_map[skeleton.root]

        # recursive unary case
        if is_unary(skeleton.root):
            return Formula(skeleton.root, Formula.from_propositional_skeleton(skeleton.first, substitution_map))

        # recursive binary case
        if is_binary(skeleton.root):
            return Formula(skeleton.root, Formula.from_propositional_skeleton(skeleton.first, substitution_map),
                           Formula.from_propositional_skeleton(skeleton.second, substitution_map))
