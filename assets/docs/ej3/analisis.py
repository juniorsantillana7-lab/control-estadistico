import matplotlib
matplotlib.use('Agg')
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from statsmodels.formula.api import ols
from statsmodels.stats.anova import anova_lm
from scipy.stats import f as f_dist, studentized_range
import os, warnings
warnings.filterwarnings('ignore')

# ============================================================
# PROBLEMA #3 - Cuadrado Latino 4x4
# Inspectores (filas) x Escalas (columnas) x Proveedores (trat)
# ============================================================

TITULO      = "PROBLEMA #3 - Peso en gramos por Proveedor"
NOMBRE_FIL  = "Inspector"
NOMBRE_COL  = "Escala"
NOMBRE_TRAT = "Proveedor"
RESPUESTA   = "Peso (g)"
PREFIJO_OUT = "P3"

p = 4

cuadrado = [
    ["A", "B", "C", "D"],
    ["B", "C", "D", "A"],
    ["C", "D", "A", "B"],
    ["D", "A", "B", "C"],
]

y_mat = [
    [16, 10, 11, 13],
    [15,  9, 14, 13],
    [13, 12, 17, 14],
    [16, 15, 13, 11],
]

# ============================================================
# Construccion del DataFrame
# ============================================================
N = p * p; alpha = 0.05
filas_idx = [f"I{i+1}" for i in range(p)]
cols_idx  = [f"E{j+1}" for j in range(p)]

fila_col, col_col, trat_col, y_col = [], [], [], []
for i in range(p):
    for j in range(p):
        fila_col.append(filas_idx[i])
        col_col.append(cols_idx[j])
        trat_col.append(cuadrado[i][j])
        y_col.append(y_mat[i][j])

df = pd.DataFrame({
    NOMBRE_FIL:  pd.Categorical(fila_col,  categories=filas_idx),
    NOMBRE_COL:  pd.Categorical(col_col,   categories=cols_idx),
    NOMBRE_TRAT: pd.Categorical(trat_col,  categories=sorted(set(trat_col))),
    'Y': y_col
})

# ============================================================
# HIPOTESIS
# ============================================================
print("=" * 65)
print("HIPOTESIS")
print("=" * 65)
print("H0: No hay diferencia significativa entre proveedores (uA=uB=uC=uD)")
print("H1: Al menos un proveedor difiere significativamente")
print("H0 filas: No hay diferencia significativa entre inspectores")
print("H0 cols:  No hay diferencia significativa entre escalas")

# ============================================================
# ANOVA - Cuadrado Latino
# ============================================================
formula = f"Y ~ C({NOMBRE_FIL}) + C({NOMBRE_COL}) + C({NOMBRE_TRAT})"
modelo  = ols(formula, data=df).fit()
tabla_anova = anova_lm(modelo, typ=2)

print("\n" + "=" * 65)
print(f"TABLA ANOVA - {TITULO}")
print("=" * 65)
print(tabla_anova.round(4))

gl_F = p-1; gl_C = p-1; gl_T = p-1; gl_E = (p-1)*(p-2)
ft_F = f_dist.ppf(1-alpha, gl_F, gl_E)
ft_C = f_dist.ppf(1-alpha, gl_C, gl_E)
ft_T = f_dist.ppf(1-alpha, gl_T, gl_E)

key_F = f"C({NOMBRE_FIL})"
key_C = f"C({NOMBRE_COL})"
key_T = f"C({NOMBRE_TRAT})"
Fc_F  = tabla_anova.loc[key_F, 'F']
Fc_C  = tabla_anova.loc[key_C, 'F']
Fc_T  = tabla_anova.loc[key_T, 'F']

print(f"\nFt Inspector ({gl_F},{gl_E}) = {ft_F:.4f} | Fc={Fc_F:.4f} -> {'SIGNIFICATIVO' if Fc_F>ft_F else 'no sig.'}")
print(f"Ft Escala    ({gl_C},{gl_E}) = {ft_C:.4f} | Fc={Fc_C:.4f} -> {'SIGNIFICATIVO' if Fc_C>ft_C else 'no sig.'}")
print(f"Ft Proveedor ({gl_T},{gl_E}) = {ft_T:.4f} | Fc={Fc_T:.4f} -> {'SIGNIFICATIVO' if Fc_T>ft_T else 'no sig.'}")

# ============================================================
# TUKEY MANUAL - Proveedor (correcto para Cuadrado Latino)
# T_alpha = q(alpha, k, gl_E) * sqrt(CM_E / p)
# NOTA: pairwise_tukeyhsd ignora bloques -> MSE inflado -> INCORRECTO
# ============================================================
sc_E_v  = tabla_anova.loc['Residual', 'sum_sq']
cm_E_v  = sc_E_v / gl_E
q_T     = studentized_range.ppf(0.95, p, gl_E)
T_alpha_T = q_T * np.sqrt(cm_E_v / p)

