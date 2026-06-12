# ============================================================
# PROBLEMA 2 - Cuadrado Latino 4x4 con Dato Perdido
# Diseno: Orden_Montaje x Operador x Metodo
# ============================================================
library(ggplot2); library(dplyr); library(gridExtra)

# ============================================================
# DATOS
# ============================================================
TITULO      <- "PROBLEMA 2 - Cuadrado Latino 4x4 con Dato Perdido"
NOMBRE_FIL  <- "Orden_Montaje"
NOMBRE_COL  <- "Operador"
NOMBRE_TRAT <- "Metodo"
RESPUESTA   <- "Y"

p <- 4

# Cuadrado latino:  fila 3 col 3 = tratamiento C = NA
cuadrado <- matrix(c(
  "C","D","A","B",
  "B","C","D","A",
  "A","B","C","D",
  "D","A","B","C"
), nrow=p, byrow=TRUE)

# Observaciones (NA = dato perdido, fila 3 col 3)
y_mat <- matrix(c(
  10, 14,  7,  8,
   7, 18, 11,  8,
   5, 10, NA,  9,
  10, 10, 12, 14
), nrow=p, byrow=TRUE)

# ============================================================
# Construir data frame
# ============================================================
N_orig    <- p * p
filas_idx <- paste0("F", 1:p)
cols_idx  <- paste0("C", 1:p)

fila_v <- rep(filas_idx, each=p)
col_v  <- rep(cols_idx,  times=p)
trat_v <- as.vector(t(cuadrado))
y_v    <- as.vector(t(y_mat))

df_full <- data.frame(
  Fila    = factor(fila_v, levels=filas_idx),
  Columna = factor(col_v,  levels=cols_idx),
  Trat    = factor(trat_v),
  Y       = y_v
)
names(df_full)[1:3] <- c(NOMBRE_FIL, NOMBRE_COL, NOMBRE_TRAT)

idx_na <- which(is.na(df_full$Y))
cat("Dato perdido: fila", as.character(df_full[idx_na, NOMBRE_FIL]),
    "| col", as.character(df_full[idx_na, NOMBRE_COL]),
    "| trat", as.character(df_full[idx_na, NOMBRE_TRAT]), "\n")

# ============================================================
# FORMULA DE YATES  (CORRECTA): Y' = (p*(R+C+T) - 2*G) / ((p-1)*(p-2))
# ============================================================
df_sin <- df_full[!is.na(df_full$Y), ]
G      <- sum(df_sin$Y)
fila_p <- as.character(df_full[idx_na, NOMBRE_FIL])
col_p  <- as.character(df_full[idx_na, NOMBRE_COL])
trat_p <- as.character(df_full[idx_na, NOMBRE_TRAT])

R   <- sum(df_sin$Y[df_sin[[NOMBRE_FIL]]  == fila_p])
C   <- sum(df_sin$Y[df_sin[[NOMBRE_COL]]  == col_p])
T_t <- sum(df_sin$Y[df_sin[[NOMBRE_TRAT]] == trat_p])

Y_prima <- (p*(R + C + T_t) - 2*G) / ((p-1)*(p-2))
cat(sprintf("G=%.2f  R(fila3)=%.2f  C(col3)=%.2f  T(Metodo C)=%.2f\n", G, R, C, T_t))
cat(sprintf("Dato estimado Y' = (4*(%.0f+%.0f+%.0f) - 2*%.0f) / (3*2) = %.4f\n",
    R, C, T_t, G, Y_prima))

df_full$Y[idx_na] <- Y_prima
df <- df_full

# ============================================================
# ANOVA con dato estimado — gl_Error = (p-1)*(p-2) - 1 = 5
# ============================================================
formula_m <- as.formula(paste("Y ~", NOMBRE_FIL, "+", NOMBRE_COL, "+", NOMBRE_TRAT))
modelo    <- aov(formula_m, data=df)
resumen   <- summary(modelo)[[1]]

sc_F <- resumen[1,"Sum Sq"]; sc_C <- resumen[2,"Sum Sq"]
sc_T <- resumen[3,"Sum Sq"]; sc_E <- resumen[4,"Sum Sq"]

gl_F <- p-1; gl_C <- p-1; gl_T <- p-1
gl_E <- (p-1)*(p-2) - 1    # = 5
cm_E <- sc_E / gl_E

