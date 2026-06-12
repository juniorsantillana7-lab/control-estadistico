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
# PROBLEMA 2 - Cuadrado Latino 4x4 con Dato Perdido
# Fila=Orden_Montaje, Columna=Operador, Tratamiento=Metodo
# ============================================================

TITULO      = "PROBLEMA 2 - Cuadrado Latino 4x4 con Dato Perdido"
NOMBRE_FIL  = "Orden_Montaje"
NOMBRE_COL  = "Operador"
NOMBRE_TRAT = "Metodo"
RESPUESTA   = "Y"
PREFIJO_OUT = "P2"

p = 4

# Cuadrado latino: fila 3, col 3 = tratamiento C (dato perdido)
cuadrado = [
    ["C","D","A","B"],
    ["B","C","D","A"],
    ["A","B","C","D"],
    ["D","A","B","C"],
]

# Observaciones: None = dato perdido (fila 3, col 3)
y_mat = [
    [10, 14,  7,  8],
    [ 7, 18, 11,  8],
    [ 5, 10, None, 9],
    [10, 10, 12, 14],
]

# ============================================================
# Construir DataFrame
# ============================================================
N_orig = p * p
alpha  = 0.05
filas_idx = [f"F{i+1}" for i in range(p)]
cols_idx  = [f"C{j+1}" for j in range(p)]

fila_col, col_col, trat_col, y_col = [], [], [], []
for i in range(p):
    for j in range(p):
        fila_col.append(filas_idx[i])
        col_col.append(cols_idx[j])
        trat_col.append(cuadrado[i][j])
        y_col.append(np.nan if y_mat[i][j] is None else float(y_mat[i][j]))

df_full = pd.DataFrame({
    NOMBRE_FIL:  pd.Categorical(fila_col,  categories=filas_idx),
    NOMBRE_COL:  pd.Categorical(col_col,   categories=cols_idx),
    NOMBRE_TRAT: pd.Categorical(trat_col,  categories=sorted(set(trat_col))),
    'Y': y_col
})

idx_na = df_full['Y'].isna()
row_na = df_full[idx_na].iloc[0]
fila_p = row_na[NOMBRE_FIL]; col_p = row_na[NOMBRE_COL]; trat_p = row_na[NOMBRE_TRAT]
print(f"Dato perdido: {NOMBRE_FIL}={fila_p} | {NOMBRE_COL}={col_p} | {NOMBRE_TRAT}={trat_p}")

# ============================================================
# FORMULA DE YATES  (CORRECTA)
# Y' = (p*(R + C + T) - 2*G) / ((p-1)*(p-2))
# ============================================================
df_sin = df_full.dropna(subset=['Y'])
G     = df_sin['Y'].sum()
R     = df_sin[df_sin[NOMBRE_FIL]  == fila_p]['Y'].sum()
C_col = df_sin[df_sin[NOMBRE_COL]  == col_p]['Y'].sum()
T_t   = df_sin[df_sin[NOMBRE_TRAT] == trat_p]['Y'].sum()

Y_prima = (p*(R + C_col + T_t) - 2*G) / ((p-1)*(p-2))
print(f"G={G:.0f}  R(fila3)={R:.0f}  C(col3)={C_col:.0f}  T(Metodo C)={T_t:.0f}")
print(f"Y' = (4*({R:.0f}+{C_col:.0f}+{T_t:.0f}) - 2*{G:.0f}) / (3*2) = {Y_prima:.4f}")

df_full.loc[idx_na, 'Y'] = Y_prima
df = df_full.copy()

# ============================================================
# ANOVA con dato estimado
# gl_Error = (p-1)*(p-2) - 1 = 5
# ============================================================
formula = f"Y ~ C({NOMBRE_FIL}) + C({NOMBRE_COL}) + C({NOMBRE_TRAT})"
modelo  = ols(formula, data=df).fit()
tabla_anova = anova_lm(modelo, typ=2)

key_F = f"C({NOMBRE_FIL})"; key_C = f"C({NOMBRE_COL})"; key_T = f"C({NOMBRE_TRAT})"
sc_F = tabla_anova.loc[key_F, 'sum_sq']
sc_C = tabla_anova.loc[key_C, 'sum_sq']
sc_T = tabla_anova.loc[key_T, 'sum_sq']
sc_E = tabla_anova.loc['Residual', 'sum_sq']
sc_Tot = sc_F + sc_C + sc_T + sc_E

