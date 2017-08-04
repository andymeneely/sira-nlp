# Data Source: Database ----

GetCommentType <- function(connection, normalize = FALSE){
  query <- "
    SELECT c.id AS comment_id,
      CASE WHEN c.is_useful IS true THEN 'useful' ELSE 'notuseful' END AS type
    FROM comment c
    WHERE c.by_reviewer IS true;
  "
  dataset <- GetData(connection, query)
  return(dataset)
}
