from pyformlang.cfg import CFG, Variable
from pyformlang.regular_expression import Regex

from project.automata.builders import build_minimal_dfa
from project.ecfg.ecfg import ECFG
from project.rsm.rsm import RSM


class TestsForRSM:
    def test_init(self):
        rsm = RSM(start_symbol="M")

        assert rsm.start_symbol == "M"
        assert len(rsm.automata) == 0

    def test_from_ecfg(self):
        ecfg = ECFG.from_cfg(
            CFG.from_text(
                """S -> a S b X
                X -> $""",
                Variable("S"),
            )
        )

        rsm = RSM.from_ecfg(ecfg)

        assert rsm.start_symbol == "S"
        assert Regex("a.S.b.X").to_epsilon_nfa().is_equivalent_to(rsm.automata["S"])
        assert Regex("").to_epsilon_nfa().is_equivalent_to(rsm.automata["X"])

    def test_minimize(self):
        ecfg = ECFG.from_cfg(
            CFG.from_text(
                """S -> A X S
                A -> a S b X
                X -> $""",
                Variable("S"),
            )
        )
        rsm = RSM.from_ecfg(ecfg).minimize()

        assert rsm.start_symbol == "S"
        assert build_minimal_dfa(Regex("A.X.S")).is_equivalent_to(rsm.automata["S"])
        assert build_minimal_dfa(Regex("a.S.b.X")).is_equivalent_to(rsm.automata["A"])
        assert build_minimal_dfa(Regex("")).is_equivalent_to(rsm.automata["X"])
