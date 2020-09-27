from dimacs import *
from pulp import *
# does not work on Windows, "ImportError: cannot import name 'clock' from 'time' (unknown location)", use WSL or Linux instead
from random import randint  # for random weights
# from operator import mul
# from itertools import starmap


def find_min_vertex_cover_ilp(G, weights=None, relaxed=False, solver=GLPK(msg=0)):
    """
    Reduces Vertex Cover instance to Integer Linear Programming instance,
    solves ILP using provided solver and interprets the results.
    """
    model = LpProblem('vertex_cover', LpMinimize)

    params = dict(cat='Continuous', lowBound=0, upBound=1) if relaxed else dict(cat='Binary')
    xs = [LpVariable(f'x{i}', **params) for i in range(len(G))]

    if weights is None:
        ws = 1
    elif weights == 'deg':
        ws = map(len, G)
    elif weights == 'id':
        ws = range(len(G))
    elif weights == 'rand':
        ws = [randint(1, 10) for _ in range(len(G))]
    else:
        assert len(weights) == len(G)
        ws = weights

    # model += sum(w * x for w, x in zip(ws, xs))
    # model += sum(starmap(mul, zip(ws, xs)))
    model += lpDot(ws, xs)

    for u, v in edgeList(G):
        model += (xs[u] + xs[v] >= 1)

    model.solve(solver)
    assert LpStatus[model.status] == 'Optimal'

    threshold = 0.5 if relaxed else 1
    C = set(i for i, x in enumerate(xs) if value(x) is not None and value(x) >= threshold)

    k = value(model.objective)

    return C, k


if __name__ == '__main__':
    graph = 'm40'
    G = loadGraph(f'graph/{graph}')

    C, k = find_min_vertex_cover_ilp(G)
    # C, k = find_min_vertex_cover_ilp(G, weights='deg')
    # C, k = find_min_vertex_cover_ilp(G, weights='rand')
    # C, k = find_min_vertex_cover_ilp(G, relaxed=True)
    # C, k = find_min_vertex_cover_ilp(G, weights='deg', relaxed=True)
    # C, k = find_min_vertex_cover_ilp(G, weights='rand', relaxed=True)

    E = edgeList(G)
    if isVC(E, C):
        saveSolution(f'graph/{graph}.sol', C)
        print(f'Passed, k={k}')
    else:
        print('Failed')