alpha <- 0.05
ft_F  <- qf(1-alpha, gl_F, gl_E)
ft_C  <- qf(1-alpha, gl_C, gl_E)
ft_T  <- qf(1-alpha, gl_T, gl_E)
Fc_F  <- (sc_F/gl_F) / cm_E
Fc_C  <- (sc_C/gl_C) / cm_E
Fc_T  <- (sc_T/gl_T) / cm_E
sc_Tot <- sc_F + sc_C + sc_T + sc_E

cat(strrep("=",70), "\n")
cat("TABLA ANOVA AJUSTADA -", TITULO, "\n")
cat(strrep("=",70), "\n")
cat(sprintf("(gl_Error ajustado = %d, por dato estimado Y'=%.4f)\n\n", gl_E, Y_prima))
cat(sprintf("%-20s  GL=%d  SC=%.4f  CM=%.4f  Fc=%.4f  Ft=%.4f  %s\n",
    NOMBRE_FIL, gl_F, sc_F, sc_F/gl_F, Fc_F, ft_F, ifelse(Fc_F>ft_F,"SIGNIFICATIVO ***","no significativo")))
cat(sprintf("%-20s  GL=%d  SC=%.4f  CM=%.4f  Fc=%.4f  Ft=%.4f  %s\n",
    NOMBRE_COL, gl_C, sc_C, sc_C/gl_C, Fc_C, ft_C, ifelse(Fc_C>ft_C,"SIGNIFICATIVO ***","no significativo")))
cat(sprintf("%-20s  GL=%d  SC=%.4f  CM=%.4f  Fc=%.4f  Ft=%.4f  %s\n",
    NOMBRE_TRAT,gl_T, sc_T, sc_T/gl_T, Fc_T, ft_T, ifelse(Fc_T>ft_T,"SIGNIFICATIVO ***","no significativo")))
cat(sprintf("%-20s  GL=%d  SC=%.4f  CM=%.4f\n", "Error", gl_E, sc_E, cm_E))
cat(sprintf("%-20s  GL=%d  SC=%.4f\n", "Total", N_orig-2, sc_Tot))

# ============================================================
# PRUEBA DE TUKEY (Operador y Metodo son significativos)
# ============================================================
cat("\n--- TukeyHSD R:", NOMBRE_COL, "(nota: R usa gl_E=6 del aov, no el ajustado 5) ---\n")
tukey_C <- TukeyHSD(modelo, NOMBRE_COL); print(tukey_C)

cat("\n--- TukeyHSD R:", NOMBRE_TRAT, "(nota: R usa gl_E=6 del aov, no el ajustado 5) ---\n")
tukey_T <- TukeyHSD(modelo, NOMBRE_TRAT); print(tukey_T)

# ============================================================
# TUKEY MANUAL CORRECTO (usa cm_E=1.8, gl_E=5, ajustados)
# T_alpha = q(alpha, k, gl_E) * sqrt(CM_E / n)
# ============================================================
n_grupo <- p   # p=4 observaciones por nivel
k <- p         # k=4 niveles

q_crit   <- qtukey(1-alpha, k, gl_E)
T_alpha  <- q_crit * sqrt(cm_E / n_grupo)
cat(sprintf("\n%s\nTUKEY MANUAL CORRECTO (CM_E=%.4f, gl_E=%d)\n", strrep("=",65), cm_E, gl_E))
cat(sprintf("q(0.05,%d,%d) = %.4f   T_alpha = %.4f\n", k, gl_E, q_crit, T_alpha))

# Operador (columnas)
medias_C_vec <- sort(tapply(df$Y, df[[NOMBRE_COL]], mean), decreasing=TRUE)
cat(sprintf("\n--- %s:\n", NOMBRE_COL))
nivs_C <- names(medias_C_vec)
for (i in 1:(length(nivs_C)-1)) {
  for (j in (i+1):length(nivs_C)) {
    dif <- abs(medias_C_vec[i] - medias_C_vec[j])
    sig <- ifelse(dif > T_alpha, "SIGNIFICATIVO *", "no significativo")
    cat(sprintf("  %s vs %s: |%.4f - %.4f| = %.4f  %s T_alpha=%.4f -> %s\n",
        nivs_C[i], nivs_C[j], medias_C_vec[i], medias_C_vec[j],
        dif, ifelse(dif>T_alpha,">","<"), T_alpha, sig))
  }
}

