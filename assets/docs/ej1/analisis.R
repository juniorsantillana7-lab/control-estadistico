# ============================================================
# PROBLEMA #1 - DISENO FACTORIAL COMPLETAMENTE ALEATORIZADO
# Factor A: Maquina (6 niveles: M1-M6)
# Factor B: Hombre  (4 niveles: I, II, III, IV)
# Replicas: n = 3  |  N = 72
# Variable respuesta: Nro de sacos defectuosos por dia
# ============================================================

library(ggplot2)
library(dplyr)
library(gridExtra)

# ---- Datos -------------------------------------------------
maquina <- rep(c("M1","M2","M3","M4","M5","M6"), each = 12)
hombre  <- rep(c("I","I","I","II","II","II","III","III","III","IV","IV","IV"), times = 6)
sacos   <- c(
  # M1
  10, 8, 7,   5, 6, 8,   12,13,12,   5, 3, 2,
  # M2
  12,13,15,   4, 5, 2,   10,10, 5,   2, 3, 4,
  # M3
  15,13,10,   6, 6, 5,    9, 6, 4,   5, 6, 2,
  # M4
   8, 5, 6,   5, 5, 4,   11,10, 4,   5, 4, 1,
  # M5
   5, 7, 4,   5, 4, 4,    5, 5, 3,   2, 2, 3,
  # M6
   5, 6, 3,   4, 3, 5,    8, 3, 6,   2, 4, 1
)

df <- data.frame(
  Maquina = factor(maquina, levels = c("M1","M2","M3","M4","M5","M6")),
  Hombre  = factor(hombre,  levels = c("I","II","III","IV")),
  Sacos   = sacos
)

# ============================================================
# ANOVA FACTORIAL
# ============================================================
modelo <- aov(Sacos ~ Maquina * Hombre, data = df)

cat(strrep("=", 65), "\n")
cat("TABLA ANOVA - DISENO FACTORIAL\n")
cat(strrep("=", 65), "\n")
print(summary(modelo))

# F criticos
alpha <- 0.05
ft_A  <- qf(1 - alpha,  5, 48)
ft_B  <- qf(1 - alpha,  3, 48)
ft_AB <- qf(1 - alpha, 15, 48)

cat(sprintf("\nF critico Factor A  (5, 48)  = %.4f\n", ft_A))
cat(sprintf("F critico Factor B  (3, 48)  = %.4f\n", ft_B))
cat(sprintf("F critico Inter AxB (15, 48) = %.4f\n", ft_AB))

resumen <- summary(modelo)[[1]]
Fc_A  <- resumen[1, "F value"]
Fc_B  <- resumen[2, "F value"]
Fc_AB <- resumen[3, "F value"]

cat("\nCONCLUSIONES:\n")
cat(sprintf("  Factor A (Maquina): Fc=%.4f %s significativamente\n",
            Fc_A,  ifelse(Fc_A  > ft_A,  "> SI influye", "< NO influye")))
cat(sprintf("  Factor B (Hombre):  Fc=%.4f %s significativamente\n",
            Fc_B,  ifelse(Fc_B  > ft_B,  "> SI influye", "< NO influye")))
cat(sprintf("  Interaccion AxB:    Fc=%.4f %s significativamente\n",
            Fc_AB, ifelse(Fc_AB > ft_AB, "> SI influye", "< NO influye")))

# ============================================================
# PRUEBA DE TUKEY
# ============================================================
cat("\n", strrep("=", 65), "\n")
cat("PRUEBA DE TUKEY - FACTOR A: Maquina\n")
cat(strrep("=", 65), "\n")
tukey_A <- TukeyHSD(modelo, "Maquina", conf.level = 0.95)
print(tukey_A)

cat("\n", strrep("=", 65), "\n")
cat("PRUEBA DE TUKEY - FACTOR B: Hombre\n")
cat(strrep("=", 65), "\n")
tukey_B <- TukeyHSD(modelo, "Hombre", conf.level = 0.95)
print(tukey_B)

# ============================================================
# GRAFICAS (ggplot2 - evita conflicto de layout con TukeyHSD)
# ============================================================
COLORES <- c("#1f77b4","#ff7f0e","#2ca02c","#d62728")
media_global <- mean(df$Sacos)

