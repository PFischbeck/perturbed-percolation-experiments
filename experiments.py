import math
import csv
import random
from pathlib import Path
from typing import Callable

import networkit as nk
from graph_generators import generate_chung_lu_pl, generate_girg

from simulations import ActivationType, run_perturbed_percolation, run_bootstrap_percolation


def average_degree(g: nk.Graph):
    n = g.numberOfNodes()
    m = g.numberOfEdges()
    return 2 * m / n


def reduce_graph_size(g: nk.Graph, n: int):
    """Reduce g to n nodes by removing by distance from a fixed node"""
    bfs = nk.distance.BFS(g, 0, False, True)
    bfs.run()
    remaining_nodes = bfs.getNodesSortedByDistance()[:n]
    g = nk.graphtools.subgraphFromNodes(g, remaining_nodes, compact=True)
    cc = nk.components.ConnectedComponents(g)
    cc.run()
    assert cc.numberOfComponents() == 1
    return g


def run_perturbed_on_real_world_experiment():
    """Runs perturbed percolation on two real-world graphs."""
    local_names = ["inf-roadNet-PA", "inf-roadNet-CA", "inf-italy-osm"]
    global_names = ["soc-google-plus",
                    "soc-twitter-follows", "soc-delicious", "soc-youtube"]

    with open(f"outputs/real_world_perturbed.csv", 'w') as csvfile:
        fieldnames = ['local_graph', 'global_graph', 'r', 'round',
                      'active', 'new', 'new_local', 'new_global', 'new_both']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        print("Running perturbed percolation experiments...")
        for local_name in local_names:
            local_source = str(Path(f"inputs/{local_name}.txt"))

            print(f"Reading local graph {local_name}...")
            g_local = nk.graphio.EdgeListReader(' ', 1).read(local_source)
            g_local = nk.components.ConnectedComponents.extractLargestConnectedComponent(
                g_local, compactGraph=True)
            n_local = g_local.numberOfNodes()

            for global_name in global_names:
                global_source = str(Path(f"inputs/{global_name}.txt"))

                print(f"Reading global graph {global_name}...")
                g_global: nk.Graph = nk.graphio.EdgeListReader(
                    ' ', 1).read(global_source)
                n = g_global.numberOfNodes()
                if n_local < n:
                    print(
                        f"Skipping {local_name}({n_local=}) + {global_name}({n=})")
                    return
                g_local_new = reduce_graph_size(g_local, n)

                # r = int(math.log(n))
                r = int(average_degree(g_global))
                initially_active = random.randrange(n)
                print("Running perturbed percolation...")
                new_activations, total_activations = run_perturbed_percolation(
                    g_local_new, g_global, r, initially_active)
                for cur_round, data in enumerate(new_activations):
                    writer.writerow({
                        'local_graph': local_name,
                        'global_graph': global_name,
                        'r': r,
                        'round': cur_round,
                        'active': total_activations[cur_round],
                        'new': sum(data.values()),
                        'new_local': data[ActivationType.LOCAL],
                        'new_global': data[ActivationType.GLOBAL],
                        'new_both': data[ActivationType.BOTH],
                    })


