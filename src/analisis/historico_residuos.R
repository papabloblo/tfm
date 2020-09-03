library(tidyverse)

# FUENTE: https://www.ine.es/dyngs/INEbase/es/operacion.htm?c=Estadistica_C&cid=1254736176844&menu=resultados&idp=1254735976612

# IMPORTACIÓN -------------------------------------------------------------

residuos <- readr::read_csv2("data/open_data/residuos_ine_2010-17-.csv")


# NOMBRE DE VARIABLES -----------------------------------------------------

names(residuos) <- c("tipo_residuo", "ccaa", "periodo", "total")


# TRATAMIENTO TIPO DE RESIDUO ---------------------------------------------

unique(residuos$tipo_residuo)

residuos <- residuos %>% 
  mutate(
    tipo_residuo = case_when(
      tipo_residuo == "07.1 Residuos de vidrio" ~ "vidrio",
      tipo_residuo == "07.2 Residuos de papel y cartón" ~ "papel",
      tipo_residuo == "07.4 Residuos de plásticos" ~ "plastico",
      TRUE ~ tipo_residuo
    )
  )



residuos %>% 
  filter(tipo_residuo == "vidrio",
         ccaa == "Total nacional"
         ) %>% 
  ggplot(
    aes( x = periodo,
         y = total)
  ) +
  geom_line()


residuos %>% 
  filter(
    ccaa == "Total nacional",
    tipo_residuo == "TOTAL RESIDUOS"
  ) %>% 
  ggplot(
    aes( x = periodo,
         y = total)
  ) +
  geom_line()