# 1. Efecto principal A
medias_A <- tapply(df$Sacos, df$Maquina, mean)
df_A <- data.frame(Maquina = factor(names(medias_A), levels = c("M1","M2","M3","M4","M5","M6")),
                   Media = as.numeric(medias_A))
p1 <- ggplot(df_A, aes(x = Maquina, y = Media)) +
  geom_bar(stat = "identity", fill = "steelblue", color = "black") +
  geom_hline(yintercept = media_global, color = "red", linetype = "dashed", linewidth = 1.2) +
  annotate("text", x = 1, y = media_global + 0.4, label = "Media global", color = "red", size = 3) +
  labs(title = "Efecto Principal - Factor A: Maquina",
       x = "Maquina", y = "Media sacos defectuosos") +
  theme_bw(base_size = 11) +
  theme(plot.title = element_text(face = "bold", size = 10))

# 2. Efecto principal B
medias_B <- tapply(df$Sacos, df$Hombre, mean)
df_B <- data.frame(Hombre = factor(names(medias_B), levels = c("I","II","III","IV")),
                   Media = as.numeric(medias_B))
p2 <- ggplot(df_B, aes(x = Hombre, y = Media)) +
  geom_bar(stat = "identity", fill = "coral", color = "black") +
  geom_hline(yintercept = media_global, color = "red", linetype = "dashed", linewidth = 1.2) +
  annotate("text", x = 1, y = media_global + 0.4, label = "Media global", color = "red", size = 3) +
  labs(title = "Efecto Principal - Factor B: Hombre",
       x = "Operario", y = "Media sacos defectuosos") +
  theme_bw(base_size = 11) +
  theme(plot.title = element_text(face = "bold", size = 10))

# 3. Interaccion AxB
interact <- tapply(df$Sacos, list(df$Hombre, df$Maquina), mean)
df_int <- as.data.frame(as.table(interact))
names(df_int) <- c("Hombre", "Maquina", "Media")
df_int$Maquina <- factor(df_int$Maquina, levels = c("M1","M2","M3","M4","M5","M6"))
df_int$Hombre  <- factor(df_int$Hombre,  levels = c("I","II","III","IV"))
p3 <- ggplot(df_int, aes(x = Maquina, y = Media, color = Hombre, group = Hombre)) +
  geom_line(linewidth = 1.4) +
  geom_point(size = 3) +
  scale_color_manual(values = COLORES) +
  labs(title = "Interaccion AxB: Maquina x Hombre",
       x = "Maquina", y = "Media sacos defectuosos", color = "Hombre") +
  theme_bw(base_size = 11) +
  theme(plot.title = element_text(face = "bold", size = 10))

# 4. Tukey A - grafica de intervalos
tk_A <- as.data.frame(tukey_A$Maquina)
colnames(tk_A) <- c("diff","lwr","upr","p_adj")
tk_A$Comparacion <- rownames(tk_A)
tk_A$Sig <- tk_A$p_adj < 0.05
p4 <- ggplot(tk_A, aes(y = reorder(Comparacion, diff), x = diff)) +
  geom_errorbarh(aes(xmin = lwr, xmax = upr, color = Sig), height = 0.5, linewidth = 1) +
  geom_point(aes(color = Sig), size = 3) +
  geom_vline(xintercept = 0, linetype = "dashed", color = "black") +
  scale_color_manual(values = c("TRUE" = "red", "FALSE" = "steelblue"),
                     labels = c("TRUE" = "Significativo", "FALSE" = "No significativo"),
                     name = "") +
  labs(title = "Tukey HSD - Factor A: Maquina",
       x = "Diferencia de medias (IC 95%)", y = "Comparacion") +
  theme_bw(base_size = 10) +
  theme(plot.title = element_text(face = "bold", size = 10),
        legend.position = "bottom")

