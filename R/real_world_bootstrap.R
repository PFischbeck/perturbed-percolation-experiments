library(tikzDevice)
library(ggplot2)
library(dplyr)
library(ggrepel)
library(reshape2)

source("R/helpers.R")

rounds <- read.csv("outputs/real_world_bootstrap.csv")

last_vals <- rounds %>%
    group_by(local_graph, trial) %>%
    summarise(rounds = max(round), max_new = max(new)) %>%
    group_by(local_graph) %>%
    summarise(min_rounds = min(rounds), max_new = max(max_new))

last_vals
