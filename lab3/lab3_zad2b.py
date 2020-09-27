from dimacs import *
import pycosat
from pysat.formula import CNF
from pysat.solvers import Glucose4


def vertex_cover_to_sat_cnf(G, k):
    """
    Reduces Vertex Cover instance to SAT-CNF instance.
    """
    n = len(G)

    def y(i, j):
        return (i+j)*(i+j+1)//2+i + n+1

    cnf_x = edgeList(G)

    cnf_y_i0 = [
        [y(i, 0)]
        for i in range(n+1)
    ]
    cnf_y_0j = [
        [-y(0, j)]
        for j in range(1, n+1)
    ]
    cnf_impl1 = [
        [-y(i-1, j), y(i, j)]
        for i in range(1, n+1)
        for j in range(1, n+1)
    ]
    cnf_impl2 = [
        [-y(i-1, j-1), -i, y(i, j)]
        for i in range(1, n+1)
        for j in range(1, n+1)
    ]
    cnf_last = [
        [-y(n, k+1)]
    ]

    cnf = cnf_x + cnf_y_i0 + cnf_y_0j + cnf_impl1 + cnf_impl2 + cnf_last
    return cnf


def solve_sat_cnf_pycosat(cnf):
    result = pycosat.solve(cnf)
    if result == 'UNSAT':
        return None
    # see pycoSAT docs at https://pypi.org/project/pycosat/
    if result == 'UNKNOWN':
        raise Exception(
            'Solution could not be determined within the propagation limit')
    return result


def solve_sat_cnf_glucose(cnf):
    g = Glucose4(cnf)
    if g.solve():
        return g.get_model()
    return None


def sat_cnf_solution_to_vertex_cover_solution(G, result):
    return set(x for x in result if 0 < x < len(G))


def find_vertex_cover_sat_cnf_reduction(G, k, solver=solve_sat_cnf_pycosat):
    """
    Finds the vertex cover using SAT solver.
    """
    cnf = vertex_cover_to_sat_cnf(G, k)

    result = solver(cnf)
    if result is None:
        return None

    C = sat_cnf_solution_to_vertex_cover_solution(G, result)
    return C

    n = len(G)
    return set(x for x in result if 0 < x < n)


def find_min_vertex_cover_linear_search(G, algo, **kwargs):
    """
    Performs linear search to find minimal vertex cover from k=0 to k=|V| inclusive
    using selected algorithm for graph G given as adjacency list.
    """
    for k in range(len(G)):
        C = algo(G, k, **kwargs)
        if C is not None:
            return C


def find_min_vertex_cover_binary_search(G, algo, **kwargs):
    """
    Performs binary search to find minimal vertex cover from k=0 to k=|V| inclusive
    using selected algorithm for graph G given as adjacency list.
    """
    E = edgeList(G)
    if not E:
        return set()

    Cs = {}
    l = 0  # doesn't work
    r = len(G)-1  # works
    while True:
        if l+1 == r:
            if r in Cs:
                return Cs[r]
            return algo(G, r, **kwargs)

        m = (l+r) // 2
        Cs[m] = algo(G, m, **kwargs)
        if Cs[m] is None:
            l = m
        else:
            r = m


if __name__ == '__main__':
    G = loadGraph('graph/m40')
    C = find_min_vertex_cover_binary_search(
        G, algo=find_vertex_cover_sat_cnf_reduction, solver=solve_sat_cnf_pycosat)
    if isVC(edgeList(G), C):
        k = len(C)
        print(f'Passed, k={k}')
    else:
        print('Failed')
