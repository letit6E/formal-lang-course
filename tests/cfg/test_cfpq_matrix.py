from pathlib import Path

import networkx as nx

from project.cfg.cfpq import matrix
from project.cfg.cfpq import hellings
from project.cfg.io import read_from_file


class TestsForMatrixCfpq:
    def test_cfpq_matrix(self):
        cfg = read_from_file(Path("./resources/cfg1"), "S")

        graph = nx.MultiDiGraph()
        graph.add_edge(60, 14, label="b")
        graph.add_edge(11, 52, label="b")
        graph.add_edge(23, 4, label="a")
        graph.add_edge(52, 15, label="a")
        graph.add_edge(35, 64, label="b")

        # test based on correctness of hellings.cfpq_all
        assert matrix.cfpq_all(cfg, graph) == hellings.cfpq_all(cfg, graph)

    def test_cfpq(self):
        cfg = read_from_file(Path("./resources/cfg2"), "S")

        graph = nx.MultiDiGraph()
        graph.add_edge(4, 1, label="b")
        graph.add_edge(5, 5, label="c")
        graph.add_edge(2, 4, label="a")
        graph.add_edge(5, 1, label="a")
        graph.add_edge(3, 4, label="c")

        # test based on correctness of hellings.cfpq_all
        assert matrix.cfpq(cfg, graph) == hellings.cfpq(cfg, graph)
