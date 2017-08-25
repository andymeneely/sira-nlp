# Initialize Boilerplate ----
source("boilerplate.R")
source("data/comment.R")

## Continuous Valued Metrics ====

### Query Data ####
dataset <- GetCommentContinuousMetrics(normalize = F)

### Plot: Spearman's Correlation Coefficient ####
title <- "Correlation among Continuous-valued Comment Metrics"

plot.dataset <- GetCorrelation(dataset, ignore = COMMENT.KEYS)

# Resolution: 800 x 800
ggplot(plot.dataset, aes(Var2, Var1, fill = value)) +
  geom_tile() +
  geom_text(
    aes(
      Var2, Var1,
      label = ifelse(value == 0, sprintf("-"), sprintf("%.2f", value))
    ),
    color = "black", size = 4
  ) +
  scale_x_discrete(labels = COMMENT.METRIC.LABELS) +
  scale_y_discrete(labels = COMMENT.METRIC.LABELS) +
  scale_fill_gradient2(low = "#636363", high = "#636363", mid = "#f0f0f0",
                       midpoint = 0, limit = c(-1,1)) +
  guides(fill = guide_colorbar(barwidth = 10, barheight = 0.5,
                               title = expression(paste("Spearman's ", rho)),
                               title.position = "top", title.hjust = 0.5)) +
  coord_fixed() +
  labs(title = title, x = NULL, y = NULL) +
  GetTheme() +
  theme(panel.grid.major = element_blank(), panel.border = element_blank(),
        panel.background = element_blank(), axis.ticks = element_blank())