def run_perturbed_on_real_world_different_r_experiment():
    """Runs perturbed percolation on two real-world graphs for different values of r."""
    local_name = "inf-roadNet-CA"
    global_name = "soc-delicious"

    local_source = str(Path(f"inputs/{local_name}.txt"))

    print(f"Reading local graph {local_name}...")
    g_local = nk.graphio.EdgeListReader(' ', 1).read(local_source)
    g_local = nk.components.ConnectedComponents.extractLargestConnectedComponent(
        g_local, compactGraph=True)
    n_local = g_local.numberOfNodes()

    global_source = str(Path(f"inputs/{global_name}.txt"))

    print(f"Reading global graph {global_name}...")
    g_global: nk.Graph = nk.graphio.EdgeListReader(' ', 1).read(global_source)
    n = g_global.numberOfNodes()
    assert n_local >= n
    g_local_new = reduce_graph_size(g_local, n)

    r_values = [1, 3, 5, 7, 10, 15, 20, 40, 60]
    # Fix initial node across experiments
    initially_active = random.randrange(n)

    with open(f"outputs/real_world_perturbed_different_r.csv", 'w') as csvfile:
        fieldnames = ['local_graph', 'global_graph', 'r', 'round',
                      'active', 'new', 'new_local', 'new_global', 'new_both']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        print("Running perturbed percolation experiments...")
        for r in r_values:
            print(f"Running perturbed percolation with {r=}...")
            new_activations, total_activations = run_perturbed_percolation(
                g_local_new, g_global, r, initially_active)
            for cur_round, data in enumerate(new_activations):
                writer.writerow({
                    'local_graph': local_name,
                    'global_graph': global_name,
                    'r': r,
                    'round': cur_round,
                    'active': total_activations[cur_round],
                    'new': sum(data.values()),
                    'new_local': data[ActivationType.LOCAL],
                    'new_global': data[ActivationType.GLOBAL],
                    'new_both': data[ActivationType.BOTH],
                })


def run_bootstrap_on_real_world_experiment():
    bootstrap_trials = 50
    local_names = ["inf-roadNet-PA", "inf-roadNet-CA", "inf-italy-osm"]

    with open(f"outputs/real_world_bootstrap.csv", 'w') as csvfile:
        fieldnames = ['local_graph', 'trial', 'round', 'active',
                      'new', 'new_local', 'new_global', 'new_both']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        print("Running bootstrap percolation experiments...")
        for local_name in local_names:
            source = str(Path(f"inputs/{local_name}.txt"))

            print(f"Reading graph {local_name}...")
            g = nk.graphio.EdgeListReader(' ', 1).read(source)
            g = nk.components.ConnectedComponents.extractLargestConnectedComponent(
                g, compactGraph=True)
            n = g.numberOfNodes()
            for trial in range(1, bootstrap_trials + 1):
                print(f"Running trial {trial}/{bootstrap_trials}...")
                # Different initially active per trial
                initially_active = random.randrange(n)
                new_activations, total_activations = run_bootstrap_percolation(g, 1, [
                                                                               initially_active])
                for cur_round, data in enumerate(new_activations):
                    writer.writerow({
                        'local_graph': local_name,
                        'trial': trial,
                        'round': cur_round,
                        'active': total_activations[cur_round],
                        'new': sum(data.values()),
                        'new_local': data[ActivationType.LOCAL],
                        'new_global': data[ActivationType.GLOBAL],
                        'new_both': data[ActivationType.BOTH],
                    })


def run_perturbed_synthetic_plus_synthetic_experiment(local_gen: Callable[[int], nk.Graph], global_gen: Callable[[int, float], nk.Graph], name: str):
    """Runs perturbed percolation on a synthetic local graph and a synthetic global graph."""

    trials = 50
    n = 10**6
    k = math.log(n)
    r = int(k)

    with open(f"outputs/{name}.csv", 'w') as csvfile:
        fieldnames = ['trial', 'round', 'active', 'new',
                      'new_local', 'new_global', 'new_both']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for trial in range(1, trials + 1):
            print(f"Running trial {trial}/{trials}")
            print("Generating the local graph...")
            g_local = local_gen(n)
            print("Generating the global graph...")
            g_global = global_gen(n, k)
            initially_active = random.randrange(n)
            activations, total_active = run_perturbed_percolation(
                g_local, g_global, r, initially_active)
            for cur_round, data in enumerate(activations):
                writer.writerow({
                    'trial': trial,
                    'round': cur_round,
                    'active': total_active[cur_round],
                    'new': sum(data.values()),
                    'new_local': data[ActivationType.LOCAL],
                    'new_global': data[ActivationType.GLOBAL],
                    'new_both': data[ActivationType.BOTH],
                })


