# Clear ----
rm(list = ls())
cat("\014")

# Initialize ----

## Database ====
if(!file.exists("db.settings.R")){
  stop(sprintf("db.settings.R file not found."))
}
source("db.settings.R")
region <- "development"
db.settings <- GetDbSettings(region)
cat("Database Region:", region)

## Externals ====
source("library.R")

## Libraries ====
InitLibraries()