gl_F = p-1; gl_C = p-1; gl_T = p-1
gl_E = (p-1)*(p-2) - 1    # = 5
cm_E = sc_E / gl_E

ft_F = f_dist.ppf(1-alpha, gl_F, gl_E)
ft_C = f_dist.ppf(1-alpha, gl_C, gl_E)
ft_T = f_dist.ppf(1-alpha, gl_T, gl_E)
Fc_F = (sc_F/gl_F) / cm_E
Fc_C = (sc_C/gl_C) / cm_E
Fc_T = (sc_T/gl_T) / cm_E

print("\n" + "="*70)
print(f"TABLA ANOVA AJUSTADA - {TITULO}")
print(f"(gl_Error = {gl_E}, Y' = {Y_prima:.4f})")
print("="*70)
print(f"  {NOMBRE_FIL:<18} GL={gl_F} SC={sc_F:.4f} CM={sc_F/gl_F:.4f} Fc={Fc_F:.4f} Ft={ft_F:.4f}  -> {'SIGNIFICATIVO ***' if Fc_F>ft_F else 'no significativo'}")
print(f"  {NOMBRE_COL:<18} GL={gl_C} SC={sc_C:.4f} CM={sc_C/gl_C:.4f} Fc={Fc_C:.4f} Ft={ft_C:.4f}  -> {'SIGNIFICATIVO ***' if Fc_C>ft_C else 'no significativo'}")
print(f"  {NOMBRE_TRAT:<18} GL={gl_T} SC={sc_T:.4f} CM={sc_T/gl_T:.4f} Fc={Fc_T:.4f} Ft={ft_T:.4f}  -> {'SIGNIFICATIVO ***' if Fc_T>ft_T else 'no significativo'}")
print(f"  {'Error':<18} GL={gl_E} SC={sc_E:.4f} CM={cm_E:.4f}")
print(f"  {'Total':<18} GL={N_orig-2} SC={sc_Tot:.4f}")

# ============================================================
# TUKEY MANUAL CORRECTO — Operador y Metodo (usa cm_E ajustado)
# T_alpha = q(alpha, k, gl_E) * sqrt(CM_E / p)
# NOTA: pairwise_tukeyhsd ignora bloques y gl_E ajustado -> INCORRECTO
# ============================================================
k_C = df[NOMBRE_COL].nunique()
k_T = df[NOMBRE_TRAT].nunique()
n_grupo = p  # cada nivel tiene p=4 observaciones

q_C = studentized_range.ppf(1-alpha, k_C, gl_E)
q_T = studentized_range.ppf(1-alpha, k_T, gl_E)
T_alpha_C = q_C * np.sqrt(cm_E / n_grupo)
T_alpha_T = q_T * np.sqrt(cm_E / n_grupo)

print(f"\n{'='*70}")
print(f"TUKEY MANUAL CORRECTO - {NOMBRE_COL}")
print(f"  CM_E={cm_E:.4f}  gl_E={gl_E}  n={n_grupo}")
print(f"  q(0.05,{k_C},{gl_E}) = {q_C:.4f}   T_alpha = {T_alpha_C:.4f}")
print("="*70)
medias_C = df.groupby(NOMBRE_COL, observed=True)['Y'].mean().sort_values(ascending=False)
niveles_C = medias_C.index.tolist()
for i in range(len(niveles_C)):
    for j in range(i+1, len(niveles_C)):
        ni, nj = niveles_C[i], niveles_C[j]
        dif = abs(medias_C[ni] - medias_C[nj])
        sig = "SIGNIFICATIVO *" if dif > T_alpha_C else "no significativo"
        print(f"  {ni} vs {nj}: |{medias_C[ni]:.4f} - {medias_C[nj]:.4f}| = {dif:.4f}  {'>' if dif>T_alpha_C else '<'} T_alpha={T_alpha_C:.4f}  -> {sig}")

