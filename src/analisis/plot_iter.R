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

files <- list.files('results/mixed_tabu0', "log_", full.names = TRUE)

df <- purrr::map_df(files, create_df)
max(df$iter)
unique(df$id)
df2 <- df %>% 
  group_by(id) %>% 
  filter(iter == max(iter))

df2 %>% 
  ggplot(aes(x='hola', y = waste)) + 
  geom_jitter()

plot_jitter <- function(type, random){
  files <- list.files("results", type, full.names = TRUE)
  files <- files[stringr::str_ends(files, "_random", negate=!random)]
  
  df <- purrr::map_df(files, function(f){purrr::map_df(list.files(f, "log_", full.names = TRUE), create_df)})
  
  df <- df %>% 
    group_by(id) %>% 
    filter(iter == max(iter)) %>% 
    ungroup() %>% 
    mutate(
      id = stringr::str_extract(id, "/.*/"),
      id = stringr::str_remove_all(id, "/")
      )
  return(df)
}

a <- plot_jitter('mixed', F)

a2 <- a
boxplot_mixed <- a %>% 
  mutate(id = case_when(
    id == "mixed_tabu0" ~ "Escenario 1",
    id == "mixed_tabu0_epsilon" ~ "Escenario 2",
    id == "mixed_tabu50" ~ "Escenario 3",
    id == "mixed_tabu50_epsilon" ~ "Escenario 4",
  )) %>% 
  ggplot(aes(x = id, y = waste)) +
  geom_boxplot() + 
  labs(x = "", 
       y = "Función objetivo")

ggsave("borrador/fig/boxplot_mixed.png", plot=boxplot_mixed)


paper <- plot_jitter('paper', F)

boxplot_paper <- paper %>% 
  mutate(id = case_when(
    id == "paper_tabu0" ~ "Escenario 1",
    id == "paper_tabu0_epsilon" ~ "Escenario 2",
    id == "paper_tabu50" ~ "Escenario 3",
    id == "paper_tabu50_epsilon" ~ "Escenario 4",
    TRUE ~ id
  )) %>% 
  ggplot(aes(x = id, y = waste)) +
  geom_boxplot() + 
  ylim(170,NA)+
  labs(x = "", 
       y = "Función objetivo")

ggsave("borrador/fig/boxplot_paper.png", plot=boxplot_paper)

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
  