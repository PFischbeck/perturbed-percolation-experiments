library("ggplot2")
library("reshape2")
library("scales")

source("R/helpers.R")

tbl <- read.csv("outputs/real_world_perturbed_different_r.csv")
plot <- ggplot(data = melt(tbl, measure = c("new_local", "new_global", "new_both")), aes(x = round, y = value, fill = variable)) +
    geom_col() +
    facet_wrap(vars(r), labeller = label_bquote(cols = r == .(r))) +
    scale_fill_manual(values = c(yellow, blue, red), labels = c("Local", "Global", "Both")) +
    labs(x = "Round", y = "Activations", fill = "Activation Type") +
    # theme(legend.position = c(0.17, 0.88))
    theme(legend.position = "top") +
    scale_y_continuous(labels = label_number())

create_pdf("plots/perturbed_real_world_different_r.pdf", plot, height = 1.0)
