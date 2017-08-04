# Initialize Boilerplate ----
source("boilerplate.R")
source("data/comment.R")

InitGlobals()

## Yngve ====

### Query Data
dataset <- GetCommentYngve()

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
  scale_fill_manual(values = FILLCOLORS) +
  facet_wrap(~ variable, nrow = 1, scales = "free",
             labeller = as_labeller(COMMENT.METRIC.LABELS)) +
  labs(title = title, x = "Comment Type", y = metric) +
  GetTheme() +
  theme(legend.position = "none")

## Frazier ====

### Query Data
dataset <- GetCommentFrazier()

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
  scale_fill_manual(values = FILLCOLORS) +
  facet_wrap(~ variable, nrow = 1, scales = "free",
             labeller = as_labeller(COMMENT.METRIC.LABELS)) +
  labs(title = title, x = "Comment Type", y = metric) +
  GetTheme() +
  theme(legend.position = "none")

## Propositional Density ====

### Query Data
dataset <- GetCommentPdensity()

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
  scale_fill_manual(values = FILLCOLORS) +
  facet_wrap(~ variable, nrow = 1, scales = "free",
             labeller = as_labeller(COMMENT.METRIC.LABELS)) +
  labs(title = title, x = "Comment Type", y = metric) +
  GetTheme() +
  theme(legend.position = "none")

## Content Density ====

### Query Data
dataset <- GetCommentCdensity()

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
  scale_fill_manual(values = FILLCOLORS) +
  facet_wrap(~ variable, nrow = 1, scales = "free",
             labeller = as_labeller(COMMENT.METRIC.LABELS)) +
  labs(title = title, x = "Comment Type", y = metric) +
  GetTheme() +
  theme(legend.position = "none")

## Sentiment ====

### Query Data
dataset <- GetCommentSentiment()

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
  scale_fill_manual(values = FILLCOLORS) +
  facet_wrap(~ variable, nrow = 1, scales = "free",
             labeller = as_labeller(COMMENT.METRIC.LABELS)) +
  labs(title = title, x = "Comment Type", y = metric) +
  GetTheme() +
  theme(legend.position = "none")

## Uncertainty ====

### Query Data
dataset <- GetCommentUncertainty()

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
  scale_fill_manual(values = FILLCOLORS) +
  facet_wrap(~ variable, nrow = 1, scales = "free",
             labeller = as_labeller(COMMENT.METRIC.LABELS)) +
  labs(title = title, x = "Comment Type", y = metric) +
  GetTheme() +
  theme(legend.position = "none")

## Politeness ====

### Query Data
dataset <- GetCommentPoliteness()

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
  scale_fill_manual(values = FILLCOLORS) +
  facet_wrap(~ variable, nrow = 1, scales = "free",
             labeller = as_labeller(COMMENT.METRIC.LABELS)) +
  labs(title = title, x = "Comment Type", y = metric) +
  GetTheme() +
  theme(legend.position = "none")

## Formality ====

### Query Data
dataset <- GetCommentFormality()

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
  scale_fill_manual(values = FILLCOLORS) +
  facet_wrap(~ variable, nrow = 1, scales = "free",
             labeller = as_labeller(COMMENT.METRIC.LABELS)) +
  labs(title = title, x = "Comment Type", y = metric) +
  GetTheme() +
  theme(legend.position = "none")

## Informativeness ====

### Query Data
dataset <- GetCommentInformativeness()

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
  scale_fill_manual(values = FILLCOLORS) +
  facet_wrap(~ variable, nrow = 1, scales = "free",
             labeller = as_labeller(COMMENT.METRIC.LABELS)) +
  labs(title = title, x = "Comment Type", y = metric) +
  GetTheme() +
  theme(legend.position = "none")

## Implicature ====

### Query Data
dataset <- GetCommentImplicature()

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
  scale_fill_manual(values = FILLCOLORS) +
  facet_wrap(~ variable, nrow = 1, scales = "free",
             labeller = as_labeller(COMMENT.METRIC.LABELS)) +
  labs(title = title, x = "Comment Type", y = metric) +
  GetTheme() +
  theme(legend.position = "none")


## Project Experience ====

### Query Data
dataset <- GetProjectExperience()

### Plot
metric <- "Project Experience (Sqrt Scale)"
title <- "Distribution of Project Experience"

plot.dataset <- dataset %>%
  inner_join(., COMMENT.TYPE, by = "comment_id") %>%
  select(-comment_id) %>%
  melt(., id.vars = c("type"))

