# Initialize Boilerplate ----
source("boilerplate.R")
source("data/comment.R")

## Continuous Valued Metrics ====

### Query Data ####
dataset <- GetCommentContinuousMetrics(normalize = FALSE)

analysis.dataset <- dataset %>%
  select(-comment_id)

### Test: Spearman's ####
metrics <- colnames(analysis.dataset)

done <- 0
total <- length(metrics) * (length(metrics) - 1) / 2

test.outcomes <- data.frame()
for (i in 1:(length(metrics) - 1)) {
  for (j in (i + 1):length(metrics)) {
    done <- done + 1

    column.one <- metrics[i]
    label.one <- COMMENT.METRIC.LABELS[column.one]
    column.two <- metrics[j]
    label.two <- COMMENT.METRIC.LABELS[column.two]

    cat("[", done, "/", total, "] ", label.one, " and ", label.two, "\n",
        sep = "")

    test.outcome <- GetSpearmansRho(analysis.dataset, column.one, column.two)
    test.outcome <- data.frame("X" = label.one, "Y" = label.two, test.outcome)
    rownames(test.outcome) <- c()

    test.outcomes <- rbind(test.outcomes, test.outcome)
  }
}
print(test.outcomes)

### Test: Variable Clustering ####
test.outcome <- varclus(as.matrix(analysis.dataset))

## Linguistic Versus Experience ####

### Query Data ####
linguistic.dataset <- GetCommentContinuousMetrics(normalize = TRUE)
experience.dataset <- GetProjectExperience(normalize = TRUE) %>%
  select(-uni_prj_experience)

lingusitic.metrics <- setdiff(colnames(linguistic.dataset), COMMENT.KEYS)
experience.metrics <- setdiff(colnames(experience.dataset), COMMENT.KEYS)
experience.metrics <- setdiff(experience.metrics, c("author"))

analysis.dataset <- linguistic.dataset %>%
  inner_join(., experience.dataset, by = COMMENT.KEYS) %>%
  select(-comment_id)

### Test: Overall ####
done <- 0
total <- length(linguistic.metrics) * length(experience.metrics)

test.outcomes <- data.frame()
for (i in 1:length(linguistic.metrics)) {
  column.one <- linguistic.metrics[i]
  label.one <- COMMENT.METRIC.LABELS[[column.one]]
  for (j in 1:length(experience.metrics)) {
    column.two <- experience.metrics[j]
    label.two <- COMMENT.METRIC.LABELS[[column.two]]

    done <- done + 1
    cat("[", done, "/", total, "] ", label.one, " vs. ", label.two, "\n",
        sep = "")

    test.outcome <- GetSpearmansRho(analysis.dataset, column.one, column.two)
    test.outcome <- data.frame("X" = label.one, "Y" = label.two, test.outcome)
    rownames(test.outcome) <- c()

    test.outcomes <- rbind(test.outcomes, test.outcome)
  }
}
print(test.outcomes)

### Test: Per Author ####
authors.dataset <- analysis.dataset %>%
  select(author) %>%
  group_by(author) %>%
  summarise(num_comments = n()) %>%
  filter(num_comments > 1) %>%
  arrange(-num_comments)

done <- 0
cortest.outcomes <- data.frame()
for (k in 1:nrow(authors.dataset)) {
  a <- authors.dataset[k,]
  interim.dataset <- analysis.dataset %>%
    filter(author == a$author)
  for (i in 1:length(linguistic.metrics)) {
    column.one <- linguistic.metrics[i]
    for (j in 1:length(experience.metrics)) {
      column.two <- experience.metrics[j]

      test.outcome <- GetSpearmansRho(interim.dataset, column.one, column.two)
      test.outcome <- data.frame("author" = a$author,
                                 "num_comments" = a$num_comments,
                                 "X" = column.one, "Y" = column.two,
                                 test.outcome)
      rownames(test.outcome) <- c()

      cortest.outcomes <- rbind(cortest.outcomes, test.outcome)
    }
  }
  done <- done + 1
  cat("[", done, "/", nrow(authors.dataset), "]\n", sep = "")
}

test.outcomes <- data.frame()
for (i in 1:length(linguistic.metrics)) {
  metric <- linguistic.metrics[i]
  cat(metric, "\n")

  interim.dataset <- cortest.outcomes %>%
    filter(X == metric)

  rho.significant <- interim.dataset %>% filter(significant == T) %>% nrow(.)
  rho.insignificant <- interim.dataset %>% filter(significant == F) %>% nrow(.)

  x <- interim.dataset %>%
    filter(significant == T) %>%
    .$rho

  test.outcome <- GetOneSampleAssociation(x)
  test.outcome <- data.frame("metric" = metric,
                             "num_rho_significant" = rho.significant,
                             "num_rho_insignificant" = rho.insignificant,
                             test.outcome)
  rownames(test.outcome) <- c()
  test.outcomes <- rbind(test.outcomes, test.outcome)
}
print(test.outcomes)