medias_T = df.groupby(NOMBRE_TRAT, observed=True)['Y'].mean().sort_values(ascending=False)

print("\n" + "="*65)
print(f"TUKEY MANUAL - {NOMBRE_TRAT}")
print(f"  CM_E={cm_E_v:.4f}  gl_E={gl_E}  n={p}")
print(f"  q(0.05,{p},{gl_E})={q_T:.4f}   T_alpha={T_alpha_T:.4f}")
print("="*65)
nivs_T = medias_T.index.tolist()
for i in range(len(nivs_T)):
    for j in range(i+1, len(nivs_T)):
        ni, nj = nivs_T[i], nivs_T[j]
        dif = abs(medias_T[ni] - medias_T[nj])
        sig = "SIGNIFICATIVO *" if dif > T_alpha_T else "no significativo"
        print(f"  {ni} vs {nj}: |{medias_T[ni]:.4f}-{medias_T[nj]:.4f}| = {dif:.4f} {'>' if dif>T_alpha_T else '<'} {T_alpha_T:.4f} -> {sig}")

# ============================================================
# Helper: grafica de intervalos Tukey (manual)
# ============================================================
def _tukey_plot(ax, medias, T_alpha, titulo):
    niv = medias.sort_values().index.tolist()
    pares = []
    for i in range(len(niv)):
        for j in range(i+1, len(niv)):
            ni, nj = niv[i], niv[j]
            diff = float(medias[nj] - medias[ni])
            pares.append((f"{nj}-{ni}", diff, diff - T_alpha, diff + T_alpha))
    for idx, (lbl, diff, lo, hi) in enumerate(pares):
        sig = (lo > 0) or (hi < 0)
        col = 'red' if sig else 'steelblue'
        ax.plot([lo, hi], [idx, idx], color=col, linewidth=2)
        ax.plot(diff, idx, 'o', color=col, markersize=5)
    ax.set_yticks(range(len(pares)))
    ax.set_yticklabels([p[0] for p in pares], fontsize=9)
    ax.axvline(0, color='black', linewidth=0.8, linestyle='--')
    ax.set_title(titulo, fontweight='bold')
    ax.set_xlabel('Diferencia de medias (IC 95%)')
    ax.grid(alpha=0.3, axis='x')

# ============================================================
# FIGURA 1: Graficas
# ============================================================
mg = df['Y'].mean()
fig = plt.figure(figsize=(16, 11))
fig.suptitle(TITULO + f"\n(Variable respuesta: {RESPUESTA})", fontsize=14, fontweight='bold')
gs = gridspec.GridSpec(2, 3, figure=fig, hspace=0.45, wspace=0.35,
                       top=0.83, bottom=0.07, left=0.07, right=0.97)

ax1 = fig.add_subplot(gs[0, 0])
med_F = df.groupby(NOMBRE_FIL, observed=True)['Y'].mean()
ax1.bar(med_F.index, med_F.values, color='#7fb3d3', edgecolor='black')
ax1.axhline(mg, color='red', linestyle='--', linewidth=1.5, label='Media global')
ax1.set_title(f'Medias por {NOMBRE_FIL}', fontweight='bold')
ax1.set_xlabel(NOMBRE_FIL); ax1.set_ylabel(RESPUESTA)
ax1.legend(fontsize=8); ax1.grid(axis='y', alpha=0.3)

ax2 = fig.add_subplot(gs[0, 1])
med_C = df.groupby(NOMBRE_COL, observed=True)['Y'].mean()
ax2.bar(med_C.index, med_C.values, color='#f0a070', edgecolor='black')
ax2.axhline(mg, color='red', linestyle='--', linewidth=1.5, label='Media global')
ax2.set_title(f'Medias por {NOMBRE_COL}', fontweight='bold')
ax2.set_xlabel(NOMBRE_COL); ax2.set_ylabel(RESPUESTA)
ax2.legend(fontsize=8); ax2.grid(axis='y', alpha=0.3)

ax3 = fig.add_subplot(gs[0, 2])
med_T = df.groupby(NOMBRE_TRAT, observed=True)['Y'].mean()
ax3.bar(med_T.index, med_T.values, color='#82c982', edgecolor='black')
ax3.axhline(mg, color='red', linestyle='--', linewidth=1.5, label='Media global')
ax3.set_title(f'Medias por {NOMBRE_TRAT}', fontweight='bold')
ax3.set_xlabel(NOMBRE_TRAT); ax3.set_ylabel(RESPUESTA)
ax3.legend(fontsize=8); ax3.grid(axis='y', alpha=0.3)

ax4 = fig.add_subplot(gs[1, :])
_tukey_plot(ax4, medias_T, T_alpha_T, f'Prueba de Tukey - {NOMBRE_TRAT} (IC 95% manual correcto)')

