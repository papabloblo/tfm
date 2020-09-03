library(tidyverse)
times <- readr::read_tsv("data/times-between-pickup-points.txt")

names(times) <- c('orig', 'dest', 'time')

times2 <- times %>% 
  group_by(orig) %>% 
  top_n(-1, time) %>% 
  ungroup()

mean(times2$time)
sd(times2$time)


rate_mixed <- readr::read_csv("data/pickup-point-filling-rates-mixed.csv")
rate_paper <- readr::read_csv("data/pickup-point-filling-rates-paper.csv")

rate_mixed$TASA <- as.numeric(rate_mixed$TASA)
rate_paper$TASA <- as.numeric(rate_paper$TASA)

mean(rate_mixed$TASA, na.rm=TRUE)
sd(rate_mixed$TASA, na.rm=TRUE)

mean(rate_paper$TASA, na.rm=TRUE)
sd(rate_paper$TASA, na.rm=TRUE)
