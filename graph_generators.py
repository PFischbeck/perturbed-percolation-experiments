import math
import random

import igraph
import networkit as nk
from pygirgs import girgs


# Return a power-law distribution
def powerlaw_generate(n, d, beta):
    import numpy as np

    n = int(n)

    degrees = np.array([0.]*n)
    for i in range(n):
        deg = (i+1) ** (1 / (-beta+1))
        degrees[i] = deg

    factor = d * n / sum(degrees)

    degrees *= factor
    degrees = np.around(degrees)

    return list(degrees)


def generate_ring(n: int):
    """Generates a ring, i.e., a cycle of size n"""

    g = nk.Graph(n)

    for i in range(n):
        g.addEdge(i, (i+1) % n)

    return g


def generate_torus(n: int):
    """Generates a two-dimensional torus graph"""

    g = nk.Graph(n)

    sqrt_n = int(n ** 0.5)
    assert sqrt_n**2 == n, "n has to be square!"

    def coords_to_index(x, y):
        return y * sqrt_n + x

    def index_to_coords(i):
        return i % sqrt_n, i // sqrt_n

    for i in range(n):
        x, y = index_to_coords(i)
        # Only add edges into one direction, since the graph is undirected
        for dx, dy in [(+1, 0), (0, +1)]:
            x2 = (x + dx) % sqrt_n
            y2 = (y + dy) % sqrt_n
            j = coords_to_index(x2, y2)
            g.addEdge(i, j)

    return g


def generate_er(n: int, k: float):
    """Generates an Erdos-Renyi random graph"""
    return nk.generators.ErdosRenyiGenerator(n, k / (n - 1)).generate()


def generate_chung_lu_pl(n: int, k: float, beta: float = 3.0):
    """Generates a Chung Lu graph with power-law degree distribution"""
    degree_sequence = powerlaw_generate(n, k, beta)
    return nk.generators.ChungLuGenerator(degree_sequence).generate()


def generate_girg(n: int, k: float, beta: float, T: float):
    """Generates a geometric inhomogeneous random graph"""
    dimension = 1

    wseed = random.randrange(10000)
    pseed = random.randrange(10000)
    sseed = random.randrange(10000)

    alpha = 1 / T

    weights = girgs.generate_weights(n, beta, wseed, False)
    positions = girgs.generate_positions(n, dimension, pseed, False)
    scaling = girgs.scale_weights(weights, k, dimension, alpha)
    weights = [scaling * weight for weight in weights]
    edges = girgs.generate_edges(weights, positions, alpha, sseed)

    g = nk.Graph(n)

    for u, v in edges:
        g.addEdge(u, v)

    return g


def generate_rgg(n: int, k: float):
    """Generates a 2-dimensional random geometric graph"""

    # In general, choose r such that the graph is connected whp, i.e., k = ln(n) + Omega(1)
    # k = 2 * math.log(n)
    r = math.sqrt(k / (math.pi * n))

    g_igraph = igraph.Graph.GRG(n, r, torus=True)

    g = nk.Graph(n)
    for u, l in enumerate(g_igraph.get_adjlist()):
        for v in l:
            if u < v:
                g.addEdge(u, v)
    return g
