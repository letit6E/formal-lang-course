from networkx import MultiDiGraph
from pyformlang.cfg import CFG, Variable
from scipy.sparse import dok_matrix

from project.cfg.transformers import transform_to_wcnf


def cfpq_all(cfg: CFG, graph: MultiDiGraph) -> set[tuple[any, Variable, any]]:
    """Executes the matrix algorithm for all the pair of nodes in a graph using the specified grammar.

    Parameters
    ----------
    cfg : CFG
        The context-free grammar to be used for deriving the subgraphs.
    graph : MultiDiGraph
        The directed graph used to yield the subgraphs.

    Returns
    -------
    set[tuple[Any, Variable, Any]]
        A set of tuples, each containing two nodes of the graph and a variable.
        Each tuple represents a valid path in the graph as per the grammar.

    """
    wcnf = transform_to_wcnf(cfg)

    eps_production_vars = set()
    term_productions = set()
    var_productions = set()
    for production in wcnf.productions:
        if not production.body:
            eps_production_vars.add(production.head.value)
        elif len(production.body) == 1:
            term_productions.add(production)
        elif len(production.body) == 2:
            var_productions.add(production)

    vars_matrices = {
        var.value: dok_matrix(
            (graph.number_of_nodes(), graph.number_of_nodes()), dtype=bool
        )
        for var in wcnf.variables
    }

    node_to_indexes = {}
    nodes = list(graph.nodes)
    for i in range(len(nodes)):
        node_to_indexes[nodes[i]] = i

    for i, j, data in graph.edges(data=True):
        symbol = data["label"]
        for production in term_productions:
            if production.body[0].value == symbol:
                var = production.head.value
                vars_matrices[var][node_to_indexes[i], node_to_indexes[j]] = True

    for i in graph.nodes:
        for var in eps_production_vars:
            vars_matrices[var][node_to_indexes[i], node_to_indexes[i]] = True

    prev_nnz = -1
    cur_nnz = sum([matrix.getnnz() for matrix in vars_matrices.values()])
    while cur_nnz != prev_nnz:
        prev_nnz = cur_nnz

        for production in var_productions:
            vars_matrices[production.head.value] += (
                vars_matrices[production.body[0].value]
                @ vars_matrices[production.body[1].value]
            )

        cur_nnz = sum([matrix.getnnz() for matrix in vars_matrices.values()])

    result = set()
    for var, matrix in vars_matrices.items():
        for i, j in zip(*matrix.nonzero()):
            result.add((nodes[i], Variable(var), nodes[j]))

    return result


def cfpq(
    cfg: CFG,
    graph: MultiDiGraph,
    start_nodes: set = None,
    final_nodes: set = None,
    start_symbol: Variable = Variable("S"),
) -> set[tuple[any, any]]:
    """Computes the context-free path querying (CFPQ) for the given graph and grammar.

    The function performs the matrix-based algorithm for CFPQ, but only adds the paths
    from the start nodes to the final nodes with the specified start symbol.

    Parameters
    ----------
    cfg : CFG
        The context-free grammar used for path querying.
    graph : MultiDiGraph
        The directed graph used for path querying.
    start_nodes : set, optional
        The set of nodes from which paths can start. If not provided, all nodes are considered as start nodes.
    final_nodes : set, optional
        The set of nodes where paths can end. If not provided, all nodes are considered as final nodes.
    start_symbol : str, optional
        The start symbol of the grammar. If not provided, 'S' is considered as the start symbol.

    Returns
    -------
    set[tuple[any, any]]
        A set of tuples representing the start and end nodes of the paths in the graph
        that are valid according to the specified context-free grammar.

    """
    if start_nodes is None:
        start_nodes = set(graph.nodes)
    if final_nodes is None:
        final_nodes = set(graph.nodes)
    if start_symbol is None:
        start_symbol = "S"

    matrix_result = cfpq_all(cfg, graph)

    cfpq_result = set()
    for start_node, var, final_node in matrix_result:
        if (
            var.value == start_symbol
            and start_node in start_nodes
            and final_node in final_nodes
        ):
            cfpq_result.add((start_node, final_node))

    return cfpq_result
