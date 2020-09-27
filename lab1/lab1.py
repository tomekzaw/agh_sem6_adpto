from dimacs import *
from copy import deepcopy
from itertools import combinations


def has_no_edges(G):
    """
    Returns True, if graph G given as adjacency list has no edges.
    This is equivalent to `len(edgeList(G)) == 0` but way more efficient.
    """
    return not any(G)  # bool(set()) == False, bool({1,2,3}) == True


def edges(G):
    """
    Yields every edge from graph G.
    This is roughly equivalent to `edgeList(G)` but slightly more efficient.
    """
    for u, N_u in enumerate(G):  # yields pairs (vertex_id: int, neighbours: set)
        for v in N_u:
            if u <= v:  # ensures only one yield per each edge
                yield (u, v)


def number_of_edges(G):
    """
    Returns number of edges in graph G given as adjacency list.
    Works only for graphs without self-loops.
    This is equivalent to `len(edgeList(G))` but way more efficient.
    """
    return sum(map(len, G)) // 2  # divide by 2 because each edge has been counted twice


def without(G, xs):
    """
    Returns a new graph without some nodes and all their adjacent edges.
    """
    G = deepcopy(G)
    for x in xs:
        for y in G[x]:  # no need to .copy()
            G[y].remove(x)
        G[x].clear()  # faster than removing one-by-one
    return G


def find_min_vertex_cover(G, algo):
    """
    Performs linear search to find minimal vertex cover from k=0 to k=|V| inclusive
    using selected algorithm for graph G given as adjacency list.
    """
    for k in range(len(G)):
        # some implementations could potentially destroy the original graph
        C = algo(deepcopy(G), k)
        if C is not None:
            return C


def find_vertex_cover_brute_force(G, k):
    """
    O(n^k)
    https://faliszew.github.io/apto/lab1#brute-force-onk
    """
    V = range(1, len(G)+1)  # don't include vertex 0
    E = edgeList(G)
    for C in combinations(V, k):
        if isVC(E, C):
            return C
    return None


def find_vertex_cover_2_k(G, k, S=frozenset()):
    """
    O(2^k)
    https://faliszew.github.io/apto/lab1#rekurencja-z-powrotami-o2k
    """
    for u, v in edges(G):
        if u not in S and v not in S:
            break
    else:  # no such edge found
        return S

    # found (u, v)

    if k == 0:
        return None

    C = find_vertex_cover_2_k(without(G, {u}), k-1, S | {u})
    if C is not None:
        return C

    return find_vertex_cover_2_k(without(G, {v}), k-1, S | {v})


def find_vertex_cover_1_618_k(G, k, S=frozenset()):
    """
    O(1.618^k)
    https://faliszew.github.io/apto/lab1#rekurencja-z-powrotami-o1618k
    """
    if k < 0:
        return None

    if has_no_edges(G):
        return S

    if k == 0:
        return None

    for u, N_u in enumerate(G):
        if N_u:  # if len(N_u) >= 1:
            break

    C = find_vertex_cover_1_618_k(without(G, {u}), k-1, S | {u})
    if C is not None:
        return C

    return find_vertex_cover_1_618_k(without(G, N_u), k-len(N_u), S | N_u)


def find_vertex_cover_1_47_k(G, k, S=frozenset()):
    """
    O(1.47^k)
    https://faliszew.github.io/apto/lab1#rekurencja-z-powrotami-o147k
    """
    if k < 0:
        return None

    if has_no_edges(G):
        return S

    if k == 0:
        return None

    w = 0
    for u, N_u in enumerate(G):
        if len(N_u) == 1:
            return find_vertex_cover_1_47_k(without(G, {u} | N_u), k-1, S | N_u)

        if len(N_u) > len(G[w]):
            w = u

    C = find_vertex_cover_1_47_k(without(G, {w}), k-1, S | {w})
    if C is not None:
        return C

    N_w = G[w]
    return find_vertex_cover_1_47_k(without(G, N_w), k-len(N_w), S | N_w)


def find_vertex_cover_kernelization(G, k):
    """
    https://faliszew.github.io/apto/lab1#kernelizacjia-to-już-dla-koneserów
    https://en.wikipedia.org/wiki/Kernelization#Example:_vertex_cover
    https://arxiv.org/pdf/1811.09429.pdf#subsection.2.1
    """
    S = set()

    for u, N_u in enumerate(G):  # self-loops
        if u in N_u:
            G = without(G, {u})
            k -= 1
            S.add(u)

    def inner(G, k, S):
        if k < 0:
            return None

        for u, N_u in enumerate(G):
            if len(N_u) == 1:
                return inner(without(G, N_u), k-1, S | N_u)  # N_u == {v}

            if len(N_u) > k:
                return inner(without(G, {u}), k-1, S | {u})

        if number_of_edges(G) > k*k:
            return None

        C = find_vertex_cover_1_47_k(G, k)
        if C is not None:
            return S | C

        return None

    return inner(G, k, S)
