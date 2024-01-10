library("ggplot2")
library("reshape2")

source("R/helpers.R")

tbl <- read.csv("outputs/real_world_perturbed.csv")
plot <- ggplot(data = melt(tbl, measure = c("new_local", "new_global", "new_both")), aes(x = round, y = value, fill = variable)) +
    geom_col() +
    facet_grid(rows = vars(global_graph), cols = vars(local_graph), scales = "free") +
    scale_fill_manual(values = c(yellow, blue, red), labels = c("Local", "Global", "Both")) +
    labs(x = "Round", y = "Activations", fill = "Activation Type") +
    theme(legend.position = "top") +
    scale_y_continuous(labels = label_number())

create_pdf("plots/perturbed_real_world_combinations.pdf", plot, height = 1.1)
