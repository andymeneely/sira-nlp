# Data Source: Database ----

GetCommentType <- function(connection, normalize = FALSE){
  notuseful.comments <- GetNotUsefulComments()
  if (nrow(notuseful.comments) > 0) {
    query <- "
      SELECT c.id AS comment_id,
        'useful'::text AS type
      FROM comment c
      WHERE c.by_reviewer IS true AND c.is_useful IS true;
    "
    dataset <- GetData(connection, query) %>%
      bind_rows(notuseful.comments)
  } else {
    query <- "
      SELECT c.id AS comment_id,
        CASE WHEN is_useful IS true THEN 'useful' ELSE 'notuseful' END AS type
      FROM comment c
      WHERE c.by_reviewer IS true;
    "
    dataset <- GetData(connection, query)
  }
  dataset$type <- factor(dataset$type, levels = c("notuseful", "useful"))
  return(dataset)
}

# Data Source: File System ----

GetNotUsefulComments <- function() {
  if (file.exists("data/notuseful.csv"))
    return(read.csv("data/notuseful.csv", header = T))
  return(data.frame())
}
