library(tikzDevice)
library(ggplot2)
library(reshape2)
library(scales)

source("R/helpers.R")

rounds_girg <- read.csv("outputs/different_r_girg.csv")
rounds_girg$model <- "GIRG"
rounds_cl <- read.csv("outputs/different_r_cl.csv")
rounds_cl$model <- "Chung-Lu with PL"

rounds <- rbind(rounds_girg, rounds_cl)

rounds$graph <- factor(rounds$graph, levels = c("local_only", "r=1", "r=2", "r=3", "r=5", "r=10", "r=20", "r=30", "r=50", "r=100"), labels = c("Local graph", "r = 1", "r = 2", "r = 3", "r = 5", "r = 10", "r = 20", "r = 30", "r = 50", "r = 100"))

plot <- ggplot(rounds, aes(x = round)) +
  theme(legend.title = element_blank(), legend.margin = margin(t = 0, unit = "cm")) +
  geom_line(aes(y = new, color = graph)) +
  xlab("Round") +
  ylab("Activations") +
  scale_y_log10(labels = label_number()) +
  scale_x_log10(labels = label_number()) +
  facet_grid(rows = vars(model))

create_pdf("plots/different_r_other.pdf", plot, height = 0.6)
