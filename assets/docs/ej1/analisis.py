"""
Diseño Factorial 2^2 - Efecto del tamaño de broca y velocidad sobre vibración
Factor A: Tamaño de broca (1/16 y 1/8 de pulgada)
Factor B: Velocidad (40 y 90 rpm)
Respuesta Y: Vibración
4 réplicas por combinación → 16 corridas totales
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from statsmodels.formula.api import ols
from statsmodels.stats.anova import anova_lm
from statsmodels.stats.multicomp import pairwise_tukeyhsd
import warnings
warnings.filterwarnings("ignore")

# ─────────────────────────────────────────────
# 1. DATOS
# ─────────────────────────────────────────────
data = {
    "Broca":     ["1/16"]*4 + ["1/8"]*4 + ["1/16"]*4 + ["1/8"]*4,
    "Velocidad": ([40]*4 + [40]*4 + [90]*4 + [90]*4),
    "Vibracion": [
        18.2, 18.9, 12.9, 14.4,   # Broca=1/16, Vel=40
        27.2, 24.0, 22.4, 22.5,   # Broca=1/8,  Vel=40
        15.9, 14.5, 15.1, 14.2,   # Broca=1/16, Vel=90
        41.0, 43.9, 36.3, 39.9,   # Broca=1/8,  Vel=90
    ]
}

df = pd.DataFrame(data)
df["Broca"] = df["Broca"].astype("category")
df["Velocidad"] = df["Velocidad"].astype("category")
df["Grupo"] = df["Broca"].astype(str) + " | " + df["Velocidad"].astype(str) + " rpm"

print("=" * 60)
print("  DISEÑO FACTORIAL 2² — Broca × Velocidad → Vibración")
print("=" * 60)

# ─────────────────────────────────────────────
# 2. ESTADÍSTICAS DESCRIPTIVAS
# ─────────────────────────────────────────────
resumen = df.groupby(["Broca", "Velocidad"])["Vibracion"].agg(
    n="count", Media="mean", SD="std", Min="min", Max="max"
).round(3)
print("\nEstadísticas descriptivas por tratamiento:\n")
print(resumen.to_string())

# ─────────────────────────────────────────────
# 3. ANOVA FACTORIAL
# ─────────────────────────────────────────────
modelo = ols("Vibracion ~ C(Broca) * C(Velocidad)", data=df).fit()
tabla_anova = anova_lm(modelo, typ=2)

print("\n\nTabla ANOVA:\n")
print(tabla_anova.round(4).to_string())

# Efectos principales e interacción
SS_A   = tabla_anova.loc["C(Broca)", "sum_sq"]
SS_B   = tabla_anova.loc["C(Velocidad)", "sum_sq"]
SS_AB  = tabla_anova.loc["C(Broca):C(Velocidad)", "sum_sq"]
SS_E   = tabla_anova.loc["Residual", "sum_sq"]
SS_T   = SS_A + SS_B + SS_AB + SS_E

print(f"\nR² del modelo = {modelo.rsquared:.4f}")
print(f"R² ajustado   = {modelo.rsquared_adj:.4f}")

# ─────────────────────────────────────────────
# 4. PRUEBA DE TUKEY HSD
# ─────────────────────────────────────────────
tukey = pairwise_tukeyhsd(endog=df["Vibracion"], groups=df["Grupo"], alpha=0.05)
print("\n\nPrueba de Tukey HSD (α = 0.05):\n")
print(tukey.summary())

# Extraer resultados de Tukey
tukey_df = pd.DataFrame(
    data=tukey._results_table.data[1:],
    columns=tukey._results_table.data[0]
)

# ─────────────────────────────────────────────
# 5. GRÁFICOS
# ─────────────────────────────────────────────
colores = {"1/16 | 40 rpm": "#2196F3", "1/8 | 40 rpm": "#FF5722",
           "1/16 | 90 rpm": "#4CAF50", "1/8 | 90 rpm": "#9C27B0"}

fig = plt.figure(figsize=(18, 14))
fig.patch.set_facecolor("#F8F9FA")
gs = gridspec.GridSpec(2, 3, figure=fig, hspace=0.42, wspace=0.38)

# ── 5a. Gráfico de interacción ─────────────────
ax1 = fig.add_subplot(gs[0, 0])
medias = df.groupby(["Broca", "Velocidad"])["Vibracion"].mean().unstack()
for vel, color, marker in zip([40, 90], ["#2196F3", "#FF5722"], ["o", "s"]):
    ax1.plot(medias.index, medias[vel], marker=marker, linewidth=2.2,
             markersize=8, color=color, label=f"Velocidad {vel} rpm")
ax1.set_title("Gráfico de Interacción A×B", fontweight="bold", fontsize=12)
ax1.set_xlabel("Tamaño de Broca (pulgadas)")
ax1.set_ylabel("Vibración media")
ax1.legend(fontsize=9)
ax1.grid(True, alpha=0.3)
ax1.set_facecolor("#FFFFFF")

# ── 5b. Medias por grupo (barras) ─────────────
ax2 = fig.add_subplot(gs[0, 1])
medias_grupo = df.groupby("Grupo")["Vibracion"].mean()
barras_col = [colores.get(g, "#607D8B") for g in medias_grupo.index]
bars = ax2.bar(range(len(medias_grupo)), medias_grupo.values,
               color=barras_col, edgecolor="white", linewidth=1.5, width=0.6)
ax2.set_xticks(range(len(medias_grupo)))
ax2.set_xticklabels(medias_grupo.index, rotation=15, ha="right", fontsize=8.5)
ax2.set_title("Media de Vibración por Tratamiento", fontweight="bold", fontsize=12)
ax2.set_ylabel("Vibración media")
for bar, val in zip(bars, medias_grupo.values):
    ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.4,
             f"{val:.2f}", ha="center", va="bottom", fontsize=9, fontweight="bold")
ax2.grid(axis="y", alpha=0.3)
ax2.set_facecolor("#FFFFFF")

# ── 5c. Boxplot por grupo ─────────────────────
ax3 = fig.add_subplot(gs[0, 2])
grupos_orden = sorted(df["Grupo"].unique())
datos_box = [df[df["Grupo"] == g]["Vibracion"].values for g in grupos_orden]
bp = ax3.boxplot(datos_box, patch_artist=True, notch=False,
                 medianprops=dict(color="white", linewidth=2.5))
for patch, g in zip(bp["boxes"], grupos_orden):
    patch.set_facecolor(colores.get(g, "#607D8B"))
    patch.set_alpha(0.85)
ax3.set_xticks(range(1, len(grupos_orden) + 1))
ax3.set_xticklabels(grupos_orden, rotation=15, ha="right", fontsize=8.5)
ax3.set_title("Distribución por Tratamiento", fontweight="bold", fontsize=12)
ax3.set_ylabel("Vibración")
ax3.grid(axis="y", alpha=0.3)
ax3.set_facecolor("#FFFFFF")

# ── 5d. Tukey HSD — Intervalos de confianza ───
ax4 = fig.add_subplot(gs[1, :2])
tukey_res = tukey.summary()
comparaciones = []
for row in tukey._results_table.data[1:]:
    comparaciones.append({
        "par":      f"{row[0]}  vs  {row[1]}",
        "diff":     float(row[2]),
        "lower":    float(row[3]),
        "upper":    float(row[4]),
        "reject":   row[5]
    })
comp_df = pd.DataFrame(comparaciones)
colores_bar = ["#E53935" if r else "#43A047" for r in comp_df["reject"]]
y_pos = range(len(comp_df))
xerr_lo = (comp_df["diff"] - comp_df["lower"]).abs()
xerr_hi = (comp_df["upper"] - comp_df["diff"]).abs()
ax4.barh(y_pos, comp_df["diff"], xerr=[xerr_lo, xerr_hi],
         color=colores_bar, edgecolor="white", height=0.55,
         error_kw=dict(ecolor="#333333", capsize=5, linewidth=1.8))
ax4.axvline(0, color="black", linewidth=1.5, linestyle="--")
ax4.set_yticks(list(y_pos))
ax4.set_yticklabels(comp_df["par"], fontsize=9)
ax4.set_xlabel("Diferencia de medias (con IC 95%)")
ax4.set_title("Prueba de Tukey HSD — Diferencias de Medias\n"
              "🔴 Diferencia significativa   🟢 No significativa", fontweight="bold", fontsize=12)
ax4.grid(axis="x", alpha=0.3)
ax4.set_facecolor("#FFFFFF")

# ── 5e. Diagnóstico: residuos ─────────────────
ax5 = fig.add_subplot(gs[1, 2])
residuos = modelo.resid
valores_ajust = modelo.fittedvalues
ax5.scatter(valores_ajust, residuos, color="#5C6BC0", alpha=0.8, edgecolors="white",
            s=70, linewidth=0.8)
ax5.axhline(0, color="#E53935", linewidth=1.5, linestyle="--")
ax5.set_xlabel("Valores ajustados")
ax5.set_ylabel("Residuos")
ax5.set_title("Residuos vs Valores Ajustados", fontweight="bold", fontsize=12)
ax5.grid(True, alpha=0.3)
ax5.set_facecolor("#FFFFFF")

# Título general
fig.suptitle("Diseño Factorial 2² — Broca × Velocidad → Vibración\n"
             "Análisis ANOVA con Prueba de Tukey HSD",
             fontsize=14, fontweight="bold", y=1.01)

plt.savefig("/mnt/user-data/outputs/factorial_python.png",
            dpi=160, bbox_inches="tight", facecolor=fig.get_facecolor())
plt.close()

print("\n✔ Gráfico guardado: factorial_python.png")

# ─────────────────────────────────────────────
# 6. RESUMEN EJECUTIVO
# ─────────────────────────────────────────────
alpha = 0.05
print("\n" + "=" * 60)
print("  RESUMEN EJECUTIVO")
print("=" * 60)
for fuente in ["C(Broca)", "C(Velocidad)", "C(Broca):C(Velocidad)"]:
    p = tabla_anova.loc[fuente, "PR(>F)"]
    sig = "SIGNIFICATIVO ✔" if p < alpha else "No significativo"
    nombre = fuente.replace("C(", "").replace(")", "").replace(":", " × ")
    print(f"  {nombre:30s}  p = {p:.4f}  →  {sig}")
