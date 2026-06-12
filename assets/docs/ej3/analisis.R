# ============================================================
# PROBLEMA #3 - Cuadrado Latino 4x4
# Inspectores (filas) x Escalas (columnas) x Proveedores (trat)
# ============================================================
library(ggplot2); library(dplyr); library(gridExtra)

TITULO      <- "PROBLEMA #3 - Peso en gramos por Proveedor"
NOMBRE_FIL  <- "Inspector"
NOMBRE_COL  <- "Escala"
NOMBRE_TRAT <- "Proveedor"
RESPUESTA   <- "Peso (g)"

p <- 4

# Cuadrado latino: filas=Inspectores, columnas=Escalas
cuadrado <- matrix(c(
  "A","B","C","D",
  "B","C","D","A",
  "C","D","A","B",
  "D","A","B","C"
), nrow=p, byrow=TRUE)

# Observaciones fila por fila
y_mat <- matrix(c(
  16, 10, 11, 13,
  15,  9, 14, 13,
  13, 12, 17, 14,
  16, 15, 13, 11
), nrow=p, byrow=TRUE)

# ============================================================
# Construccion del DataFrame
# ============================================================
N    <- p * p
fila <- rep(paste0("I", 1:p), each=p)
col  <- rep(paste0("E", 1:p), times=p)
trat <- as.vector(t(cuadrado))
y    <- as.vector(t(y_mat))

df <- data.frame(
  Inspector = factor(fila),
  Escala    = factor(col),
  Proveedor = factor(trat),
  Y         = y
)

# ============================================================
# HIPOTESIS
# ============================================================
cat(strrep("=",65), "\n")
cat("HIPOTESIS\n")
cat(strrep("=",65), "\n")
cat("H0: No hay diferencia significativa entre proveedores (uA=uB=uC=uD)\n")
cat("H1: Al menos un proveedor difiere significativamente\n\n")

# ============================================================
# ANOVA - Cuadrado Latino
# ============================================================
modelo  <- aov(Y ~ Inspector + Escala + Proveedor, data=df)
resumen <- summary(modelo)[[1]]

cat(strrep("=",65), "\n")
cat("TABLA ANOVA -", TITULO, "\n")
cat(strrep("=",65), "\n")
print(summary(modelo))

alpha <- 0.05
gl_F  <- p - 1; gl_C <- p - 1; gl_T <- p - 1; gl_E <- (p-1)*(p-2)
ft_F  <- qf(1-alpha, gl_F, gl_E)
ft_C  <- qf(1-alpha, gl_C, gl_E)
ft_T  <- qf(1-alpha, gl_T, gl_E)
Fc_F  <- resumen[1,"F value"]
Fc_C  <- resumen[2,"F value"]
Fc_T  <- resumen[3,"F value"]

cat(sprintf("\nFt Inspector (%d,%d) = %.4f | Fc = %.4f -> %s\n", gl_F, gl_E, ft_F, Fc_F, ifelse(Fc_F>ft_F,"SIGNIFICATIVO","no significativo")))
cat(sprintf("Ft Escala    (%d,%d) = %.4f | Fc = %.4f -> %s\n", gl_C, gl_E, ft_C, Fc_C, ifelse(Fc_C>ft_C,"SIGNIFICATIVO","no significativo")))
cat(sprintf("Ft Proveedor (%d,%d) = %.4f | Fc = %.4f -> %s\n", gl_T, gl_E, ft_T, Fc_T, ifelse(Fc_T>ft_T,"SIGNIFICATIVO","no significativo")))

# ============================================================
# TUKEY - Proveedor
# ============================================================
cat("\n--- Tukey Proveedor ---\n")
tukey_T <- TukeyHSD(modelo, "Proveedor")
print(tukey_T)

# ============================================================
# GRAFICAS -> PNG  (ESTILO DISTINTIVO DE R: serif + viridis + sello)
# ============================================================
theme_R <- theme_minimal(base_family = "serif", base_size = 12) +
  theme(plot.title       = element_text(face = "bold", color = "#4b0082"),
        panel.background = element_rect(fill = "#faf7fb", color = NA),
        panel.grid.minor = element_blank(),
        legend.position  = "bottom")