def run_different_r_experiment(local_gen_func: Callable[[int], nk.Graph], global_gen_func: Callable[[int, float], nk.Graph], name: str = "different_r"):
    """Runs the experiment for only the local graph, and then different values of r"""

    n = 10 ** 6
    k = 20 * math.log(n)
    r_vals = [1, 2, 3, 5, 10, 20, 30, 50, 100]

    print("Generating the local graph...")
    g_local = local_gen_func(n)
    print("Generating the global graph...")
    g_global = global_gen_func(n, k)
    m = g_global.numberOfEdges()
    avg_k = 2*m/n
    print(f"Global graph: expected avg. deg {k}, got {avg_k}")

    with open(f"outputs/{name}.csv", 'w') as csvfile:
        fieldnames = ['graph', 'round', 'active', 'new',
                      'new_local', 'new_global', 'new_both']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        print("Running on local graph only...")
        # Only local graph
        initially_active = random.randrange(n)
        new_activations, total_activations = run_bootstrap_percolation(g_local, 1, [
                                                                       initially_active])

        for cur_round, data in enumerate(new_activations):
            writer.writerow({
                'graph': 'local_only',
                'round': cur_round,
                'active': total_activations[cur_round],
                'new': sum(data.values()),
                'new_local': data[ActivationType.LOCAL],
                'new_global': data[ActivationType.GLOBAL],
                'new_both': data[ActivationType.BOTH],
            })

        for r in r_vals:
            print(f"Running on r={r}...")
            initially_active = random.randrange(n)
            new_activations, total_activations = run_perturbed_percolation(
                g_local, g_global, r, initially_active)
            for cur_round, data in enumerate(new_activations):
                writer.writerow({
                    'graph': f"r={r}",
                    'round': cur_round,
                    'active': total_activations[cur_round],
                    'new': sum(data.values()),
                    'new_local': data[ActivationType.LOCAL],
                    'new_global': data[ActivationType.GLOBAL],
                    'new_both': data[ActivationType.BOTH],
                })


def run_girg_different_beta_experiment(base_gen_func: Callable[[int], nk.Graph], name: str = "girg_different_beta"):
    """Runs the experiment for a fixed r with the given base graph, and then different GIRG with differing beta values"""

    n = 10 ** 6
    k = 20 * math.log(n)
    r = 30
    T = 0.01

    beta_vals = [2.1, 2.5, 2.7, 3.0, 3.5, 4.0, 6.0, 10.0]

    print("Generating the base graph...")
    g_base = base_gen_func(n)

    with open(f"outputs/{name}.csv", 'w') as csvfile:
        fieldnames = ['graph', 'beta', 'r', 'round',
                      'active', 'new', 'new_local', 'new_global', 'new_both']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for beta in beta_vals:
            print(f"Running on beta={beta}...")
            print("Generating the random graph...")
            g_random = generate_girg(n, k, beta, T)
            m = g_random.numberOfEdges()
            avg_k = 2*m/n
            print(f"Random graph: expected avg. deg {k}, got {avg_k}")
            initially_active = random.randrange(n)
            new_activations, total_activations = run_perturbed_percolation(
                g_base, g_random, r, initially_active)
            for cur_round, data in enumerate(new_activations):
                writer.writerow({
                    'graph': f"beta={beta}",
                    'beta': beta,
                    'r': r,
                    'round': cur_round,
                    'active': total_activations[cur_round],
                    'new': sum(data.values()),
                    'new_local': data[ActivationType.LOCAL],
                    'new_global': data[ActivationType.GLOBAL],
                    'new_both': data[ActivationType.BOTH],
                })


