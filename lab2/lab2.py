from dimacs import *
from copy import deepcopy
from random import shuffle, randint
import numpy as np
from scipy.sparse import dok_matrix
from scipy.optimize import linprog


def nodes(G):
    """
    Returns a set of all nodes from given graph G.
    """
    return set(range(len(G)))


def edges(G):
    """
    Yields every edge from graph G.
    This is roughly equivalent to `edgeList(G)` but slightly more efficient.
    """
    for u, N_u in enumerate(G):  # yields pairs (vertex id, neighbours set)
        for v in N_u:
            if u <= v:  # ensures only one yield per each edge
                yield (u, v)


def find_vertex_cover_2_approximation(G):
    """
    Algorytm 2-aproksymacyjny (wybieramy niepokrytą krawędź, dodajemy oba jej wierzchołki do rozwiązania)
    """
    C = set()
    E = edgeList(G)
    shuffle(E)  # optional

    for u, v in E:  # single pass is enough
        if u not in C and v not in C:
            C.add(u)
            C.add(v)
            if isVC(E, C):
                return C


def find_vertex_cover_log_n_approximation(G):
    """
    Algorytm O(log n)-aproksymacyjny (dodajemy do rozwiązania wierzchołek o najwyższym aktualnym stopniu)
    """
    C = set()
    G = deepcopy(G)
    V = nodes(G)

    while True:
        u = max(V, key=lambda u: len(G[u]))
        if not G[u]:
            return C

        C.add(u)
        if isVC(edges(G), C):
            return C

        for v in G[u]:  # no need to .copy()
            G[v].remove(u)
        G[u].clear()  # faster than removing one-by-one
        V.remove(u)  # for performance only


def find_vertex_cover_linear_programming(G):
    """
    Rozwiązanie problemu w liczbach wymiernych i zaokrąglenie wyników
    """
    V = nodes(G)
    E = edgeList(G)

    if len(V) > 1e4 or len(E) > 1e4:  # f56 has 109601 edges, nobody has time for that
        return V

    A = dok_matrix((len(E), len(V)), dtype=np.float64)
    for i, (u, v) in enumerate(E):
        A[i, u] = A[i, v] = 1

    c = np.ones((len(V),))
    b = np.ones((len(E),))

    result = linprog(c, A_ub=-A, b_ub=-b, bounds=(0, None), options={'sparse': True})  # ub means upper bound
    C = set(np.argwhere(result.x >= 0.5).ravel())

    if not isVC(E, C):  # if something went wrong
        return V

    return C


def find_vertex_cover_simulated_annealing(G):
    # what else, genetic algorithms?!
    # already done that for TSP and sudoku
    # https://github.com/tomekzaw/agh_sem4_mownit2/blob/master/lab4/Laboratorium_4_Tomasz_Zawadzki.pdf
    pass


def optimize_vertex_cover_greedy_single_pass(G, C):
    """
    usuwanie w losowej kolejności wierzchołków z rozwiązania obliczonego przez dany algorytm,
    o ile nie powoduje to, że tracimy pokrycie wierzchołkowe
    """
    C = list(C)
    shuffle(C)
    while True:
        for u in C:
            if all(v in C for v in G[u]):
                C.remove(u)
                break
        else:
            return C


def optimize_vertex_cover_greedy_multi_pass(G, C):
    """
    usuwanie w losowej kolejności wierzchołków z rozwiązania obliczonego przez dany algorytm,
    o ile nie powoduje to, że tracimy pokrycie wierzchołkowe
    """
    C = C.copy()  # leave the original solution untouched
    for _ in range(100):
        for u in C:
            if all(v in C for v in G[u]):
                C.remove(u)
                break
        else:
            for _ in range(randint(0, 10)):
                C.add(randint(0, len(G)-1))
    for u in C:
        if all(v in C for v in G[u]):
            C.remove(u)
            break
    return C
