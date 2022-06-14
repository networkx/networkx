from collections import deque

import networkx as nx
from enum import Enum


class State(Enum):
    D = "descending"
    U = "ascending"
    N = "untouched"
    P = "pivot"


class Operation(Enum):
    A = "add"
    D = "delete"


def g_1():
    G = nx.Graph()

    edge_list = [('3', '4'), ('3', '7'), ('4', '8'), ('6', '7'), ('7', '8')]

    for edge in edge_list:
        G.add_edge(*edge)

    return G


def kourtellis_dynamic_bc(G):
    bc, D, SP, Delta = nx.betweenness_centrality(G, xtra_data=True, normalized=False)
    new_edge = ('v1', 'v2')

    algorithm_1(G, bc, D, SP, Delta, new_edge, "add")


def algorithm_1(G, bc, D, SP, Delta, edge, operation):
    if not (operation == "add" or operation == "delete"):
        raise TypeError("edge operation must be add or delete")

    for s in G:
        u_low = find_lowest(s, edge[0], edge[1], D)  # furthest away from s
        u_high = find_highest(s, edge[0], edge[1], D)  # closest to s
        dd = D[s][u_low] - D[s][u_high]  # distance difference between endpoints of newly added edge relative to s

        if dd == 0:
            continue  # same level addition deletion

        if dd >= 1:
            SPd, Dd, Delta_d, flag = {}, {}, {}, {}  # data structures to store updates from dynamic addition/deletion
            for r in G:
                SPd[r], Dd[r], Delta_d[r] = SP[s][r], D[s][r], Delta[s][r]
                flag[r] = State.N
            Q_lvl, Q_bfs = {}, deque([u_low])
            if operation == "add":
                if dd == 1:  # 0 level rise
                    algorithm_2(G, s, u_low, u_high, Q_lvl, Q_bfs, flag, bc, SP, SPd, Dd, Delta, Delta_d, operation)
                if dd > 1:  # 1 or more level rise
                    algorithm_4(G, s, u_low, u_high, Q_lvl, Q_bfs, flag, bc, SP, SPd, D, Dd, Delta, Delta_d)
            if operation == "delete":
                if u_low.has_predecessors():  # 0 level drop
                    algorithm_2(G, s, u_low, u_high, Q_lvl, Q_bfs, flag, bc, SP, SPd, Dd, Delta, Delta_d, operation)
                else:  # 1 or more level drop
                    algorithm_6()

        for r in G:  # must have updated G
            SP[s][r], D[s][r] = SPd[r], Dd[r]
            if flag[r] != State.N:
                Delta[s][r] = Delta_d[r]


def algorithm_2(G, s, u_low, u_high, Q_lvl, Q_bfs, flag, bc, SP, SPd, Dd, Delta, Delta_d, operation):
    Q_lvl[Dd[u_low]], flag[u_low] = u_low, State.D  # mistake here must be handled, append distance to list
    if operation == "add":
        SPd[u_low] += SP[s][u_high]
    if operation == "delete":
        SPd[u_low] -= SP[s][u_high]

    while Q_bfs:
        v = Q_bfs.popleft()
        for w in G[v]:  # adjacent nodes
            if Dd[w] == Dd[v] + 1:
                if flag[w] == State.N:
                    Q_lvl[Dd[w]], flag[w] = w, State.D
                    Q_bfs.append(w)
                    SPd[w] += (SPd[v] - SP[s][v])
    if operation == "delete":
        Delta_d[u_high] = Delta[s][u_high] - (SP[s][u_high]/SP[s][u_low]) * (1 + Delta[s][u_low])
        Q_lvl[Dd[u_high]], flag[u_high] = u_high, State.U  # must be fixed

    level = G.number_of_nodes()
    while level > 0:
        for w in Q_lvl[level]:
            for v in G[w]:  # adjacent nodes
                if Dd[v] < Dd[w]:  # be mindful of order of v, w in alg 3
                    flag, Delta_d, Q_lvl, a = algorithm_3(s, v, w, flag, Delta, Delta_d, SP, SPd, Q_lvl, level)
                    if operation == "add":
                        if flag[v] == State.U and (v != u_high or w != u_low):
                            Delta_d[v] -= a
                    if operation == "delete":
                        if flag[v] == State.U:
                            Delta_d[v] -= a
            if w != s:
                bc[w] += (Delta_d[w] - Delta[s][w])
        level -= 1
    return


def algorithm_3(s, v, w, flag, Delta, Delta_d, SP, SPd, Q_lvl, level):
    if flag[v] == State.N:
        flag[v] = State.U
        Delta_d[v] = Delta[s][v]
        Q_lvl[level-1] = v  # must be fixed
        Delta_d[v] += (SPd[v]/SPd[w]) * (1 + Delta_d[w])
        a = (SP[s][v]/SP[s][w]) * (1 + Delta[s][w])
        return flag, Delta_d, Q_lvl, a


