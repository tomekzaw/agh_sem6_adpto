from dimacs import *
from pulp import *
# does not work on Windows, "ImportError: cannot import name 'clock' from 'time' (unknown location)", use WSL or Linux instead
import networkx as nx  # for visualization purposes only
import matplotlib.pyplot as plt  # same here


def find_graph_coloring_ilp(G, k=None, optimal=False, solver=GLPK(msg=0)):
    """
    Reduces Graph Coloring instance to Integer Linear Programming instance,
    solves ILP using provided solver and interprets the results.
    """
    model = LpProblem('graph_coloring', LpMinimize)

    V = tuple(range(len(G)))  # all nodes

    if k is None:
        k = len(V)  # X(G) <= |V|

    C = tuple(range(k))  # all colors

    xs = {
        (v, c): LpVariable(f'x{v},{c}', cat='Binary')
        for v in V
        for c in C
    }

    for v in V:
        model += sum(xs[v, c] for c in C) == 1  # exactly one color per vertex

    for u, v in edgeList(G):
        for c in C:
            # at most one node with that color per edge
            model += (xs[u, c] + xs[v, c] <= 1)

    if optimal:  # minimize number of colors
        ys = [LpVariable(f'y{c}', cat='Binary') for c in C]
        for v in V:
            for c in C:
                # force y_c == 1 if color c is being used
                model += (ys[c] >= xs[v, c])
        model += sum(ys)  # objective: minimize sum of ys

    model.solve(solver)

    if LpStatus[model.status] == 'Infeasible':
        raise Exception(f'Graph is not colorable with {max_k} colors')

    assert LpStatus[model.status] == 'Optimal'

    # coloring = [next(c for c in C if value(xs[v, c]) == 1) for v in V]
    # k = len(set(coloring)
    coloring = {
        v: c
        for v in V
        for c in C
        if value(xs[v, c]) == 1
    }
    number_of_colors = len(set(coloring.values()))

    return coloring, number_of_colors


def is_valid_coloring(G, coloring):
    # for u, v in edgeList(G):
    #     if coloring[u] == coloring[v]:
    #         return False
    # return True
    return all(coloring[u] != coloring[v] for u, v in edgeList(G))


def visualize(G, coloring=None):
    nx_G = nx.Graph()
    nx_G.add_nodes_from(range(len(G)))
    nx_G.add_edges_from(
        (u, v)
        for u, N_u in enumerate(G)
        for v in N_u
    )

    real_colors = dict(zip(set(coloring.values()), ['red', 'yellow', 'green', 'blue', 'cyan', 'magenta', 'black']))
    node_colors = [real_colors[coloring[v]] for v in range(len(G))]

    pos = nx.circular_layout(nx_G)

    fig, ax = plt.subplots()
    ax.axis('off')
    nx.draw_networkx_nodes(nx_G, pos, node_color=node_colors, node_size=40, ax=ax)
    nx.draw_networkx_edges(nx_G, pos, ax=ax)
    fig.tight_layout()
    return fig


if __name__ == '__main__':
    G = loadGraph('all-instaces/1-FullIns_3.col')
    k = 10

    # coloring, number_of_colors = find_graph_coloring_ilp(G, k)
    coloring, number_of_colors = find_graph_coloring_ilp(G, k, optimal=True)

    if not is_valid_coloring(G, coloring):
        raise SystemExit('Failed')

    print(f'Passed, {number_of_colors} colors')

    fig = visualize(G, coloring)
    fig.savefig('visualization.png')
