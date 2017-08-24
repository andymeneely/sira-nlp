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

# Render
png("diagrams/comment.yngve.png", width = 500, height = 400)
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
dev.off()

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

# Render
png("diagrams/comment.frazier.png", width = 500, height = 400)
ggplot(plot.dataset, aes(x = type, y = value, fill = type)) +
  geom_boxplot() +
  scale_x_discrete(labels = COMMENT.TYPE.LABELS) +
  scale_fill_manual(values = FILLCOLORS) +
  facet_wrap(~ variable, nrow = 1, scales = "free",
             labeller = as_labeller(COMMENT.METRIC.LABELS)) +
  labs(title = title, x = "Comment Type", y = metric) +
  GetTheme() +
  theme(legend.position = "none")
dev.off()

## Propositional Density ====

### Query Data
dataset <- GetCommentPdensity()

### Plot
metric <- "Comment p-density"
title <- "Distribution of Comment p-density"

plot.dataset <- dataset %>%
  inner_join(., COMMENT.TYPE, by = "comment_id") %>%
  select(-comment_id) %>%
  melt(., id.vars = c("type"))

# Render
png("diagrams/comment.pdensity.png", width = 500, height = 400)
ggplot(plot.dataset, aes(x = type, y = value, fill = type)) +
  geom_boxplot() +
  scale_x_discrete(labels = COMMENT.TYPE.LABELS) +
  scale_fill_manual(values = FILLCOLORS) +
  facet_wrap(~ variable, nrow = 1, scales = "free",
             labeller = as_labeller(COMMENT.METRIC.LABELS)) +
  labs(title = title, x = "Comment Type", y = metric) +
  GetTheme() +
  theme(legend.position = "none")
dev.off()

## Content Density ====

### Query Data
dataset <- GetCommentCdensity()

### Plot
metric <- "Comment c-density (Sqrt Scale)"
title <- "Distribution of Comment c-density"

plot.dataset <- dataset %>%
  inner_join(., COMMENT.TYPE, by = "comment_id") %>%
  select(-comment_id) %>%
  melt(., id.vars = c("type"))

# Render
png("diagrams/comment.cdensity.png", width = 500, height = 400)
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
dev.off()

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

# Render
png("diagrams/comment.sentiment.png", width = , height = )
ggplot(plot.dataset, aes(x = type, y = value, fill = type)) +
  geom_boxplot() +
  scale_x_discrete(labels = COMMENT.TYPE.LABELS) +
  scale_y_continuous(labels = scales::percent) +
  scale_fill_manual(values = FILLCOLORS) +
  facet_wrap(~ variable, nrow = 1, scales = "free",
             labeller = as_labeller(COMMENT.METRIC.LABELS)) +
  labs(title = title, x = "Comment Type", y = metric) +
  GetTheme() +
  theme(legend.position = "none")
dev.off()

## Uncertainty ====

### Query Data
dataset <- GetCommentUncertainty()

### Plot
metric <- "% Comments"
title <- "Distribution of Comment Uncertainty"

interim.dataset <- dataset %>%
  inner_join(., COMMENT.TYPE, by = "comment_id") %>%
  select(-comment_id)

alpha.dataset <- interim.dataset %>%
  filter(has_doxastic == T) %>%
  group_by(type, has_doxastic) %>%
  summarize(num_doxastic = n()) %>%
  select(type, num_doxastic)
alpha.dataset <- interim.dataset %>%
  filter(has_epistemic == T) %>%
  group_by(type, has_epistemic) %>%
  summarize(num_epistemic = n()) %>%
  select(type, num_epistemic) %>%
  inner_join(., alpha.dataset, by = "type")
alpha.dataset <- interim.dataset %>%
  filter(has_conditional == T) %>%
  group_by(type, has_conditional) %>%
  summarize(num_conditional = n()) %>%
  select(type, num_conditional) %>%
  inner_join(., alpha.dataset, by = "type")
alpha.dataset <- interim.dataset %>%
  filter(has_investigative == T) %>%
  group_by(type, has_investigative) %>%
  summarize(num_investigative = n()) %>%
  select(type, num_investigative) %>%
  inner_join(., alpha.dataset, by = "type")
alpha.dataset <- interim.dataset %>%
  filter(has_uncertainty == T) %>%
  group_by(type, has_uncertainty) %>%
  summarize(num_uncertain = n()) %>%
  select(type, num_uncertain) %>%
  inner_join(., alpha.dataset, by = "type")

beta.dataset <- interim.dataset %>%
  group_by(type) %>%
  summarise(num_comments = n())

plot.dataset <- inner_join(alpha.dataset, beta.dataset, by = "type") %>%
  mutate(has_doxastic = num_doxastic / num_comments) %>%
  mutate(has_epistemic = num_epistemic / num_comments) %>%
  mutate(has_conditional = num_conditional / num_comments) %>%
  mutate(has_investigative = num_investigative / num_comments) %>%
  mutate(has_uncertainty = num_uncertain / num_comments) %>%
  select(type, has_doxastic, has_epistemic, has_conditional, has_investigative,
         has_uncertainty) %>%
  melt(., id.vars = c("type"))

