# Initialize Boilerplate ----
source("boilerplate.R")
source("data/sentence.R")

InitGlobals()

# Natural Language Metrics ----

## Yngve ====

### Query Data
dataset <- GetSentenceYngve()

### Plot
metric <- "Sentence Yngve (Log Scale)"
title <- "Distribution of Sentence Yngve"

plot.dataset <- dataset %>%
  inner_join(., COMMENT.TYPE, by = "comment_id") %>%
  select(-comment_id, -sentence_id) %>%
  melt(., id.vars = c("type"))

# Resolution: 500 x 400
ggplot(plot.dataset, aes(x = type, y = value, fill = type)) +
  geom_boxplot() +
  scale_x_discrete(labels = COMMENT.TYPE.LABELS) +
  scale_y_log10() +
  scale_fill_manual(values = FILLCOLORS) +
  facet_wrap(~ variable, nrow = 1, scales = "free",
             labeller = as_labeller(SENTENCE.METRIC.LABELS)) +
  labs(title = title, x = "Comment Type", y = metric) +
  GetTheme() +
  theme(legend.position = "none")

## Frazier ====

### Query Data
dataset <- GetSentenceFrazier()

### Plot
metric <- "Sentence Frazier"
title <- "Distribution of Sentence Frazier"

plot.dataset <- dataset %>%
  inner_join(., COMMENT.TYPE, by = "comment_id") %>%
  select(-comment_id, -sentence_id) %>%
  melt(., id.vars = c("type"))

# Resolution: 500 x 400
ggplot(plot.dataset, aes(x = type, y = value, fill = type)) +
  geom_boxplot() +
  scale_x_discrete(labels = COMMENT.TYPE.LABELS) +
  scale_fill_manual(values = FILLCOLORS) +
  facet_wrap(~ variable, nrow = 1, scales = "free",
             labeller = as_labeller(SENTENCE.METRIC.LABELS)) +
  labs(title = title, x = "Comment Type", y = metric) +
  GetTheme() +
  theme(legend.position = "none")

## Propositional Density ====

### Query Data
dataset <- GetSentencePdensity()

### Plot
metric <- "Sentence Propositional Density"
title <- "Distribution of Sentence Density"

plot.dataset <- dataset %>%
  inner_join(., COMMENT.TYPE, by = "comment_id") %>%
  select(-comment_id, -sentence_id) %>%
  melt(., id.vars = c("type"))

# Resolution: 500 x 400
ggplot(plot.dataset, aes(x = type, y = value, fill = type)) +
  geom_boxplot() +
  scale_x_discrete(labels = COMMENT.TYPE.LABELS) +
  scale_fill_manual(values = FILLCOLORS) +
  facet_wrap(~ variable, nrow = 1, scales = "free",
             labeller = as_labeller(SENTENCE.METRIC.LABELS)) +
  labs(title = title, x = "Comment Type", y = metric) +
  GetTheme() +
  theme(legend.position = "none")

## Content Density ====

### Query Data
dataset <- GetSentenceCdensity()

### Plot
metric <- "Sentence Content Density (Sqrt Scale)"
title <- "Distribution of Sentence Density"

plot.dataset <- dataset %>%
  inner_join(., COMMENT.TYPE, by = "comment_id") %>%
  select(-comment_id, -sentence_id) %>%
  melt(., id.vars = c("type"))

# Resolution: 500 x 400
ggplot(plot.dataset, aes(x = type, y = value, fill = type)) +
  geom_boxplot() +
  scale_x_discrete(labels = COMMENT.TYPE.LABELS) +
  scale_y_sqrt() +
  scale_fill_manual(values = FILLCOLORS) +
  facet_wrap(~ variable, nrow = 1, scales = "free",
             labeller = as_labeller(SENTENCE.METRIC.LABELS)) +
  labs(title = title, x = "Comment Type", y = metric) +
  GetTheme() +
  theme(legend.position = "none")

## Sentiment ====

### Query Data
dataset <- GetSentenceSentiment()

### Plot
metric <- "% Sentences"
title <- "Distribution of Sentiment in Sentences"

interim.dataset <- dataset %>%
  inner_join(., COMMENT.TYPE, by = "comment_id") %>%
  select(-comment_id, -sentence_id)

alpha.dataset <- interim.dataset %>%
  group_by(sentiment, type) %>%
  summarize(alpha_num_sentences = n())

beta.dataset <- interim.dataset %>%
  group_by(type) %>%
  summarize(beta_num_sentences = n())

plot.dataset <- inner_join(alpha.dataset, beta.dataset, by = "type") %>%
  mutate(pct_sentences = alpha_num_sentences / beta_num_sentences) %>%
  select(sentiment, type, pct_sentences)

# Resolution: 450 x 450
ggplot(plot.dataset, aes(x = type, y = pct_sentences, fill = sentiment)) +
  geom_bar(stat = "identity", position = "dodge") +
  geom_text(aes(label = scales::percent(pct_sentences)), vjust = "inward",
            position = position_dodge(width=0.9)) +
  scale_x_discrete(labels = COMMENT.TYPE.LABELS) +
  scale_y_continuous(labels = scales::percent) +
  scale_fill_manual(name = "Comment Type", values = FILLCOLORS,
                    labels = COMMENT.TYPE.LABELS) +
  labs(title = title, x = "Sentiment", y = metric) +
  GetTheme()

## Uncertainty ====

### Query Data
dataset <- GetSentenceUncertainty()

### Plot
metric <- "% Sentences"
title <- "Distribution of Uncertain Sentences"

interim.dataset <- dataset %>%
  inner_join(., COMMENT.TYPE, by = "comment_id") %>%
  select(-comment_id)

