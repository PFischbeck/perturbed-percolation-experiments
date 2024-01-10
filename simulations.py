import itertools
from collections import deque
from enum import Enum
from typing import Collection

import networkit as nk


class ActivationType(Enum):
    LOCAL = 1
    GLOBAL = 2
    BOTH = 3


def run_bootstrap_percolation(g: nk.Graph, r: int, initially_active: Collection[int]):
    """Run bootstrap percolation on a single graph. Some nodes are activated initially,
     and every node with at least r active neighbors is activated in the next round. """
    n = g.numberOfNodes()

    marks = [0] * n
    activation_phase = [-1] * n
    activation_queue = deque()

    for v in initially_active:
        marks[v] = r
        activation_phase[v] = 0
        activation_queue.append(v)

    while activation_queue:
        v = activation_queue.popleft()

        for nei in g.iterNeighbors(v):
            if marks[nei] < r and activation_phase[nei] == -1:
                marks[nei] += 1
                if marks[nei] == r:
                    activation_queue.append(nei)
                    activation_phase[nei] = activation_phase[v] + 1

    new_activations = [{type_name: 0 for type_name in ActivationType} for _ in range(max(activation_phase) + 1)]

    for i in range(n):
        if activation_phase[i] != -1:
            new_activations[activation_phase[i]][ActivationType.LOCAL] += 1

    total_activations = list(itertools.accumulate(sum(acts.values()) for acts in new_activations))

    return new_activations, total_activations


def run_perturbed_percolation(g_local: nk.Graph, g_global: nk.Graph, r: int, initially_active: int):
    """Run perturbed percolation on a local graph and global graph. A single node is initially active, and every node
    with at least 1 (local graph) or r (global graph) active neighbors is activated in the next round. """

    n = g_local.numberOfNodes()
    assert (g_global.numberOfNodes() == n)

    marks = [0] * n
    activation_phase = [-1] * n
    activation_type = [None] * n
    activation_queue = deque()

    for v in [initially_active]:
        marks[v] = r
        activation_phase[v] = 0
        activation_queue.append(v)
        activation_type[v] = ActivationType.LOCAL

    while activation_queue:
        v = activation_queue.popleft()

        for nei in g_global.iterNeighbors(v):
            if marks[nei] < r and activation_phase[nei] == -1:
                marks[nei] += 1
                if marks[nei] == r:
                    activation_queue.append(nei)
                    activation_phase[nei] = activation_phase[v] + 1
                    activation_type[nei] = ActivationType.GLOBAL

        for nei in g_local.iterNeighbors(v):
            if marks[nei] < r and activation_phase[nei] == -1:
                marks[nei] = r
                activation_queue.append(nei)
                activation_phase[nei] = activation_phase[v] + 1
                activation_type[nei] = ActivationType.LOCAL
            elif marks[nei] == r and activation_phase[nei] == activation_phase[v] + 1 and activation_type[nei] == ActivationType.GLOBAL:
                activation_type[nei] = ActivationType.BOTH

    new_activations = [{type_name: 0 for type_name in ActivationType} for _ in range(max(activation_phase) + 1)]

    for i in range(n):
        if activation_phase[i] != -1:
            new_activations[activation_phase[i]][activation_type[i]] += 1

    total_activations = list(itertools.accumulate(sum(acts.values()) for acts in new_activations))

    return new_activations, total_activations