PALETA_R <- c("#440154","#3b528b","#21918c","#5ec962")
ACCENT_R <- "#4b0082"
SELLO_R  <- "Generado en R 4.6  |  ggplot2  |  aov + TukeyHSD"
mg <- mean(df$Y)

# p1 - Medias por Inspector
df_pF <- data.frame(Niv=levels(df$Inspector),
                    Med=tapply(df$Y, df$Inspector, mean))
p1 <- ggplot(df_pF, aes(x=Niv, y=Med)) +
  geom_bar(stat="identity", fill=PALETA_R[1], color="black") +
  geom_hline(yintercept=mg, color="red", linetype="dashed", linewidth=1.2) +
  labs(title="Medias por Inspector", x="Inspector", y=RESPUESTA) +
  theme_R + theme(plot.title=element_text(size=12))

# p2 - Medias por Escala
df_pC <- data.frame(Niv=levels(df$Escala),
                    Med=tapply(df$Y, df$Escala, mean))
p2 <- ggplot(df_pC, aes(x=Niv, y=Med)) +
  geom_bar(stat="identity", fill=PALETA_R[3], color="black") +
  geom_hline(yintercept=mg, color="red", linetype="dashed", linewidth=1.2) +
  labs(title="Medias por Escala", x="Escala", y=RESPUESTA) +
  theme_R + theme(plot.title=element_text(size=12))

# p3 - Medias por Proveedor
df_pT <- data.frame(Niv=levels(df$Proveedor),
                    Med=tapply(df$Y, df$Proveedor, mean))
p3 <- ggplot(df_pT, aes(x=Niv, y=Med)) +
  geom_bar(stat="identity", fill=PALETA_R[4], color="black") +
  geom_hline(yintercept=mg, color="red", linetype="dashed", linewidth=1.2) +
  labs(title="Medias por Proveedor", x="Proveedor", y=RESPUESTA) +
  theme_R + theme(plot.title=element_text(size=12))

# p4 - Tukey Proveedor
tk_T_df <- as.data.frame(tukey_T[["Proveedor"]])
colnames(tk_T_df) <- c("diff","lwr","upr","p_adj")
tk_T_df$Comp <- rownames(tk_T_df)
tk_T_df$Sig  <- tk_T_df$p_adj < 0.05
p4 <- ggplot(tk_T_df, aes(y=reorder(Comp,diff), x=diff)) +
  geom_errorbarh(aes(xmin=lwr, xmax=upr, color=Sig), height=0.4, linewidth=1) +
  geom_point(aes(color=Sig), size=3) +
  geom_vline(xintercept=0, linetype="dashed") +
  scale_color_manual(values=c("TRUE"="#c2185b","FALSE"="#3b528b"),
                     labels=c("TRUE"="Sig.","FALSE"="No sig."), name="") +
  labs(title="Tukey HSD - Proveedor", x="Dif. medias (IC 95%)", y="") +
  theme_R + theme(plot.title=element_text(size=12))

# Tabla ANOVA grob
sc_F_v     <- resumen[1,"Sum Sq"]
sc_C_v     <- resumen[2,"Sum Sq"]
sc_T_v     <- resumen[3,"Sum Sq"]
sc_E_v     <- resumen[4,"Sum Sq"]
sc_Tot_v   <- sc_F_v + sc_C_v + sc_T_v + sc_E_v