# Metodo (tratamiento)
medias_T_vec <- sort(tapply(df$Y, df[[NOMBRE_TRAT]], mean), decreasing=TRUE)
cat(sprintf("\n--- %s:\n", NOMBRE_TRAT))
nivs_T <- names(medias_T_vec)
for (i in 1:(length(nivs_T)-1)) {
  for (j in (i+1):length(nivs_T)) {
    dif <- abs(medias_T_vec[i] - medias_T_vec[j])
    sig <- ifelse(dif > T_alpha, "SIGNIFICATIVO *", "no significativo")
    cat(sprintf("  %s vs %s: |%.4f - %.4f| = %.4f  %s T_alpha=%.4f -> %s\n",
        nivs_T[i], nivs_T[j], medias_T_vec[i], medias_T_vec[j],
        dif, ifelse(dif>T_alpha,">","<"), T_alpha, sig))
  }
}

# ============================================================
# GRAFICAS  (ESTILO DISTINTIVO DE R: serif + viridis + sello)
# ============================================================
theme_R <- theme_minimal(base_family = "serif", base_size = 12) +
  theme(plot.title       = element_text(face = "bold", color = "#4b0082"),
        panel.background = element_rect(fill = "#faf7fb", color = NA),
        panel.grid.minor = element_blank(),
        legend.position  = "bottom")
PALETA_R <- c("#440154","#3b528b","#21918c","#5ec962")
ACCENT_R <- "#4b0082"
SELLO_R  <- "Generado en R 4.6  |  ggplot2  |  aov + Yates + Tukey manual"
mg <- mean(df$Y)

df_pF <- data.frame(Niv=levels(df[[NOMBRE_FIL]]),  Med=tapply(df$Y,df[[NOMBRE_FIL]],mean))
df_pC <- data.frame(Niv=levels(df[[NOMBRE_COL]]),  Med=tapply(df$Y,df[[NOMBRE_COL]],mean))
df_pT <- data.frame(Niv=levels(df[[NOMBRE_TRAT]]), Med=tapply(df$Y,df[[NOMBRE_TRAT]],mean))

# Grafica barras filas
p1 <- ggplot(df_pF,aes(x=Niv,y=Med))+geom_bar(stat="identity",fill=PALETA_R[1],color="black")+
  geom_hline(yintercept=mg,color="red",linetype="dashed",linewidth=1.2)+
  labs(title=paste("Medias por",NOMBRE_FIL),x=NOMBRE_FIL,y=RESPUESTA)+theme_R+
  theme(plot.title=element_text(size=11),
        axis.text.x=element_text(angle=30,hjust=1))

# Grafica barras Operador (columnas)
p2 <- ggplot(df_pC,aes(x=Niv,y=Med))+geom_bar(stat="identity",fill=PALETA_R[3],color="black")+
  geom_hline(yintercept=mg,color="red",linetype="dashed",linewidth=1.2)+
  labs(title=paste("Medias por",NOMBRE_COL),x=NOMBRE_COL,y=RESPUESTA)+theme_R+
  theme(plot.title=element_text(size=11))

# Grafica barras Metodo (tratamiento)
p3 <- ggplot(df_pT,aes(x=Niv,y=Med))+geom_bar(stat="identity",fill=PALETA_R[4],color="black")+
  geom_hline(yintercept=mg,color="red",linetype="dashed",linewidth=1.2)+
  labs(title=paste("Medias por",NOMBRE_TRAT,"(con Y'=13)"),x=NOMBRE_TRAT,y=RESPUESTA)+theme_R+
  theme(plot.title=element_text(size=11))

# Helper Tukey manual (gl_E ajustado = 5) -> el grafico coincide con la consola
make_tukey_comps <- function(factor_name) {
  T_a  <- qtukey(0.95, k, gl_E) * sqrt(cm_E / n_grupo)
  meds <- tapply(df$Y, df[[factor_name]], mean)
  nv   <- names(meds)
  out  <- data.frame(Comp=character(), diff=numeric(), lwr=numeric(), upr=numeric(), Sig=logical(), stringsAsFactors=FALSE)
  for (i in 1:(length(nv)-1)) for (j in (i+1):length(nv)) {
    d <- meds[nv[i]] - meds[nv[j]]
    out <- rbind(out, data.frame(Comp=paste0(nv[i],"-",nv[j]), diff=d, lwr=d-T_a, upr=d+T_a, Sig=abs(d)>T_a, stringsAsFactors=FALSE))
  }
  out
}

