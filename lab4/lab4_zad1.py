from pulp import *


if __name__ == '__main__':
    model = LpProblem('zad1', LpMinimize)

    # x = LpVariable('x', cat='Continuous')
    # y = LpVariable('y', cat='Continuous')
    x = LpVariable('x', cat='Integer')
    y = LpVariable('y', cat='Integer')

    model += x + y

    model += y >= x-1
    model += y >= -4*x+4
    model += y <= -0.5*x+3

    # print(model)

    model.solve()
    # model.solve(GLPK(msg=0))

    for var in model.variables():
        print(f'{var.name} = {var.varValue}')

    # print(value(model.objective))

    print(LpStatus[model.status])

    # print(x.value())
    # print(y.value())