def algorithm_4(G, s, u_low, u_high, Q_lvl, Q_bfs, flag, bc, SP, SPd, D, Dd, Delta, Delta_d):
    Q_lvl[D[u_low]], Dd[u_low] = u_low, D[s][u_high]  # mistake here must be handled, append distance to list
    while Q_bfs:
        v, flag[v], SPd[v] = Q_bfs.popleft(), State.D, 0
        for w in G[v]:  # adjacent nodes
            if Dd[w] + 1 == Dd[v]:
                SPd[v] += SPd[w]
            if Dd[w] > Dd[v] and flag[w] == State.N:
                flag[w], Dd[w] = State.D, Dd[v] + 1
                Q_lvl[Dd[w]] = w  # must be fixed
                Q_bfs.append(w)
            if Dd[w] == Dd[v] and D[s][w] != D[s][v]:
                if flag[w] == State.N:
                    flag[w] = State.D
                    Q_lvl[Dd[w]] = w
                    Q_bfs.append(w)
    level = G.number_of_nodes()
    while level > 0:
        for w in Q_lvl[level]:
            for v in G[w]:  # adjacent nodes
                if Dd[v] < Dd[w]:  # be mindful of order of v, w in alg 3
                    flag, Delta_d, Q_lvl, a = algorithm_3(s, v, w, flag, Delta, Delta_d, SP, SPd, Q_lvl, level)
                    if flag[w] == State.U and (v != u_high or w != u_low):
                        Delta_d[v] -= a
            if w != s:
                bc[w] += (Delta_d[w] - Delta[s][w])
        level -= 1


def algorithm_6(G, s, u_low, u_high, Q_lvl, flag, bc, SP, SPd, D, Dd, Delta, Delta_d):
    PQ, Q_bfs = {}, deque([])  # mistake here must be handled, must be dict of lists
    first = None  # don't understand this line yet
    Q_bfs.append(u_low)
    flag[u_low] = State.N
    while Q_bfs:
        v = Q_bfs.popleft()
        for w in G[v]:  # adjacent nodes
            if D[s][w] + 1 == D[s][v] and flag[w] == State.N and flag[v] != State.P:
                PQ[D[s][v]], flag[v] = v, State.P  # a new pivot
                if first > D[s][v]:
                    first = D[s][v]  # the first pivot
            elif D[s][w] == D[s][v] + 1 or D[s][w] == D[s][v]:
                if flag[w] == State.N:
                    Q_bfs.append(w)
                    flag[w] = State.N
    if not PQ.is_empty():  # don't quite understand yet
        algorithm_7()
    elif PQ.is_empty():  # don't quite understand yet
        print("adjust appropriately for disconnected components")


def algorithm_7(G, s, u_low, u_high, Q_lvl, flag, bc, SP, SPd, D, Dd, Delta, Delta_d, PQ, first):
    Q_bfs = deque([])
    Q_bfs.append(PQ[first])
    nxt = first + 1
    while Q_bfs:
        v = Q_bfs.popleft()
        flag[v], Q_lvl[Dd[v]], SPd[v] = State.D, v, 0  # must be fixed
        if nxt == Dd[v] + 1:
            Q_bfs.append(PQ[nxt])  # don't understand this line yet
            nxt += 1
        for w in G[v]:  # adjacent nodes
            if flag[w] == State.N:
                flag[w], Dd[w] = State.D, Dd[v] + 1
                Q_bfs.append(w)
            elif flag[w] == State.P:
                flag[w] = State.D
            else:
                if Dd[w] + 1 == Dd[v]:
                    SPd[v] += SPd[v]
                if Dd[w] == Dd[v] and D[s][w] != D[s][v]:
                    if D[s][w] > D[s][v] and flag[w] != State.D:
                        flag[w] = State.D
                        Q_lvl[Dd[w]] = w  # must be fixed
                        Q_bfs.append(w)
    Delta_d[u_high] = Delta[s][u_high] - (SP[s][u_high]/SP[s][u_low]) * (1 + Delta[s][u_low])
    Q_lvl[Dd[u_high]], flag[u_high] = u_high, State.U  # must be fixed
    level = G.number_of_nodes()
    while level:
        for w in Q_lvl[level]:
            for v in G[w]:  # adjacent nodes
                if Dd[v] < Dd[w]:  # be mindful of order of v, w in alg 3
                    flag, Delta_d, Q_lvl, a = algorithm_3(s, v, w, flag, Delta, Delta_d, SP, SPd, Q_lvl, level)
                    a = 0
                if D[s][w] > D[s][v]:
                    a = (SP[s][v]/SP[s][w]) * (1 + Delta[s][w])
                elif D[s][w] < D[s][v]:
                    a = (SP[s][w] / SP[s][v]) * (1 + Delta[s][v])
                if flag[v] == State.U:
                    Delta_d[v] -= a
            if w != s:
                bc[w] += (Delta_d[w] - Delta[s][w])
        level -= 1


def find_lowest(s, v_1, v_2, D):
    if v_1 or v_2 not in D:
        print("from find lowest: v_1 or v_2 not in G")
    return max(D[s][v_1], D[s][v_2])


def find_highest(s, v_1, v_2, D):
    if v_1 or v_2 not in D:
        print("from find highest: v_1 or v_2 not in G")
    return min(D[s][v_1], D[s][v_2])


if __name__ == '__main__':
    G_1 = g_1()
    kourtellis_dynamic_bc(G_1)