# 5. Tukey B - grafica de intervalos
tk_B <- as.data.frame(tukey_B$Hombre)
colnames(tk_B) <- c("diff","lwr","upr","p_adj")
tk_B$Comparacion <- rownames(tk_B)
tk_B$Sig <- tk_B$p_adj < 0.05
p5 <- ggplot(tk_B, aes(y = reorder(Comparacion, diff), x = diff)) +
  geom_errorbarh(aes(xmin = lwr, xmax = upr, color = Sig), height = 0.35, linewidth = 1) +
  geom_point(aes(color = Sig), size = 3) +
  geom_vline(xintercept = 0, linetype = "dashed", color = "black") +
  scale_color_manual(values = c("TRUE" = "red", "FALSE" = "coral"),
                     labels = c("TRUE" = "Significativo", "FALSE" = "No significativo"),
                     name = "") +
  labs(title = "Tukey HSD - Factor B: Hombre",
       x = "Diferencia de medias (IC 95%)", y = "Comparacion") +
  theme_bw(base_size = 10) +
  theme(plot.title = element_text(face = "bold", size = 10),
        legend.position = "bottom")

# 6. Tabla ANOVA como tableGrob
sc_A  <- resumen[1, "Sum Sq"]
sc_B  <- resumen[2, "Sum Sq"]
sc_AB <- resumen[3, "Sum Sq"]
sc_E  <- resumen[4, "Sum Sq"]
sc_T  <- sc_A + sc_B + sc_AB + sc_E

anova_df <- data.frame(
  "Fuente de Variacion" = c("Factor A: Maquina", "Factor B: Hombre",
                             "Interaccion AxB", "Error (Residual)", "Total"),
  "GL"  = c("5", "3", "15", "48", "71"),
  "SC"  = c(sprintf("%.4f", sc_A),  sprintf("%.4f", sc_B),
             sprintf("%.4f", sc_AB), sprintf("%.4f", sc_E),
             sprintf("%.4f", sc_T)),
  "CM"  = c(sprintf("%.4f", sc_A/5),  sprintf("%.4f", sc_B/3),
             sprintf("%.4f", sc_AB/15), sprintf("%.4f", sc_E/48), "—"),
  "Fc"  = c(sprintf("%.4f", Fc_A), sprintf("%.4f", Fc_B),
             sprintf("%.4f", Fc_AB), "—", "—"),
  "Ft (a=5%)" = c(sprintf("%.4f", ft_A), sprintf("%.4f", ft_B),
                   sprintf("%.4f", ft_AB), "—", "—"),
  "Conclusion" = c("Significativo ***", "Significativo ***",
                   "Significativo ***", "—", "—"),
  check.names = FALSE,
  stringsAsFactors = FALSE
)

# Estilos de la tabla
tema_tbl <- gridExtra::ttheme_default(
  core = list(
    bg_params = list(fill = c("#d5f5e3","#d5f5e3","#d5f5e3","#fdfefe","#eaecee")),
    fg_params = list(fontsize = 9, hjust = 0.5)
  ),
  colhead = list(
    bg_params = list(fill = "#2c3e50"),
    fg_params = list(col = "white", fontsize = 9.5, fontface = "bold")
  )
)
p_tabla <- gridExtra::tableGrob(anova_df, rows = NULL, theme = tema_tbl)

# Titulo encima de la tabla
titulo_tabla <- grid::textGrob(
  "Tabla ANOVA - Diseno Factorial Completamente Aleatorizado",
  gp = grid::gpar(fontsize = 10, fontface = "bold")
)
p_tabla_con_titulo <- gridExtra::arrangeGrob(titulo_tabla, p_tabla, ncol = 1,
                                              heights = c(0.12, 1))

# Rutas de salida — carpeta fija del problema 1
base_dir <- normalizePath("C:/Users/ASUS/Desktop/control pc3/problemas resueltos/problema 1")
ruta   <- file.path(base_dir, "P1_resultados_R.png")
ruta_t <- file.path(base_dir, "P1_tabla_anova_R.png")

# PNG 1: graficas principales
titulo <- grid::textGrob("PROBLEMA #1 - Diseno Factorial: Maquina x Hombre",
                         gp = grid::gpar(fontsize = 13, fontface = "bold"))
lay <- rbind(c(1, 2, 3), c(4, 4, 5))
png(ruta, width = 1600, height = 1100, res = 130)
grid.arrange(p1, p2, p3, p4, p5, layout_matrix = lay,
             heights = c(1.5, 1.5), top = titulo)
dev.off()
cat(sprintf("\nGrafica guardada en: %s\n", ruta))

# PNG 2: tabla ANOVA
png(ruta_t, width = 1300, height = 450, res = 130)
grid.arrange(p_tabla_con_titulo)
dev.off()
cat(sprintf("Tabla   guardada en: %s\n", ruta_t))