print(f"\n{'='*70}")
print(f"TUKEY MANUAL CORRECTO - {NOMBRE_TRAT}")
print(f"  CM_E={cm_E:.4f}  gl_E={gl_E}  n={n_grupo}")
print(f"  q(0.05,{k_T},{gl_E}) = {q_T:.4f}   T_alpha = {T_alpha_T:.4f}")
print("="*70)
medias_T = df.groupby(NOMBRE_TRAT, observed=True)['Y'].mean().sort_values(ascending=False)
niveles_T = medias_T.index.tolist()
for i in range(len(niveles_T)):
    for j in range(i+1, len(niveles_T)):
        ni, nj = niveles_T[i], niveles_T[j]
        dif = abs(medias_T[ni] - medias_T[nj])
        sig = "SIGNIFICATIVO *" if dif > T_alpha_T else "no significativo"
        print(f"  {ni} vs {nj}: |{medias_T[ni]:.4f} - {medias_T[nj]:.4f}| = {dif:.4f}  {'>' if dif>T_alpha_T else '<'} T_alpha={T_alpha_T:.4f}  -> {sig}")

# ============================================================
# Helper: grafica de intervalos Tukey (manual, correcto)
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
# FIGURA 1: Graficas (3 barras + 2 Tukey)
# ============================================================
mg = df['Y'].mean()
fig = plt.figure(figsize=(18, 13))
fig.suptitle(TITULO + f"\n(Y' estimado = {Y_prima:.4f}  |  Variable respuesta: {RESPUESTA})",
             fontsize=13, fontweight='bold')
gs = gridspec.GridSpec(2, 3, figure=fig, hspace=0.50, wspace=0.38,
                       top=0.83, bottom=0.07, left=0.07, right=0.97)

# Medias por Orden_Montaje
ax1 = fig.add_subplot(gs[0, 0])
med_F = df.groupby(NOMBRE_FIL, observed=True)['Y'].mean()
ax1.bar(med_F.index, med_F.values, color='#7fb3d3', edgecolor='black')
ax1.axhline(mg, color='red', linestyle='--', linewidth=1.5, label='Media global')
ax1.set_title(f'Medias por\n{NOMBRE_FIL}', fontweight='bold', fontsize=10)
ax1.set_xlabel(NOMBRE_FIL, fontsize=9); ax1.set_ylabel(RESPUESTA)
ax1.tick_params(axis='x', labelsize=8)
ax1.legend(fontsize=8); ax1.grid(axis='y', alpha=0.3)

# Medias por Operador
ax2 = fig.add_subplot(gs[0, 1])
med_C = df.groupby(NOMBRE_COL, observed=True)['Y'].mean()
ax2.bar(med_C.index, med_C.values, color='#f0a070', edgecolor='black')
ax2.axhline(mg, color='red', linestyle='--', linewidth=1.5, label='Media global')
ax2.set_title(f'Medias por\n{NOMBRE_COL}', fontweight='bold', fontsize=10)
ax2.set_xlabel(NOMBRE_COL, fontsize=9); ax2.set_ylabel(RESPUESTA)
ax2.legend(fontsize=8); ax2.grid(axis='y', alpha=0.3)

# Medias por Metodo
ax3 = fig.add_subplot(gs[0, 2])
med_T = df.groupby(NOMBRE_TRAT, observed=True)['Y'].mean()
ax3.bar(med_T.index, med_T.values, color='#82c982', edgecolor='black')
ax3.axhline(mg, color='red', linestyle='--', linewidth=1.5, label='Media global')
ax3.set_title(f"Medias por\n{NOMBRE_TRAT}  (con Y'={Y_prima:.0f})", fontweight='bold', fontsize=10)
ax3.set_xlabel(NOMBRE_TRAT, fontsize=9); ax3.set_ylabel(RESPUESTA)
ax3.legend(fontsize=8); ax3.grid(axis='y', alpha=0.3)

# Tukey Operador
ax4 = fig.add_subplot(gs[1, 0:2])
_tukey_plot(ax4, medias_C, T_alpha_C, f'Prueba de Tukey - {NOMBRE_COL} (IC 95% manual correcto)')

# Tukey Metodo
ax5 = fig.add_subplot(gs[1, 2])
_tukey_plot(ax5, medias_T, T_alpha_T, f'Prueba de Tukey - {NOMBRE_TRAT} (IC 95% manual correcto)')

BASE  = os.path.dirname(os.path.abspath(__file__))
SELLO_PY = "Generado en Python  |  matplotlib  |  statsmodels (ANOVA) + scipy (Tukey)"
fig.text(0.5, 0.012, SELLO_PY, ha='center', va='bottom', fontsize=13,
         style='italic', fontweight='bold', color='#1a5276',
         bbox=dict(boxstyle='round,pad=0.4', facecolor='#eaf2f8', edgecolor='#1a5276', linewidth=1.2))
