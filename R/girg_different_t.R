library(tikzDevice)
library(ggplot2)
library(reshape2)

source("R/helpers.R")

rounds <- read.csv("outputs/girg_different_t.csv")

plot <- ggplot(rounds, aes(x = round)) +
  # theme(legend.title = element_blank(), legend.margin = margin(t = 0, unit = "cm")) +
  geom_line(aes(y = new, color = factor(t))) +
  xlab("Round") +
  ylab("Activations") +
  scale_y_log10(labels = label_number()) +
  scale_x_log10(labels = label_number()) +
  labs(color = "Temperature")

create_pdf("plots/girg_different_t.pdf", plot, height = 0.6)
