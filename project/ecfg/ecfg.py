from pyformlang.cfg import CFG
from pyformlang.regular_expression import Regex


class ECFG:
    """A class representing an extended context free grammar --
    a context free grammar with fixed format:

    1. There is exactly one rule for each non-terminal.
    2. One line contains exactly one rule.
    3. A rule is a non-terminal and a regular expression over terminals and non-terminals
        accepted by pyformalng, separated by ->. For example: S -> a | b*S

    Parameters
    ----------
    productions : dict of str to Regex, optional
        The productions or rules of the ECFG
    start_symbol : str, optional
        The start symbol
    """

    def __init__(self, productions: dict[str, Regex] = None, start_symbol: str = None):
        if start_symbol is None:
            start_symbol = "S"
        if productions is None:
            productions = dict()

        self.start_symbol = start_symbol
        self.productions = productions

    @classmethod
    def from_cfg(cls, cfg: CFG):
        """Transforms the CFG to ECFG

        Parameters
        ----------
        cfg : CFG
            The context free grammar

        Returns
        ----------
        result : ECFG
            The extended context free grammar equivalent to cfg

        """
        result = ECFG()
        result.start_symbol = cfg.start_symbol.value

        for production in cfg.productions:
            regex = Regex(".".join(map(lambda elem: elem.value, production.body)))

            if production.head in result.productions:
                result.productions[production.head.value] = result.productions[
                    production.head.value
                ].union(regex)
            else:
                result.productions[production.head.value] = regex

        return result