tbl_df <- data.frame(
  "Fuente"   = c("Inspector","Escala","Proveedor","Error","Total"),
  "GL"       = c(gl_F, gl_C, gl_T, gl_E, N-1),
  "SC"       = round(c(sc_F_v, sc_C_v, sc_T_v, sc_E_v, sc_Tot_v), 4),
  "CM"       = c(round(sc_F_v/gl_F,4), round(sc_C_v/gl_C,4),
                 round(sc_T_v/gl_T,4), round(sc_E_v/gl_E,4), "-"),
  "Fc"       = c(round(Fc_F,4), round(Fc_C,4), round(Fc_T,4), "-", "-"),
  "Ft(5%)"   = c(round(ft_F,4), round(ft_C,4), round(ft_T,4), "-", "-"),
  "Decision" = c(ifelse(Fc_F>ft_F,"Sig ***","No sig"),
                 ifelse(Fc_C>ft_C,"Sig ***","No sig"),
                 ifelse(Fc_T>ft_T,"Sig ***","No sig"), "-", "-"),
  check.names=FALSE, stringsAsFactors=FALSE)

# Colores dinamicos segun significancia (Fc > Ft) — Inspector puede ser no sig.
# Paleta R (lavanda/teal) + fuente serif, distinta de Python
anova_fills <- c(
  ifelse(Fc_F > ft_F, "#d9f2ee", "#efeaf5"),
  ifelse(Fc_C > ft_C, "#d9f2ee", "#efeaf5"),
  ifelse(Fc_T > ft_T, "#d9f2ee", "#efeaf5"),
  "#faf7fb", "#e8e4f0"
)
tema <- gridExtra::ttheme_default(
  core   =list(bg_params=list(fill=anova_fills),
               fg_params=list(fontsize=9, fontfamily="serif")),
  colhead=list(bg_params=list(fill="#4b0082"),
               fg_params=list(col="white",fontsize=9.5,fontface="bold",fontfamily="serif")))
p_tbl <- gridExtra::arrangeGrob(
  grid::textGrob("Tabla ANOVA - Cuadrado Latino",
                 gp=grid::gpar(fontsize=11,fontface="bold",fontfamily="serif",col="#4b0082")),
  gridExtra::tableGrob(tbl_df, rows=NULL, theme=tema),
  ncol=1, heights=c(0.12,1))

# Rutas de salida (misma carpeta del script, sea cual sea la forma de ejecucion)
get_script_dir <- function() {
  # 1) Rscript "ruta/archivo.R"  -> commandArgs trae --file=
  args <- commandArgs(trailingOnly = FALSE)
  m <- grep("^--file=", args)
  if (length(m) > 0) return(dirname(normalizePath(sub("^--file=", "", args[m]))))
  # 2) source("ruta/archivo.R")  -> boton "Run Source" de VSCode / RStudio
  for (i in sys.nframe():1) {
    of <- sys.frame(i)$ofile
    if (!is.null(of)) return(dirname(normalizePath(of)))
  }
  # 3) RStudio con documento abierto
  if (requireNamespace("rstudioapi", quietly = TRUE) && rstudioapi::isAvailable()) {
    pth <- rstudioapi::getSourceEditorContext()$path
    if (!is.null(pth) && nzchar(pth)) return(dirname(normalizePath(pth)))
  }
  # 4) ultimo recurso: carpeta de trabajo
  getwd()
}
base_dir <- get_script_dir()
ruta   <- file.path(base_dir, "r_1.png")
ruta_t <- file.path(base_dir, "r_2.png")

titulo_g <- grid::textGrob(TITULO, gp=grid::gpar(fontsize=12, fontface="bold",
                                                 fontfamily="serif", col="#4b0082"))
sello_g  <- grid::textGrob(SELLO_R, gp=grid::gpar(fontsize=11, fontface="italic",
                                                  fontfamily="serif", col=ACCENT_R))
# Paneles reordenados (Tukey arriba) para diferenciar del layout de Python
png(ruta, width=1500, height=1050, res=130)
print(grid.arrange(p1, p2, p3, p4, layout_matrix=rbind(c(4,4,4),c(1,2,3)), top=titulo_g, bottom=sello_g))
dev.off()
cat("\nGrafica guardada:", ruta, "\n")

png(ruta_t, width=1200, height=420, res=130)
print(grid.arrange(p_tbl, bottom=sello_g))
dev.off()
cat("Tabla  guardada:", ruta_t, "\n")