def run_girg_different_t_experiment(base_gen_func: Callable[[int], nk.Graph], name: str = "girg_different_t"):
    """Runs the experiment for a fixed r with the given base graph, and then different GIRG with differing temperature values"""

    n = 10 ** 6
    k = 20 * math.log(n)
    r = 30
    beta = 6.0

    T_vals = [0.01, 0.2, 0.4, 0.6, 0.7, 0.8, 0.9, 0.95, 0.99]

    print("Generating the base graph...")
    g_base = base_gen_func(n)

    with open(f"outputs/{name}.csv", 'w') as csvfile:
        fieldnames = ['graph', 't', 'r', 'round',
                      'active', 'new', 'new_local', 'new_global', 'new_both']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for T in T_vals:
            print(f"Running on T={T}...")
            print("Generating the random graph...")
            g_random = generate_girg(n, k, beta, T)
            m = g_random.numberOfEdges()
            avg_k = 2*m/n
            print(f"Random graph: expected avg. deg {k}, got {avg_k}")
            initially_active = random.randrange(n)
            new_activations, total_activations = run_perturbed_percolation(
                g_base, g_random, r, initially_active)
            for cur_round, data in enumerate(new_activations):
                writer.writerow({
                    'graph': f"T={T}",
                    't': T,
                    'r': r,
                    'round': cur_round,
                    'active': total_activations[cur_round],
                    'new': sum(data.values()),
                    'new_local': data[ActivationType.LOCAL],
                    'new_global': data[ActivationType.GLOBAL],
                    'new_both': data[ActivationType.BOTH],
                })


def run_cl_different_beta_experiment(base_gen_func: Callable[[int], nk.Graph], name: str = "cl_different_beta"):
    """Runs the experiment for a fixed r with the given base graph, and then different CL with differing beta values"""

    n = 10 ** 6
    k = 20 * math.log(n)
    r = 30

    beta_vals = [2.1, 2.5, 2.7, 3.0, 3.5, 4.0, 6.0, 10.0]

    print("Generating the base graph...")
    g_base = base_gen_func(n)

    with open(f"outputs/{name}.csv", 'w') as csvfile:
        fieldnames = ['graph', 'beta', 'r', 'round',
                      'active', 'new', 'new_local', 'new_global', 'new_both']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for beta in beta_vals:
            print(f"Running on beta={beta}...")
            print("Generating the random graph...")
            g_random = generate_chung_lu_pl(n, k, beta)
            m = g_random.numberOfEdges()
            avg_k = 2*m/n
            print(f"Random graph: expected avg. deg {k}, got {avg_k}")
            initially_active = random.randrange(n)
            new_activations, total_activations = run_perturbed_percolation(
                g_base, g_random, r, initially_active)
            for cur_round, data in enumerate(new_activations):
                writer.writerow({
                    'graph': f"beta={beta}",
                    'beta': beta,
                    'r': r,
                    'round': cur_round,
                    'active': total_activations[cur_round],
                    'new': sum(data.values()),
                    'new_local': data[ActivationType.LOCAL],
                    'new_global': data[ActivationType.GLOBAL],
                    'new_both': data[ActivationType.BOTH],
                })


def run_graph_sizes_experiment():
    """Calculates the number of nodes, number of edges, and average degree for all real-world graphs"""
    local_names = ["inf-roadNet-PA", "inf-roadNet-CA", "inf-italy-osm"]
    global_names = ["soc-google-plus", "soc-twitter-follows",
                    "soc-delicious", "soc-youtube"]

    for name in local_names + global_names:

        source = str(Path(f"inputs/{name}.txt"))

        g = nk.graphio.EdgeListReader(' ', 1).read(source)
        if name in local_names:
            g = nk.components.ConnectedComponents.extractLargestConnectedComponent(
                g, compactGraph=True)
        n = g.numberOfNodes()
        m = g.numberOfEdges()
        k = 2 * m / n
        print(f"Graph {name}:\t\t\t{n=}, {m=}, {k=}")
        # print(f"{name} & {n} & {m} & {k}")