# Tukey Operador (manual, gl_E=5)
comps_C <- make_tukey_comps(NOMBRE_COL)
p4 <- ggplot(comps_C,aes(y=reorder(Comp,diff),x=diff))+
  geom_errorbarh(aes(xmin=lwr,xmax=upr,color=Sig),height=0.4,linewidth=1)+
  geom_point(aes(color=Sig),size=3)+geom_vline(xintercept=0,linetype="dashed")+
  scale_color_manual(values=c("TRUE"="#c2185b","FALSE"="#3b528b"),
                     labels=c("TRUE"="Sig.","FALSE"="No sig."),name="")+
  labs(title=paste("Tukey manual -",NOMBRE_COL,"(gl_E =",gl_E,")"),x="Dif. medias (IC 95%)",y="")+
  theme_R+theme(plot.title=element_text(size=11))

# Tukey Metodo (manual, gl_E=5)
comps_T <- make_tukey_comps(NOMBRE_TRAT)
p5 <- ggplot(comps_T,aes(y=reorder(Comp,diff),x=diff))+
  geom_errorbarh(aes(xmin=lwr,xmax=upr,color=Sig),height=0.4,linewidth=1)+
  geom_point(aes(color=Sig),size=3)+geom_vline(xintercept=0,linetype="dashed")+
  scale_color_manual(values=c("TRUE"="#c2185b","FALSE"="#21918c"),
                     labels=c("TRUE"="Sig.","FALSE"="No sig."),name="")+
  labs(title=paste("Tukey manual -",NOMBRE_TRAT,"(gl_E =",gl_E,")"),x="Dif. medias (IC 95%)",y="")+
  theme_R+theme(plot.title=element_text(size=11))

# Tabla ANOVA ajustada (grob)
tbl_df <- data.frame(
  "Fuente"   = c(NOMBRE_FIL, NOMBRE_COL, NOMBRE_TRAT, paste0("Error (gl=",gl_E,")"), "Total"),
  "GL"       = c(gl_F, gl_C, gl_T, gl_E, N_orig-2),
  "SC"       = round(c(sc_F,sc_C,sc_T,sc_E,sc_Tot),4),
  "CM"       = c(round(sc_F/gl_F,4),round(sc_C/gl_C,4),round(sc_T/gl_T,4),round(cm_E,4),"-"),
  "Fc"       = c(round(Fc_F,4),round(Fc_C,4),round(Fc_T,4),"-","-"),
  "Ft"       = c(round(ft_F,4),round(ft_C,4),round(ft_T,4),"-","-"),
  "Decision" = c(ifelse(Fc_F>ft_F,"Sig ***","No sig"),ifelse(Fc_C>ft_C,"Sig ***","No sig"),
                 ifelse(Fc_T>ft_T,"Sig ***","No sig"),"-","-"),
  check.names=FALSE, stringsAsFactors=FALSE)

tema <- gridExtra::ttheme_default(
  core   =list(bg_params=list(fill=c("#efeaf5","#d9f2ee","#d9f2ee","#faf7fb","#e8e4f0")),
               fg_params=list(fontsize=8, fontfamily="serif")),
  colhead=list(bg_params=list(fill="#4b0082"),fg_params=list(col="white",fontsize=8.5,fontface="bold",fontfamily="serif")))
p_tbl <- gridExtra::arrangeGrob(
  grid::textGrob(paste0("Tabla ANOVA - CL Dato Perdido  (Y'=",round(Y_prima,4),
                        ", gl_E=",gl_E,")"),
                 gp=grid::gpar(fontsize=10,fontface="bold",fontfamily="serif",col="#4b0082")),
  gridExtra::tableGrob(tbl_df,rows=NULL,theme=tema), ncol=1, heights=c(0.16,1))

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

# PNG 1: graficas + tukey (paneles reordenados: Tukey arriba, distinto de Python)
titulo_g <- grid::textGrob(TITULO, gp=grid::gpar(fontsize=12, fontface="bold",
                                                 fontfamily="serif", col="#4b0082"))
sello_g  <- grid::textGrob(SELLO_R, gp=grid::gpar(fontsize=11, fontface="italic",
                                                  fontfamily="serif", col=ACCENT_R))
lay <- rbind(c(4,4,5), c(1,2,3))
png(ruta, width=1600, height=1100, res=130)
print(grid.arrange(p1,p2,p3,p4,p5, layout_matrix=lay, top=titulo_g, bottom=sello_g))
dev.off()
cat("\nGrafica guardada:", ruta, "\n")

# PNG 2: tabla ANOVA
png(ruta_t, width=1200, height=440, res=130)
print(grid.arrange(p_tbl, bottom=sello_g))
dev.off()
cat("Tabla  guardada:", ruta_t, "\n")