# Render
png("diagrams/comment.uncertainty.png", width = 800, height = 600)
ggplot(plot.dataset, aes(x = type, y = value, fill = variable)) +
  geom_bar(stat = "identity", position = "dodge") +
  geom_text(aes(label = scales::percent(value)), vjust = "inward",
            position = position_dodge(width=0.9)) +
  scale_x_discrete(labels = COMMENT.TYPE.LABELS) +
  scale_y_continuous(labels = scales::percent) +
  scale_fill_manual(name = "Uncertainty", values = FILLCOLORS,
                    labels = COMMENT.METRIC.LABELS) +
  labs(title = title, x = "Comment Type", y = metric) +
  GetTheme()
dev.off()

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

# Render
png("diagrams/comment.politeness.png", width = , height = )
ggplot(plot.dataset, aes(x = type, y = value, fill = type)) +
  geom_boxplot() +
  scale_x_discrete(labels = COMMENT.TYPE.LABELS) +
  scale_fill_manual(values = FILLCOLORS) +
  facet_wrap(~ variable, nrow = 1, scales = "free",
             labeller = as_labeller(COMMENT.METRIC.LABELS)) +
  labs(title = title, x = "Comment Type", y = metric) +
  GetTheme() +
  theme(legend.position = "none")
dev.off()

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

# Render
png("diagrams/comment.formality.png", width = , height = )
ggplot(plot.dataset, aes(x = type, y = value, fill = type)) +
  geom_boxplot() +
  scale_x_discrete(labels = COMMENT.TYPE.LABELS) +
  scale_fill_manual(values = FILLCOLORS) +
  facet_wrap(~ variable, nrow = 1, scales = "free",
             labeller = as_labeller(COMMENT.METRIC.LABELS)) +
  labs(title = title, x = "Comment Type", y = metric) +
  GetTheme() +
  theme(legend.position = "none")
dev.off()

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

# Render
png("diagrams/comment.informativeness.png", width = , height = )
ggplot(plot.dataset, aes(x = type, y = value, fill = type)) +
  geom_boxplot() +
  scale_x_discrete(labels = COMMENT.TYPE.LABELS) +
  scale_fill_manual(values = FILLCOLORS) +
  facet_wrap(~ variable, nrow = 1, scales = "free",
             labeller = as_labeller(COMMENT.METRIC.LABELS)) +
  labs(title = title, x = "Comment Type", y = metric) +
  GetTheme() +
  theme(legend.position = "none")
dev.off()

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

# Render
png("diagrams/comment.implicature.png", width = , height = )
ggplot(plot.dataset, aes(x = type, y = value, fill = type)) +
  geom_boxplot() +
  scale_x_discrete(labels = COMMENT.TYPE.LABELS) +
  scale_fill_manual(values = FILLCOLORS) +
  facet_wrap(~ variable, nrow = 1, scales = "free",
             labeller = as_labeller(COMMENT.METRIC.LABELS)) +
  labs(title = title, x = "Comment Type", y = metric) +
  GetTheme() +
  theme(legend.position = "none")
dev.off()


## Project Experience ====

### Query Data
dataset <- GetProjectExperience()

### Plot
metric <- "Project Experience (Sqrt Scale)"
title <- "Distribution of Project Experience"

plot.dataset <- dataset %>%
  inner_join(., COMMENT.TYPE, by = "comment_id") %>%
  select(-comment_id, -author) %>%
  melt(., id.vars = c("type"))

# Render
png("diagrams/comment.projectexperience.png", width = , height = )
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
dev.off()

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

# Render
png("diagrams/comment.moduleexperience.png", width = , height = )
ggplot(plot.dataset, aes(x = type, y = value, fill = type)) +
  geom_boxplot() +
  scale_x_discrete(labels = COMMENT.TYPE.LABELS) +
  scale_fill_manual(values = FILLCOLORS) +
  facet_wrap(~ variable, nrow = 1, scales = "free",
             labeller = as_labeller(COMMENT.METRIC.LABELS)) +
  labs(title = title, x = "Comment Type", y = metric) +
  GetTheme() +
  theme(legend.position = "none")
dev.off()

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

# Render
png("diagrams/comment.fileexperience.png", width = , height = )
ggplot(plot.dataset, aes(x = type, y = value, fill = type)) +
  geom_boxplot() +
  scale_x_discrete(labels = COMMENT.TYPE.LABELS) +
  scale_fill_manual(values = FILLCOLORS) +
  facet_wrap(~ variable, nrow = 1, scales = "free",
             labeller = as_labeller(COMMENT.METRIC.LABELS)) +
  labs(title = title, x = "Comment Type", y = metric) +
  GetTheme() +
  theme(legend.position = "none")
dev.off()

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

# Render
png("diagrams/comment.bugfamiliarity.png", width = , height = )
ggplot(plot.dataset, aes(x = type, y = pct_comments, fill = is_bugfamiliar)) +
  geom_bar(stat = "identity", position = "dodge") +
  geom_text(aes(label = scales::percent(pct_comments)), vjust = "inward",
            position = position_dodge(width=0.9)) +
  scale_x_discrete(labels = COMMENT.TYPE.LABELS) +
  scale_y_continuous(labels = scales::percent) +
  scale_fill_manual(name = metric, values = FILLCOLORS,
                    labels = COMMENT.METRIC.LABELS) +
  labs(title = title, x = "Comment Type", y = "% Comments") +
  GetTheme()
dev.off()

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

# Render
png("diagrams/comment.length.png", width = 500, height = 400)
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
dev.off()
