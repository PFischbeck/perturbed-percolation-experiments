library(tikzDevice)
library(ggplot2)
library(dplyr)
library(ggrepel)
library(reshape2)
library(scales)

source("R/helpers.R")

rounds <- read.csv("outputs/different_r.csv")

rounds$graph <- factor(rounds$graph, levels = c("local_only", "r=1", "r=2", "r=3", "r=5", "r=10", "r=20", "r=30", "r=50", "r=100"), labels = c("Local graph", "r = 1", "2", "3", "5", "10", "20", "30", "50", "100"))

last_vals <- rounds %>%
  group_by(graph) %>%
  slice(which.max(round) - 2)

plot <- ggplot(rounds, aes(x = round, y = new)) +
  theme(legend.position = "none") +
  geom_line(aes(color = graph)) +
  xlab("Round") +
  ylab("Activations") +
  scale_y_log10(labels = label_number()) +
  scale_x_log10(labels = label_number()) +
  geom_label_repel(aes(label = graph), data = last_vals, size = 3, direction = "y", min.segment.length = 10)

create_pdf("plots/different_r.pdf", plot, height = 0.6)
