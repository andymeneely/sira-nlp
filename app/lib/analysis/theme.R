# Colors ----
FILLCOLORS <- c(
  # Comment Type
  "useful" = "#ed7d31",
  "notuseful" = "#70ad47",
  # Sentiment
  "negative" = "#f3ac7b",
  "neutral" = "#bcbcbc",
  "positive" = "#b1d29a",
  # Uncertainty
  "D" = "#d2e8de",
  "E" = "#a5d1bd",
  "N" = "#78ba9c",
  "I" = "#4ca37b",
  "has_doxastic" = "#d2e8de",
  "has_epistemic" = "#a5d1bd",
  "has_conditional" = "#78ba9c",
  "has_investigative" = "#4ca37b",
  "has_uncertainty" = "#1f8c5a",
  # Bug Familiarity
  "TRUE" = "#f3ac7b",
  "FALSE" = "#b1d29a"
)

# Function ----
GetTheme <- function(){
  plot.theme <-
    theme_bw() +
    theme(plot.title = element_text(size = 14, face = "bold",
                                    margin = ggplot2::margin(5,0,15,0),
                                    hjust = 0.5),
          axis.text.x = element_text(size=10, colour = "black", angle = 50,
                                     vjust = 1, hjust = 1),
          axis.title.x = element_text(colour = "black", face = "bold",
                                      margin = ggplot2::margin(10,0,5,0)),
          axis.text.y = element_text(size=10, colour = "black"),
          axis.title.y = element_text(colour = "black", face = "bold",
                                      margin = ggplot2::margin(0,10,0,5)),
          strip.text.x = element_text(size=10, face="bold"),
          legend.position = "bottom",
          legend.title = element_text(size = 9, face = "bold"),
          legend.text = element_text(size = 9)
    )
  return(plot.theme)
}
