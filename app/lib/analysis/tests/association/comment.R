# Initialize Boilerplate ----
source("boilerplate.R")
source("data/comment.R")

InitGlobals()

## Test: Continuous-valued Metrics ====
metrics <- COMMENT.CV.METRICS

test.outcomes <- data.frame()
for (i in 1:length(metrics)) {
  metric <- metrics[i]
  metric.label <- COMMENT.METRIC.LABELS[[metric]]
  cat("[", i, "/", length(metrics), "] ", metric.label, "\n", sep = "")

  dataset <- GetCommentMetric(metric)
  analysis.dataset <- dataset %>%
    inner_join(., COMMENT.TYPE, by = "comment_id") %>%
    select(-comment_id)

  variants <- c(metric)
  if (metric %in% names(COMMENT.CV.METRIC.VARIANTS)) {
    variants <- unlist(COMMENT.CV.METRIC.VARIANTS[[metric]])
  }
  for (j in 1:length(variants)) {
    metric.variant <- variants[j]
    variant.label <- COMMENT.METRIC.LABELS[[metric.variant]]
    cat(" [", j, "/", length(variants), "] ", variant.label, "\n", sep = "")

    splits <- SplitByCommentType(analysis.dataset, metric = metric.variant)
    SaveSplits(splits, granularity = "comment", metric = metric.variant)

    test.outcome <- GetAssociation(splits$x, splits$y, "useful", "notuseful")
    test.outcome <- data.frame("metric" = variant.label, test.outcome)
    rownames(test.outcome) <- c()
    test.outcomes <- rbind(test.outcomes, test.outcome)
  }
}
print(test.outcomes)

## Test: Boolean-valued Metrics ====
metrics <- COMMENT.BV.METRICS

test.outcomes <- data.frame()
for (i in 1:length(metrics)) {
  metric <- metrics[i]
  metric.label <- COMMENT.METRIC.LABELS[[metric]]
  cat("[", i, "/", length(metrics), "] ", metric.label, "\n", sep = "")

  dataset <- GetCommentMetric(metric)
  analysis.dataset <- dataset %>%
    inner_join(., COMMENT.TYPE, by = "comment_id") %>%
    select(-comment_id)

  variants <- c(metric)
  if (metric %in% names(COMMENT.BV.METRIC.VARIANTS)) {
    variants <- unlist(COMMENT.BV.METRIC.VARIANTS[[metric]])
  }
  for (j in 1:length(variants)) {
    metric.variant <- variants[j]
    variant.label <- COMMENT.METRIC.LABELS[[metric.variant]]
    cat(" [", j, "/", length(variants), "] ", variant.label, "\n", sep = "")

    test.outcome <- GetIndependence(analysis.dataset$type,
                                    analysis.dataset[[metric.variant]])
    test.outcome <- data.frame("metric" = variant.label, test.outcome)
    rownames(test.outcome) <- c()
    test.outcomes <- rbind(test.outcomes, test.outcome)
  }
}
print(test.outcomes)

## Test: Linguistic Versus Experience ####

### Query Data ####
linguistic.dataset <- GetCommentUncertainty(normalize = TRUE)
experience.dataset <- GetProjectExperience(normalize = TRUE) %>%
  select(-uni_prj_experience)

linguistic.metrics <- setdiff(colnames(linguistic.dataset), COMMENT.KEYS)
experience.metrics <- setdiff(colnames(experience.dataset), COMMENT.KEYS)
experience.metrics <- setdiff(experience.metrics, c("author"))

analysis.dataset <- linguistic.dataset %>%
  inner_join(., experience.dataset, by = COMMENT.KEYS) %>%
  select(-comment_id)

### Overall ####
test.outcomes <- data.frame()
for (i in 1:length(linguistic.metrics)) {
  metric <- linguistic.metrics[i]
  metric.label <- COMMENT.METRIC.LABELS[[metric]]

  cat(metric.label, "\n")

  x <- analysis.dataset[analysis.dataset[, metric] == T,]$prp_prj_experience
  y <- analysis.dataset[analysis.dataset[, metric] == F,]$prp_prj_experience
  splits <- list("x" = x, "y" = y)
  SaveSplits(splits, granularity = "comment", metric = metric)

  test.outcome <- GetAssociation(splits$x, splits$y, "uncertain", "certain")
  test.outcome <- data.frame("metric" = metric.label, test.outcome)
  rownames(test.outcome) <- c()
  test.outcomes <- rbind(test.outcomes, test.outcome)
}
print(test.outcomes)

### Per Author ####
authors.dataset <- analysis.dataset %>%
  select(author) %>%
  group_by(author) %>%
  summarise(num_comments = n()) %>%
  filter(num_comments > 1) %>%
  arrange(-num_comments)

done <- 0
assoctest.outcomes <- data.frame()
for (k in 1:nrow(authors.dataset)) {
  a <- authors.dataset[k,]
  interim.dataset <- analysis.dataset %>%
    filter(author == a$author)
  for (i in 1:length(linguistic.metrics)) {
    metric <- linguistic.metrics[i]

    x <- interim.dataset[interim.dataset[, metric] == T,]$prp_prj_experience
    y <- interim.dataset[interim.dataset[, metric] == F,]$prp_prj_experience
    splits <- list("x" = x, "y" = y)

    if (length(x) == 0 || length(y) == 0) {
      next
    }

    test.outcome <- GetEffectSize(splits$x, splits$y)
    test.outcome <- data.frame("metric" = metric, test.outcome)
    rownames(test.outcome) <- c()
    assoctest.outcomes <- rbind(assoctest.outcomes, test.outcome)
  }
  done <- done + 1
  cat("[", done, "/", nrow(authors.dataset), "]\n", sep = "")
}

test.outcomes <- data.frame()
for (i in 1:length(linguistic.metrics)) {
  metric <- linguistic.metrics[i]
  metric.label <- COMMENT.METRIC.LABELS[[metric]]
  cat(metric.label, "\n")

  interim.dataset <- assoctest.outcomes %>%
    filter(metric == linguistic.metrics[i])

  delta.significant <- interim.dataset %>% filter(significant == T) %>% nrow(.)
  delta.insignificant <- interim.dataset %>% filter(significant == F) %>% nrow(.)

  x <- interim.dataset %>%
    filter(significant == T) %>%
    .$delta

  test.outcome <- GetOneSampleAssociation(x)
  test.outcome <- data.frame("metric" = metric,
                             "num_delta_significant" = delta.significant,
                             "num_delta_insignificant" = delta.insignificant,
                             test.outcome)
  rownames(test.outcome) <- c()
  test.outcomes <- rbind(test.outcomes, test.outcome)
}
print(test.outcomes)