ruta1 = os.path.join(BASE, 'python_1.png')
plt.savefig(ruta1, dpi=150, bbox_inches='tight'); plt.close()
print(f"\nGrafica guardada: {ruta1}")

# ============================================================
# FIGURA 2: Tabla ANOVA ajustada (imagen separada)
# ============================================================
dec_F = 'No significativo'    if Fc_F <= ft_F else 'Significativo ***'
dec_C = 'Significativo ***'   if Fc_C >  ft_C else 'No significativo'
dec_T = 'Significativo ***'   if Fc_T >  ft_T else 'No significativo'

encab = ['Fuente de Variacion', 'GL', 'SC', 'CM', 'Fc', 'Ft (a=5%)', 'Conclusion']
filas_tbl = [
    [NOMBRE_FIL,              str(gl_F), f'{sc_F:.4f}', f'{sc_F/gl_F:.4f}', f'{Fc_F:.4f}', f'{ft_F:.4f}', dec_F],
    [NOMBRE_COL,              str(gl_C), f'{sc_C:.4f}', f'{sc_C/gl_C:.4f}', f'{Fc_C:.4f}', f'{ft_C:.4f}', dec_C],
    [NOMBRE_TRAT,             str(gl_T), f'{sc_T:.4f}', f'{sc_T/gl_T:.4f}', f'{Fc_T:.4f}', f'{ft_T:.4f}', dec_T],
    [f'Error* (gl={gl_E})',   str(gl_E), f'{sc_E:.4f}', f'{cm_E:.4f}',       '-',           '-',           '-'  ],
    ['Total',                 str(N_orig-2), f'{sc_Tot:.4f}', '-',           '-',           '-',           '-'  ],
]
todas = [encab] + filas_tbl
nota  = f"* gl Error = (p-1)(p-2)-1 = {gl_E}  |  Y' estimado = {Y_prima:.4f}  |  G (sin perdido) = {G:.0f}"

fig2, ax_t = plt.subplots(figsize=(15, 4.8))
ax_t.set_xlim(0,1); ax_t.set_ylim(0,1); ax_t.axis('off')
fig2.suptitle(f'Tabla ANOVA - Cuadrado Latino con Dato Perdido\n{TITULO}',
              fontsize=13, fontweight='bold', y=0.99)

col_x = [0.00, 0.24, 0.32, 0.44, 0.54, 0.64, 0.76, 1.00]
n_fil = len(todas); row_h = 0.72/n_fil; y_start = 0.87

for i, fila in enumerate(todas):
    y_top = y_start - i*row_h; y_bot = y_top - row_h; y_mid = (y_top+y_bot)/2
    if   i == 0:       bg, fg, fw = '#2c3e50','white','bold'
    elif i == 1:       bg, fg, fw = '#eef6fb','black','normal'   # Filas (no sig)
    elif i in (2,3):   bg, fg, fw = '#d5f5e3','black','normal'   # Operador, Metodo (sig)
    elif i == 4:       bg, fg, fw = '#fdf2da','black','normal'   # Error
    else:              bg, fg, fw = '#eaecee','black','normal'   # Total
    for j, texto in enumerate(fila):
        x0, x1 = col_x[j], col_x[j+1]
        rect = plt.Rectangle((x0,y_bot), x1-x0, row_h, facecolor=bg,
                              edgecolor='#555555', linewidth=0.8,
                              transform=ax_t.transAxes, clip_on=True)
        ax_t.add_patch(rect)
        ax_t.text((x0+x1)/2, y_mid, texto, ha='center', va='center', fontsize=9.5,
                  color=fg, fontweight=fw, transform=ax_t.transAxes, clip_on=True)

ax_t.text(0.01, 0.05, nota, ha='left', va='bottom', fontsize=9,
          color='#c0392b', style='italic', transform=ax_t.transAxes)

fig2.text(0.5, 0.01, SELLO_PY, ha='center', va='bottom', fontsize=12,
          style='italic', fontweight='bold', color='#1a5276',
          bbox=dict(boxstyle='round,pad=0.4', facecolor='#eaf2f8', edgecolor='#1a5276', linewidth=1.2))
ruta2 = os.path.join(BASE, 'python_2.png')
plt.savefig(ruta2, dpi=150, bbox_inches='tight'); plt.close()
print(f"Tabla ANOVA guardada: {ruta2}")
