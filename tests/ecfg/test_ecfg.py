from pyformlang.cfg import CFG, Variable
from pyformlang.regular_expression import Regex

from project.ecfg.ecfg import ECFG


class TestsForECFG:
    def test_empty_init(self):
        empty_ecfg = ECFG()
        assert empty_ecfg.start_symbol == "S"
        assert len(empty_ecfg.productions) == 0

    def test_init(self):
        productions = {"A": Regex("bc.df.ae"), "B": Regex("A.B.c"), "X": Regex("A")}
        start_symbol = "X"

        ecfg = ECFG(productions, start_symbol)

        assert ecfg.start_symbol == start_symbol
        assert ecfg.productions == productions

    def test_from_cfg(self):
        cfg = CFG.from_text(
            """S -> a S b X
            X -> $""",
            Variable("S"),
        )

        ecfg = ECFG.from_cfg(cfg)

        assert ecfg.start_symbol == cfg.start_symbol.value
        assert set(ecfg.productions.keys()) == set(map(lambda tr: tr.head, cfg.productions))

        for cfg_head, ecfg_head in zip(map(lambda tr: tr.head, cfg.productions), ecfg.productions.keys()):
            assert cfg_head.value == ecfg_head

        for ecfg_regex, cfg_body in zip(ecfg.productions.values(), map(lambda tr: tr.body, cfg.productions)):
            values = list(map(lambda x: x.value, cfg_body))
            if values:
                assert ecfg_regex.accepts(values)