"""Independent enumerators of endpoint opportunities and closures."""

from fractions import Fraction
from itertools import permutations, product


def directed_oracle(G, focal):
    patterns = ("total", "source", "target", "head", "mid", "end", "cyclic")
    closed = dict.fromkeys(patterns, 0)
    opportunities = dict.fromkeys(patterns, 0)
    for j, k in permutations([n for n in G if n != focal], 2):
        first = [arc for arc in ((focal, j), (j, focal)) if G.has_edge(*arc)]
        second = [arc for arc in ((j, k), (k, j)) if G.has_edge(*arc)]
        for a, b in product(first, second):
            for c in ((focal, k), (k, focal)):
                out = sum(u == focal for u, _ in (a, b, c))
                if out == 2:
                    role = "head"
                elif out == 0:
                    role = "end"
                else:
                    degrees = {
                        n: sum(u == n for u, _ in (a, b, c)) for n in (focal, j, k)
                    }
                    role = "cyclic" if set(degrees.values()) == {1} else "mid"
                closing_role = "source" if c[0] == focal else "target"
                exists = int(G.has_edge(*c))
                for pattern in ("total", closing_role, role):
                    opportunities[pattern] += 1
                    closed[pattern] += exists
    return {
        p: closed[p] / opportunities[p] if opportunities[p] else 0.0 for p in patterns
    }


def weighted_closure_oracle(G, focal, weight, exact=False):
    maximum = max(
        (d.get(weight, 1) for u, v, d in G.edges(data=True) if u != v), default=0
    )
    if not maximum:
        return 0.0

    def w(u, v):
        if not G.has_edge(u, v):
            return 0
        value = G[u][v].get(weight, 1)
        return Fraction(value) / Fraction(maximum) if exact else value / maximum

    closed = opportunities = 0
    for j, k in permutations([n for n in G if n != focal], 2):
        if G.is_directed():
            first = [arc for arc in ((focal, j), (j, focal)) if G.has_edge(*arc)]
            second = [arc for arc in ((j, k), (k, j)) if G.has_edge(*arc)]
            for a, b in product(first, second):
                opportunities += 2 * w(*a) * w(*b)
                closed += w(*a) * w(*b) * (w(focal, k) + w(k, focal))
        else:
            opportunities += w(focal, j) * w(j, k)
            closed += w(focal, j) * w(j, k) * w(k, focal)
    return closed / opportunities if opportunities else 0.0