BASE  = os.path.dirname(os.path.abspath(__file__))
SELLO_PY = "Generado en Python  |  matplotlib  |  statsmodels (ANOVA) + scipy (Tukey)"
fig.text(0.5, 0.012, SELLO_PY, ha='center', va='bottom', fontsize=13,
         style='italic', fontweight='bold', color='#1a5276',
         bbox=dict(boxstyle='round,pad=0.4', facecolor='#eaf2f8', edgecolor='#1a5276', linewidth=1.2))
ruta1 = os.path.join(BASE, 'python_1.png')
plt.savefig(ruta1, dpi=150, bbox_inches='tight'); plt.close()
print(f"\nGrafica guardada: {ruta1}")

# ============================================================
# FIGURA 2: Tabla ANOVA (imagen separada)
# ============================================================
sc_F   = tabla_anova.loc[key_F, 'sum_sq']
sc_C   = tabla_anova.loc[key_C, 'sum_sq']
sc_T   = tabla_anova.loc[key_T, 'sum_sq']
sc_E   = sc_E_v
sc_Tot = sc_F + sc_C + sc_T + sc_E

dec_F = 'Significativo ***' if Fc_F > ft_F else 'No significativo'
dec_C = 'Significativo ***' if Fc_C > ft_C else 'No significativo'
dec_T = 'Significativo ***' if Fc_T > ft_T else 'No significativo'

encab = ['Fuente de Variacion', 'GL', 'SC', 'CM', 'Fc', 'Ft (a=5%)', 'Conclusion']
filas = [
    [NOMBRE_FIL,  str(gl_F), f'{sc_F:.4f}', f'{sc_F/gl_F:.4f}', f'{Fc_F:.4f}', f'{ft_F:.4f}', dec_F],
    [NOMBRE_COL,  str(gl_C), f'{sc_C:.4f}', f'{sc_C/gl_C:.4f}', f'{Fc_C:.4f}', f'{ft_C:.4f}', dec_C],
    [NOMBRE_TRAT, str(gl_T), f'{sc_T:.4f}', f'{sc_T/gl_T:.4f}', f'{Fc_T:.4f}', f'{ft_T:.4f}', dec_T],
    ['Error',     str(gl_E), f'{sc_E:.4f}', f'{sc_E/gl_E:.4f}', '-',           '-',           '-'  ],
    ['Total',     str(N-1),  f'{sc_Tot:.4f}','-',               '-',           '-',           '-'  ],
]
todas = [encab] + filas

fig2, ax_t = plt.subplots(figsize=(14, 4))
ax_t.set_xlim(0,1); ax_t.set_ylim(0,1); ax_t.axis('off')
fig2.suptitle(f'Tabla ANOVA - Cuadrado Latino\n{TITULO}',
              fontsize=13, fontweight='bold', y=0.98)

col_x  = [0.00, 0.26, 0.34, 0.46, 0.56, 0.66, 0.78, 1.00]
n_fil  = len(todas); row_h = 0.82/n_fil; y_start = 0.88
sig_map = [Fc_F > ft_F, Fc_C > ft_C, Fc_T > ft_T]  # Inspector, Escala, Proveedor

for i, fila in enumerate(todas):
    y_top = y_start - i*row_h; y_bot = y_top - row_h; y_mid = (y_top+y_bot)/2
    if   i == 0:        bg, fg, fw = '#2c3e50','white','bold'
    elif 1 <= i <= 3:   bg, fg, fw = ('#d5f5e3' if sig_map[i-1] else '#ebebeb'),'black','normal'
    elif i == 4:        bg, fg, fw = '#fdfefe','black','normal'
    else:               bg, fg, fw = '#eaecee','black','normal'
    for j, texto in enumerate(fila):
        x0, x1 = col_x[j], col_x[j+1]
        rect = plt.Rectangle((x0,y_bot), x1-x0, row_h, facecolor=bg,
                              edgecolor='#555555', linewidth=0.8,
                              transform=ax_t.transAxes, clip_on=True)
        ax_t.add_patch(rect)
        ax_t.text((x0+x1)/2, y_mid, texto, ha='center', va='center', fontsize=11,
                  color=fg, fontweight=fw, transform=ax_t.transAxes, clip_on=True)

fig2.text(0.5, 0.01, SELLO_PY, ha='center', va='bottom', fontsize=12,
          style='italic', fontweight='bold', color='#1a5276',
          bbox=dict(boxstyle='round,pad=0.4', facecolor='#eaf2f8', edgecolor='#1a5276', linewidth=1.2))
ruta2 = os.path.join(BASE, 'python_2.png')
plt.savefig(ruta2, dpi=150, bbox_inches='tight'); plt.close()
print(f"Tabla ANOVA guardada: {ruta2}")
