import random
import pycosat
import numpy as np
import matplotlib.pyplot as plt


def randlit(n):
    var = random.randint(1, n)
    return var if random.getrandbits(1) else -var


def randclause(n, k):
    return [randlit(n) for _ in range(k)]


def randcnf(n, k, c):
    return [randclause(n, k) for _ in range(c)]


if __name__ == '__main__':
    k = 4  # liczba zmiennych w klauzuli, k=3 to SAT-3CNF
    n = 11  # liczba zmiennych, 10, 50, 100
    T = 2000  # liczba powtórzeń
    a_min = 1
    a_max = 21
    a_step = 0.05

    xs = np.arange(a_min, a_max+a_step, a_step)
    ys = []

    for a in xs:
        S = 0
        for _ in range(T):
            cnf = randcnf(n, k, int(a*n))
            if pycosat.solve(cnf) != 'UNSAT':
                S += 1
        p = S / T
        ys.append(p)
        print(a, p)

    plt.grid()
    plt.title(f'${k=}, {n=}, {T=}$')
    plt.ylabel('P(cnf is SAT)')
    plt.xlabel('iloraz liczby klauzul i liczby zmiennych')
    plt.ylim((-0.1, 1.1))
    plt.xlim((a_min, a_max))
    plt.scatter(xs, ys, s=7)
    plt.savefig('wykres.png')
