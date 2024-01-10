library(tikzDevice)
library(ggplot2)
library(reshape2)

source("R/helpers.R")

rounds_girg <- read.csv("outputs/girg_different_beta.csv")
rounds_girg$model <- "GIRG"
rounds_cl <- read.csv("outputs/cl_different_beta.csv")
rounds_cl$model <- "Chung-Lu with PL"

rounds <- rbind(rounds_girg, rounds_cl)

plot <- ggplot(rounds, aes(x = round)) +
  # theme(legend.margin = margin(t = 0, unit = "cm")) +
  geom_line(aes(y = new, color = factor(beta))) +
  xlab("Round") +
  ylab("Activations") +
  scale_y_log10(labels = label_number()) +
  scale_x_log10(labels = label_number()) +
  facet_grid(rows = vars(model)) +
  labs(color = "Beta")

create_pdf("plots/different_beta.pdf", plot, height = 0.6)