# Resolution: 500 x 400
ggplot(plot.dataset, aes(x = type, y = value, fill = type)) +
  geom_boxplot() +
  scale_x_discrete(labels = COMMENT.TYPE.LABELS) +
  scale_y_sqrt() +
  scale_fill_manual(values = FILLCOLORS) +
  facet_wrap(~ variable, nrow = 1, scales = "free",
             labeller = as_labeller(COMMENT.METRIC.LABELS)) +
  labs(title = title, x = "Comment Type", y = metric) +
  GetTheme() +
  theme(legend.position = "none")

## Module Experience ====

### Query Data
dataset <- GetModuleExperience()

### Plot
metric <- "Module Experience"
title <- "Distribution of Module Experience"

plot.dataset <- dataset %>%
  inner_join(., COMMENT.TYPE, by = "comment_id") %>%
  select(-comment_id) %>%
  melt(., id.vars = c("type"))

# Resolution: 500 x 400
ggplot(plot.dataset, aes(x = type, y = value, fill = type)) +
  geom_boxplot() +
  scale_x_discrete(labels = COMMENT.TYPE.LABELS) +
  scale_fill_manual(values = FILLCOLORS) +
  facet_wrap(~ variable, nrow = 1, scales = "free",
             labeller = as_labeller(COMMENT.METRIC.LABELS)) +
  labs(title = title, x = "Comment Type", y = metric) +
  GetTheme() +
  theme(legend.position = "none")

## File Experience ====

### Query Data
dataset <- GetFileExperience()

### Plot
metric <- "File Experience"
title <- "Distribution of File Experience"

plot.dataset <- dataset %>%
  inner_join(., COMMENT.TYPE, by = "comment_id") %>%
  select(-comment_id) %>%
  melt(., id.vars = c("type"))

# Resolution: 500 x 400
ggplot(plot.dataset, aes(x = type, y = value, fill = type)) +
  geom_boxplot() +
  scale_x_discrete(labels = COMMENT.TYPE.LABELS) +
  scale_fill_manual(values = FILLCOLORS) +
  facet_wrap(~ variable, nrow = 1, scales = "free",
             labeller = as_labeller(COMMENT.METRIC.LABELS)) +
  labs(title = title, x = "Comment Type", y = metric) +
  GetTheme() +
  theme(legend.position = "none")

## Bug Familiarity ====

### Query Data
dataset <- GetBugFamiliarity()

### Plot
metric <- "Bug Familiarity"
title <- "Distribution of Bug Familiarity"

interim.dataset <- dataset %>%
  inner_join(., COMMENT.TYPE, by = "comment_id") %>%
  select(-comment_id)

alpha.dataset <- interim.dataset %>%
  group_by(type, is_bugfamiliar) %>%
  summarize(alpha_num_comments = n())

beta.dataset <- interim.dataset %>%
  group_by(type) %>%
  summarize(beta_num_comments = n())

plot.dataset <- inner_join(alpha.dataset, beta.dataset, by = "type") %>%
  mutate(pct_comments = alpha_num_comments / beta_num_comments) %>%
  select(type, is_bugfamiliar, pct_comments)

# Resolution: 500 x 400
ggplot(plot.dataset, aes(x = type, y = pct_comments, fill = is_bugfamiliar)) +
  geom_bar(stat = "identity", position = "dodge") +
  geom_text(aes(label = scales::percent(pct_comments)), vjust = "inward",
            position = position_dodge(width=0.9)) +
  scale_x_discrete(labels = COMMENT.TYPE.LABELS) +
  scale_y_continuous(labels = scales::percent) +
  scale_fill_manual(name = "Comment Type", values = FILLCOLORS,
                    labels = COMMENT.METRIC.LABELS) +
  labs(title = title, x = metric, y = "% Comments") +
  GetTheme()

## Number of Sentences ====

### Query Data
dataset <- GetCommentLength()

### Plot
metric <- "# Sentences (Log Scale)"
title <- "Distribution of Number of Sentences"

plot.dataset <- dataset %>%
  inner_join(., COMMENT.TYPE, by = "comment_id") %>%
  select(-comment_id) %>%
  melt(., id.vars = c("type"))

# Resolution: 500 x 400
ggplot(plot.dataset, aes(x = type, y = value, fill = type)) +
  geom_boxplot() +
  scale_x_discrete(labels = COMMENT.TYPE.LABELS) +
  scale_y_log10() +
  scale_fill_manual(values = FILLCOLORS) +
  facet_wrap(~ variable, nrow = 1, scales = "free",
             labeller = as_labeller(COMMENT.METRIC.LABELS)) +
  labs(title = title, x = "Comment Type", y = metric) +
  GetTheme() +
  theme(legend.position = "none")
