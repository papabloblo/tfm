
library(ggplot2)
library(latex2exp)
i <- 1:1000
epsilon <- 10/(1+0.0005*(i**2))

p <- ggplot(data = data.frame(i = i, alpha = epsilon),
       aes(x = i, y = alpha)) +
  labs(y = TeX("$\\alpha$"),
       x = TeX("$i$"))+
  geom_line()

ggsave("borrador/fig/alpha.png", plot=p)
