# Load Externals ----
source("theme.R")
source("constants.R")
source("data/data.R")

# Function Definitions ----

## Generic ====
InitLibraries <- function(){
  libraries <- c("DBI", "effsize", "Hmisc", "nortest", "plyr", "dplyr", "ggplot2",
                 "reshape2", "tidyr")
  for(lib in libraries){
    suppressPackageStartupMessages(library(lib, character.only = T))
  }
}

InitGlobals <- function(){
  db.connection <- GetDbConnection(db.settings)
  COMMENT.TYPE <<- GetCommentType(db.connection)
  Disconnect(db.connection)
}

SplitByCommentType <- function(dataset, metric) {
  if (!(metric %in% colnames(dataset))) {
    stop(cat(metric, "is not a column in the dataset"))
  }
  x <- dataset %>% filter(type == "useful") %>% .[[metric]] %>% na.omit(.)
  y <- dataset %>% filter(type == "notuseful") %>% .[[metric]] %>% na.omit(.)

  return(list("x" = x, "y" = y))
}

## Database ====
GetDbConnection <- function(db.settings){
  connection <- Connect(
    provider = db.settings$provider,
    host = db.settings$host, port = db.settings$port,
    user = db.settings$user, password = db.settings$password,
    dbname = db.settings$dbname
  )
  return(connection)
}

Connect <- function(provider, host, port, user, password, dbname){
  connection <- NULL

  if(provider == "PostgreSQL")
    library("RPostgreSQL")
  else
    stop(sprintf("Database provider %s not supported.", provider))

  connection <- dbConnect(
    dbDriver(provider),
    host = host, port = port, user = user, password = password, dbname = dbname
  )

  return(connection)
}

Disconnect <- function(connection){
    return(dbDisconnect(connection))
}

GetData <- function(connection, query){
    return(dbGetQuery(connection, query))
}

## Correlation ====
GetSpearmansRho <- function(dataset, column.one, column.two, p.value = 0.05){
  correlation <- cor.test(
    dataset[[column.one]], dataset[[column.two]],
    method = "spearman", exact = F
  )
  p <- round(correlation$p.value, 4)
  rho <- round(correlation$estimate, 4)
  if(p > p.value){
    warning(paste("Spearman's correlation insignificant with p-value =", p))
  }
  return(list("significant" = p <= p.value, "rho" = rho))
}

GetCorrelation <- function(dataset, ignore = NA){
  if (!missing(ignore)) {
    dataset <- dataset %>%
      select(-(one_of(ignore)))
  }

  dataset <- na.omit(dataset)
  correlation <- dataset %>%
    cor(., method = "spearman")

  correlation[lower.tri(correlation)] <- NA
  correlation <- melt(correlation)
  correlation <- na.omit(correlation)

  return(correlation)
}

## Association ====
GetAssociation <- function(x, y, x.label, y.label, include.es = TRUE,
                           p.value = 0.05) {
  htest <- wilcox.test(x, y)

  p <- htest$p.value
  if(p > p.value){
    warning(paste("Association outcome insignificant with p-value =", p))
  }

  effect.size <- NA
  effect.magnitude <- NA
  if (include.es) {
    effect <- cliff.delta(x, y)
    effect.size <- effect$estimate
    effect.magnitude <- effect$magnitude
  }

  test.outcome <- list()
  test.outcome[["p"]] <- p
  test.outcome[["significant"]] <- p <= p.value
  test.outcome[["effect.size"]] <- effect.size
  test.outcome[["effect.magnitude"]] <- effect.magnitude
  test.outcome[[paste("mean.", x.label, sep = "")]] <- mean(x)
  test.outcome[[paste("mean.", y.label, sep = "")]] <- mean(y)
  test.outcome[[paste("median.", x.label, sep = "")]] <- median(x)
  test.outcome[[paste("median.", y.label, sep = "")]] <- median(y)
  return(test.outcome)
}

TestAssociation <- function(dataset, types, labels, p.value = 0.05){
  combinations <- combn(types, m = 2)
  for(column in seq(ncol(combinations))){
    type.a <- combinations[1,column]
    type.b <- combinations[2,column]
    population.a <- (dataset %>% filter(type == type.a))$metric
    population.b <- (dataset %>% filter(type == type.b))$metric
    label.a <- labels[type.a]
    label.b <- labels[type.b]

    htest <- wilcox.test(population.a, population.b)

    p <- htest$p.value
    significance <- ""
    if(p <= p.value){
      significance <- "*"
    }

    dataset.subset <- dataset %>% filter(type %in% c(type.a, type.b))
    dataset.subset$type <- factor(
      dataset.subset$type, levels = unique(dataset.subset$type)
    )
    # cliffs.delta <- cliff.delta(metric ~ type, data = dataset.subset)
    # d <- cliffs.delta$estimate
    # interpretation <- paste(" (", cliffs.delta$magnitude, ")", sep="")

    means <- data.frame(
      "type.a" = mean(population.a), "type.b" = mean(population.b)
    )
    medians <- data.frame(
      "type.a" = median(population.a), "type.b" = median(population.b)
    )
    summary.stats <- rbind(medians, means)
    colnames(summary.stats) <- c(label.a, label.b)
    rownames(summary.stats) <- c("Median", "Mean")

    cat(paste(rep("-", times = 79), collapse = ""), "\n")
    cat("", label.a, "vs.", label.b, "\n")
    cat(paste(rep("-", times = 79), collapse = ""), "\n")
    cat("p-value ", p, significance, "\n", sep = "")
    # cat("Effect  ", d, interpretation, "\n", sep = "")
    print(
      format(
        summary.stats, width = max(sapply(as.character(labels), nchar))
      )
    )
  }
}

## Plotting ====
PlotDistributions <- function(dataset){
  plots <- list()
  index <- 1
  for(metric.key in unique(dataset$metric)){
    subset <- dataset %>% filter(metric == metric.key)

    plot <- ggplot(subset, aes(x = type, y = value)) +
      geom_boxplot()

    if(metric.key %in% PERCENTSCALE.METRICS){
       plot <- plot + scale_y_continuous(labels = scales::percent)
    } else if(metric.key %in% LOGSCALE.METRICS){
      plot <- plot + scale_y_log10()
    } else {
      plot <- plot + scale_y_continuous()
    }
    plot <- plot +
      labs(x = NULL, y = NULL) +
      facet_wrap(~ metric, labeller = as_labeller(ALLMETRIC.LABELS)) +
      scale_x_discrete(labels = REVIEWTYPE.LABELS) +
      get.theme()

    plots[[index]] <- ggplotGrob(plot)
    index <- index + 1
  }

  return(plots)
}

## Normality ===
GetNormality <- function(data, p.value = 0.05) {
  test.outcome <- ad.test(data)
  return(list("p" = test.outcome$p.value,
              "is.normal" = test.outcome$p.value > p.value))
}

TestNormality <- function(data, label) {
  test.outcome <- ad.test(data)
  if (test.outcome$p.value < 0.05) {
    cat(label, "IS NOT normally distributed (p=", test.outcome$p.value, ")\n")
  } else {
    cat(label, "IS normally distributed (p=", test.outcome$p.value, ")\n")
  }
}
