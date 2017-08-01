# Initialize Boilerplate ----
source("boilerplate.R")
source("data/comment.R")

InitGlobals()

## Yngve ====

### Query Data
dataset <- GetYngve(normalize = F)

### Plot
metric <- "Comment Yngve (Log Scale)"
title <- "Distribution of Comment Yngve"

plot.dataset <- dataset %>%
  inner_join(., COMMENT.TYPE, by = "comment_id") %>%
  select(-comment_id) %>%
  melt(., id.vars = c("type"))

# Resolution: 1000 x 400
ggplot(plot.dataset, aes(x = type, y = value, fill = type)) +
  geom_boxplot() +
  scale_x_discrete(labels = COMMENT.TYPE.LABELS) +
  scale_y_log10() +
  scale_fill_manual(values = COMMENT.TYPE.FILLCOLORS) +
  facet_wrap(~ variable, nrow = 1, scales = "free",
             labeller = as_labeller(COMMENT.METRIC.LABELS)) +
  labs(title = title, x = "Comment Type", y = metric) +
  GetTheme() +
  theme(legend.position = "none")

## Frazier ====

### Query Data
dataset <- GetFrazier(normalize = F)

### Plot
metric <- "Comment Frazier"
title <- "Distribution of Comment Frazier"

plot.dataset <- dataset %>%
  inner_join(., COMMENT.TYPE, by = "comment_id") %>%
  select(-comment_id) %>%
  melt(., id.vars = c("type"))

# Resolution: 1000 x 400
ggplot(plot.dataset, aes(x = type, y = value, fill = type)) +
  geom_boxplot() +
  scale_x_discrete(labels = COMMENT.TYPE.LABELS) +
  scale_fill_manual(values = COMMENT.TYPE.FILLCOLORS) +
  facet_wrap(~ variable, nrow = 1, scales = "free",
             labeller = as_labeller(COMMENT.METRIC.LABELS)) +
  labs(title = title, x = "Comment Type", y = metric) +
  GetTheme() +
  theme(legend.position = "none")

## Propositional Density ====

### Query Data
dataset <- GetPdensity(normalize = F)

### Plot
metric <- "Comment Propositional Density"
title <- "Distribution of Propositional Density"

plot.dataset <- dataset %>%
  inner_join(., COMMENT.TYPE, by = "comment_id") %>%
  select(-comment_id) %>%
  melt(., id.vars = c("type"))

# Resolution: 1000 x 400
ggplot(plot.dataset, aes(x = type, y = value, fill = type)) +
  geom_boxplot() +
  scale_x_discrete(labels = COMMENT.TYPE.LABELS) +
  scale_fill_manual(values = COMMENT.TYPE.FILLCOLORS) +
  facet_wrap(~ variable, nrow = 1, scales = "free",
             labeller = as_labeller(COMMENT.METRIC.LABELS)) +
  labs(title = title, x = "Comment Type", y = metric) +
  GetTheme() +
  theme(legend.position = "none")

## Content Density ====

### Query Data
dataset <- GetCdensity(normalize = F)

### Plot
metric <- "Comment Content Density (Sqrt Scale)"
title <- "Distribution of Content Density"

plot.dataset <- dataset %>%
  inner_join(., COMMENT.TYPE, by = "comment_id") %>%
  select(-comment_id) %>%
  melt(., id.vars = c("type"))

# Resolution: 1000 x 400
ggplot(plot.dataset, aes(x = type, y = value, fill = type)) +
  geom_boxplot() +
  scale_x_discrete(labels = COMMENT.TYPE.LABELS) +
  scale_y_sqrt() +
  scale_fill_manual(values = COMMENT.TYPE.FILLCOLORS) +
  facet_wrap(~ variable, nrow = 1, scales = "free",
             labeller = as_labeller(COMMENT.METRIC.LABELS)) +
  labs(title = title, x = "Comment Type", y = metric) +
  GetTheme() +
  theme(legend.position = "none")

## Sentiment ====

### Query Data
dataset <- GetSentiment(normalize = F)

### Plot
metric <- "Comment Sentiment"
title <- "Distribution of Comment Sentiment"

plot.dataset <- dataset %>%
  inner_join(., COMMENT.TYPE, by = "comment_id") %>%
  select(-comment_id) %>%
  melt(., id.vars = c("type"))

# Resolution: 750 x 400
ggplot(plot.dataset, aes(x = type, y = value, fill = type)) +
  geom_boxplot() +
  scale_x_discrete(labels = COMMENT.TYPE.LABELS) +
  scale_fill_manual(values = COMMENT.TYPE.FILLCOLORS) +
  facet_wrap(~ variable, nrow = 1, scales = "free",
             labeller = as_labeller(COMMENT.METRIC.LABELS)) +
  labs(title = title, x = "Comment Type", y = metric) +
  GetTheme() +
  theme(legend.position = "none")

