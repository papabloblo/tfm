library(jsonlite)
library(tidyverse)


extract_best <- function(f){
  a <- readLines(f)
  w <- c()
  
  for (i in 1:length(a)){
    b <- jsonlite::fromJSON(a[i])
    w <- c(w, max(b$best_waste, b$candidate1_waste))
  }
  return(w)
}




library(patchwork)
a <- (x1 | x2) 

a / a + plot_annotation(tag_levels = 'a')

create_df <- function(f){
  w <- extract_best(f)
  return(tibble(id = f, iter = 1:length(w), waste = w))
}

plot_iter <- function(f, scene, last){
  files <- list.files(f, "log_", full.names = TRUE)
  
  df <- purrr::map_df(files, create_df)
  
  x1 <- df %>% 
    ggplot(aes(x = iter, y = waste, group=id)) +
    geom_line() +
    ylim(50,NA) + 
    labs(y = "", x = "") +
    ggtitle(paste('Escenario', scene))
  
  x2 <- df %>% 
    ggplot(aes(x = iter, y = waste^20, group=id)) +
    geom_line() +
    labs(y = "", x = "") +
    scale_y_continuous(labels = function(x)round(x^(1/20)))
  
  if (last){ 
    x1 <- x1 + labs(x = "Iteración")
    x2 <- x2 + labs(x = "Iteración")
  }
  
  return(x1 | x2)
}

plot_all <- function(type, random){
  files <- list.files("results", type, full.names = TRUE)
  files <- files[stringr::str_ends(files, "_random", negate=!random)]
  i <- 0
  for (f in files){
    i <- i + 1
    if (f == files[1]){
      x <- plot_iter(f, scene=i, last=F)
    } else {
      x <- x / plot_iter(f, scene=i, last = f==files[length(files)])
    }
  }
  return(x)
}

mixed <- plot_all('mixed', random=F)
mixed_random <- plot_all('mixed', random=T)

ggsave("borrador/fig/mixed.png", plot=mixed, width = 7, height=10)

paper <- plot_all('paper', random=F)
paper_random <- plot_all('paper', random=T)

ggsave("borrador/fig/paper.png", plot=paper, width = 7, height=10)
  