# Data Source: Database ----

GetCommentType <- function(connection, normalize = FALSE){
  useful.comments <- GetUsefulComments()
  if (nrow(useful.comments) == 0) {
    query <- "
      SELECT c.id AS comment_id,
        'useful'::text AS type
      FROM comment c
      WHERE c.by_reviewer IS true AND c.is_useful IS true;
    "
    useful.comments <- GetData(connection, query)
  }
  useful.comments$type <- factor(useful.comments$type,
                                 levels = c("notuseful", "useful"))

  notuseful.comments <- GetNotUsefulComments()
  if (nrow(notuseful.comments) == 0) {
    query <- "
      SELECT c.id AS comment_id,
        'notuseful'::text AS type
      FROM comment c
      WHERE c.by_reviewer IS true AND c.is_useful IS false;
    "
    notuseful.comments <- GetData(connection, query)
  }
  notuseful.comments$type <- factor(notuseful.comments$type,
                                    levels = c("notuseful", "useful"))

  dataset <- bind_rows(useful.comments, notuseful.comments)
  dataset$type <- factor(dataset$type, levels = c("notuseful", "useful"))
  return(dataset)
}

# Data Source: File System ----

GetNotUsefulComments <- function() {
  if (file.exists("data/notuseful.csv"))
    return(read.csv("data/notuseful.csv", header = T))
  return(data.frame())
}

GetUsefulComments <- function() {
  if (file.exists("data/useful.csv"))
    return(read.csv("data/useful.csv", header = T))
  return(data.frame())
}
