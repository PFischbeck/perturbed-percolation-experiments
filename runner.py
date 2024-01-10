import argparse
import math
import random

import networkit as nk

from experiments import run_bootstrap_on_real_world_experiment, run_cl_different_beta_experiment, run_different_r_experiment, run_girg_different_beta_experiment, run_girg_different_t_experiment, \
    run_graph_sizes_experiment, run_perturbed_on_real_world_experiment, \
    run_perturbed_on_real_world_different_r_experiment
from graph_generators import generate_chung_lu_pl, generate_er, generate_girg, generate_torus

if __name__ == "__main__":
    # Fix the random seeds

    # Fix networkit seed
    nk.engineering.setSeed(123, True)
    # Changing this number will also change the random number generation
    nk.engineering.setNumberOfThreads(1)
    # Fix python seed
    # igraph uses python for random number generation
    random.seed(123)

    parser = argparse.ArgumentParser()
    parser.add_argument('--experiment', type=str, required=True)
    args = parser.parse_args()

    experiment = args.experiment
    if experiment == 'rw_graph_sizes':
        run_graph_sizes_experiment()
    elif experiment == 'rw_bootstrap':
        run_bootstrap_on_real_world_experiment()
    elif experiment == 'rw_perturbed':
        run_perturbed_on_real_world_experiment()
    elif experiment == 'rw_perturbed_different_r':
        run_perturbed_on_real_world_different_r_experiment()
    elif experiment == 'different_r':
        run_different_r_experiment(generate_torus, generate_er, 'different_r')
    elif experiment == 'different_r_girg':
        def generate_fixed_girg(n, k):
            beta = 3.0
            T = 0.01
            return generate_girg(n, k, beta, T)
        run_different_r_experiment(
            generate_torus, generate_fixed_girg, 'different_r_girg')
    elif experiment == 'different_r_cl':
        run_different_r_experiment(
            generate_torus, generate_chung_lu_pl, 'different_r_cl'
        )
    elif experiment == 'girg_different_beta':
        run_girg_different_beta_experiment(
            generate_torus, 'girg_different_beta'
        )
    elif experiment == 'girg_different_t':
        run_girg_different_t_experiment(
            generate_torus, 'girg_different_t'
        )
    elif experiment == 'cl_different_beta':
        run_cl_different_beta_experiment(
            generate_torus, 'cl_different_beta'
        )
