from pyformlang.finite_automaton import EpsilonNFA

from project.ecfg.ecfg import ECFG


class RSM:
    """A class representing a recursive state machine

    Parameters
    ----------
    automata : dict of str to EpsilonNFA, optional
        The automata boxes of RSM
    start_symbol : str, optional
        The start symbol
    """

    def __init__(
        self, automata: dict[str, EpsilonNFA] = None, start_symbol: str = None
    ):
        if start_symbol is None:
            start_symbol = "S"
        if automata is None:
            automata = dict()

        self.start_symbol = start_symbol
        self.automata = automata

    @classmethod
    def from_ecfg(cls, ecfg: ECFG):
        """Transforms the ECFG to RSM

        Parameters
        ----------
        ecfg : ECFG
            The extended context free grammar

        Returns
        ----------
        result : RSM
            The recursive state machine equivalent to ecfg
        """
        result = RSM()
        result.start_symbol = ecfg.start_symbol

        for var, regex in ecfg.productions.items():
            result.automata[var] = regex.to_epsilon_nfa()

        return result

    def minimize(self) -> "RSM":
        """Minimize the current RSM

        Returns
        ----------
        result : RSM
            The minimal RSM
        """
        result = self

        for var, automaton in result.automata:
            result.automata[var] = automaton.minimize()

        return result