alpha.dataset <- interim.dataset %>%
  group_by(uncertainty, type) %>%
  summarize(alpha_num_sentences = n())

beta.dataset <- interim.dataset %>%
  group_by(type) %>%
  summarize(beta_num_sentences = n())

plot.dataset <- inner_join(alpha.dataset, beta.dataset, by = "type") %>%
  mutate(pct_sentences = alpha_num_sentences / beta_num_sentences) %>%
  select(uncertainty, type, pct_sentences)

# Resolution: 600 x 600
ggplot(plot.dataset, aes(x = type, y = pct_sentences, fill = uncertainty)) +
  geom_bar(stat = "identity", position = "dodge") +
  geom_text(aes(label = scales::percent(pct_sentences)), vjust = "inward",
            position = position_dodge(width=0.9)) +
  scale_x_discrete(labels = COMMENT.TYPE.LABELS) +
  scale_y_continuous(labels = scales::percent) +
  scale_fill_manual(name = "Uncertainty", values = FILLCOLORS,
                    labels = SENTENCE.METRIC.LABELS) +
  labs(title = title, x = "Comment Type", y = metric) +
  GetTheme()

## Politeness ====

### Query Data
dataset <- GetSentencePoliteness()

### Plot
metric <- "Sentence Politeness"
title <- "Distribution of Sentence Politeness"

plot.dataset <- dataset %>%
  inner_join(., COMMENT.TYPE, by = "comment_id") %>%
  select(-comment_id, -sentence_id) %>%
  melt(., id.vars = c("type"))

# Resolution: 500 x 400
ggplot(plot.dataset, aes(x = type, y = value, fill = type)) +
  geom_boxplot() +
  scale_x_discrete(labels = COMMENT.TYPE.LABELS) +
  scale_fill_manual(values = FILLCOLORS) +
  facet_wrap(~ variable, nrow = 1, scales = "free",
             labeller = as_labeller(SENTENCE.METRIC.LABELS)) +
  labs(title = title, x = "Comment Type", y = metric) +
  GetTheme() +
  theme(legend.position = "none")

## Formality ====

### Query Data
dataset <- GetSentenceFormality()

### Plot
metric <- "Sentence Formality"
title <- "Distribution of Sentence Formality"

plot.dataset <- dataset %>%
  inner_join(., COMMENT.TYPE, by = "comment_id") %>%
  select(-comment_id, -sentence_id) %>%
  melt(., id.vars = c("type"))

# Resolution: 500 x 400
ggplot(plot.dataset, aes(x = type, y = value, fill = type)) +
  geom_boxplot() +
  scale_x_discrete(labels = COMMENT.TYPE.LABELS) +
  scale_fill_manual(values = FILLCOLORS) +
  facet_wrap(~ variable, nrow = 1, scales = "free",
             labeller = as_labeller(SENTENCE.METRIC.LABELS)) +
  labs(title = title, x = "Comment Type", y = metric) +
  GetTheme() +
  theme(legend.position = "none")

## Informativeness ====

### Query Data
dataset <- GetSentenceInformativeness()

### Plot
metric <- "Sentence Informativeness"
title <- "Distribution of Sentence Informativeness"

plot.dataset <- dataset %>%
  inner_join(., COMMENT.TYPE, by = "comment_id") %>%
  select(-comment_id, -sentence_id) %>%
  melt(., id.vars = c("type"))

# Resolution: 500 x 400
ggplot(plot.dataset, aes(x = type, y = value, fill = type)) +
  geom_boxplot() +
  scale_x_discrete(labels = COMMENT.TYPE.LABELS) +
  scale_fill_manual(values = FILLCOLORS) +
  facet_wrap(~ variable, nrow = 1, scales = "free",
             labeller = as_labeller(SENTENCE.METRIC.LABELS)) +
  labs(title = title, x = "Comment Type", y = metric) +
  GetTheme() +
  theme(legend.position = "none")

## Implicature ====

### Query Data
dataset <- GetSentenceImplicature()

### Plot
metric <- "Sentence Implicature"
title <- "Distribution of Sentence Implicature"

plot.dataset <- dataset %>%
  inner_join(., COMMENT.TYPE, by = "comment_id") %>%
  select(-comment_id, -sentence_id) %>%
  melt(., id.vars = c("type"))

# Resolution: 500 x 400
ggplot(plot.dataset, aes(x = type, y = value, fill = type)) +
  geom_boxplot() +
  scale_x_discrete(labels = COMMENT.TYPE.LABELS) +
  scale_fill_manual(values = FILLCOLORS) +
  facet_wrap(~ variable, nrow = 1, scales = "free",
             labeller = as_labeller(SENTENCE.METRIC.LABELS)) +
  labs(title = title, x = "Comment Type", y = metric) +
  GetTheme() +
  theme(legend.position = "none")

## Sentence Length ====

### Query Data
dataset <- GetSentenceLength()

### Plot
metric <- "Sentence Length (Log Scale)"
title <- "Distribution of Sentence Length"

plot.dataset <- dataset %>%
  inner_join(., COMMENT.TYPE, by = "comment_id") %>%
  select(-comment_id, -sentence_id) %>%
  melt(., id.vars = c("type"))

# Resolution: 500 x 400
ggplot(plot.dataset, aes(x = type, y = value, fill = type)) +
  geom_boxplot() +
  scale_x_discrete(labels = COMMENT.TYPE.LABELS) +
  scale_y_log10() +
  scale_fill_manual(values = FILLCOLORS) +
  facet_wrap(~ variable, nrow = 1, scales = "free",
             labeller = as_labeller(SENTENCE.METRIC.LABELS)) +
  labs(title = title, x = "Comment Type", y = metric) +
  GetTheme() +
  theme(legend.position = "none")