## Uncertainty ====

### Query Data
dataset <- GetUncertainty(normalize = F)

### Plot
metric <- "Comment Uncertainty (Log Scale)"
title <- "Distribution of Comment Uncertainty"

plot.dataset <- dataset %>%
  inner_join(., COMMENT.TYPE, by = "comment_id") %>%
  select(-comment_id) %>%
  melt(., id.vars = c("type"))

# Resolution: 1000 x 400
ggplot(plot.dataset, aes(x = type, y = value, fill = type)) +
  geom_boxplot() +
  scale_x_discrete(labels = COMMENT.TYPE.LABELS) +
  scale_y_log10() +
  scale_fill_manual(values = COMMENT.TYPE.FILLCOLORS) +
  facet_wrap(~ variable, nrow = 1, scales = "free",
             labeller = as_labeller(COMMENT.METRIC.LABELS)) +
  labs(title = title, x = "Comment Type", y = metric) +
  GetTheme() +
  theme(legend.position = "none")

## Politeness ====

### Query Data
dataset <- GetPoliteness(normalize = F)

### Plot
metric <- "Comment Politeness"
title <- "Distribution of Comment Politeness"

plot.dataset <- dataset %>%
  inner_join(., COMMENT.TYPE, by = "comment_id") %>%
  select(-comment_id) %>%
  melt(., id.vars = c("type"))

# Resolution: 1000 x 400
ggplot(plot.dataset, aes(x = type, y = value, fill = type)) +
  geom_boxplot() +
  scale_x_discrete(labels = COMMENT.TYPE.LABELS) +
  scale_fill_manual(values = COMMENT.TYPE.FILLCOLORS) +
  facet_wrap(~ variable, nrow = 1, scales = "free",
             labeller = as_labeller(COMMENT.METRIC.LABELS)) +
  labs(title = title, x = "Comment Type", y = metric) +
  GetTheme() +
  theme(legend.position = "none")

## Formality ====

### Query Data
dataset <- GetFormality(normalize = F)

### Plot
metric <- "Comment Formality"
title <- "Distribution of Comment Formality"

plot.dataset <- dataset %>%
  inner_join(., COMMENT.TYPE, by = "comment_id") %>%
  select(-comment_id) %>%
  melt(., id.vars = c("type"))

# Resolution: 1000 x 400
ggplot(plot.dataset, aes(x = type, y = value, fill = type)) +
  geom_boxplot() +
  scale_x_discrete(labels = COMMENT.TYPE.LABELS) +
  scale_fill_manual(values = COMMENT.TYPE.FILLCOLORS) +
  facet_wrap(~ variable, nrow = 1, scales = "free",
             labeller = as_labeller(COMMENT.METRIC.LABELS)) +
  labs(title = title, x = "Comment Type", y = metric) +
  GetTheme() +
  theme(legend.position = "none")

## Informativeness ====

### Query Data
dataset <- GetInformativeness(normalize = F)

### Plot
metric <- "Comment Informativeness"
title <- "Distribution of Comment Informativeness"

plot.dataset <- dataset %>%
  inner_join(., COMMENT.TYPE, by = "comment_id") %>%
  select(-comment_id) %>%
  melt(., id.vars = c("type"))

# Resolution: 1000 x 400
ggplot(plot.dataset, aes(x = type, y = value, fill = type)) +
  geom_boxplot() +
  scale_x_discrete(labels = COMMENT.TYPE.LABELS) +
  scale_fill_manual(values = COMMENT.TYPE.FILLCOLORS) +
  facet_wrap(~ variable, nrow = 1, scales = "free",
             labeller = as_labeller(COMMENT.METRIC.LABELS)) +
  labs(title = title, x = "Comment Type", y = metric) +
  GetTheme() +
  theme(legend.position = "none")

## Implicature ====

### Query Data
dataset <- GetImplicature(normalize = F)

### Plot
metric <- "Comment Implicature"
title <- "Distribution of Comment Implicature"

plot.dataset <- dataset %>%
  inner_join(., COMMENT.TYPE, by = "comment_id") %>%
  select(-comment_id) %>%
  melt(., id.vars = c("type"))

# Resolution: 1000 x 400
ggplot(plot.dataset, aes(x = type, y = value, fill = type)) +
  geom_boxplot() +
  scale_x_discrete(labels = COMMENT.TYPE.LABELS) +
  scale_fill_manual(values = COMMENT.TYPE.FILLCOLORS) +
  facet_wrap(~ variable, nrow = 1, scales = "free",
             labeller = as_labeller(COMMENT.METRIC.LABELS)) +
  labs(title = title, x = "Comment Type", y = metric) +
  GetTheme() +
  theme(legend.position = "none")
