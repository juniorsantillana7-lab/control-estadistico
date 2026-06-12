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
# PROBLEMA #1 - DISENO FACTORIAL COMPLETAMENTE ALEATORIZADO
# Factor A: Maquina (6 niveles: M1-M6)
# Factor B: Hombre  (4 niveles: I, II, III, IV)
# Replicas: n = 3  |  N = 72
# Variable respuesta: Nro de sacos defectuosos por dia
# ============================================================

# -- Datos ---------------------------------------------------
maquinas = ['M1']*12 + ['M2']*12 + ['M3']*12 + ['M4']*12 + ['M5']*12 + ['M6']*12
hombres  = ['I','I','I','II','II','II','III','III','III','IV','IV','IV'] * 6
sacos_vals = [
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
     5, 6, 3,   4, 3, 5,    8, 3, 6,   2, 4, 1,
]

df = pd.DataFrame({'Maquina': maquinas, 'Hombre': hombres, 'Sacos': sacos_vals})
df['Maquina'] = pd.Categorical(df['Maquina'], categories=['M1','M2','M3','M4','M5','M6'])
df['Hombre']  = pd.Categorical(df['Hombre'],  categories=['I','II','III','IV'])

# ============================================================
# ANOVA FACTORIAL (Tipo II)
# ============================================================
modelo = ols('Sacos ~ C(Maquina) + C(Hombre) + C(Maquina):C(Hombre)', data=df).fit()
tabla_anova = anova_lm(modelo, typ=2)

print("=" * 65)
print("TABLA ANOVA - DISENO FACTORIAL")
print("=" * 65)
print(tabla_anova.round(4))

# F criticos
alpha  = 0.05
ft_A   = f_dist.ppf(1 - alpha,  5, 48)
ft_B   = f_dist.ppf(1 - alpha,  3, 48)
ft_AB  = f_dist.ppf(1 - alpha, 15, 48)

print(f"\nF critico Factor A  (5, 48)  = {ft_A:.4f}")
print(f"F critico Factor B  (3, 48)  = {ft_B:.4f}")
print(f"F critico Inter AxB (15, 48) = {ft_AB:.4f}")

print("\nCONCLUSIONES:")
Fc_A  = tabla_anova.loc['C(Maquina)',            'F']
Fc_B  = tabla_anova.loc['C(Hombre)',             'F']
Fc_AB = tabla_anova.loc['C(Maquina):C(Hombre)', 'F']

print(f"  Factor A (Maquina): Fc={Fc_A:.4f}  {'> SI influye' if Fc_A > ft_A else '< NO influye'} significativamente")
print(f"  Factor B (Hombre):  Fc={Fc_B:.4f}  {'> SI influye' if Fc_B > ft_B else '< NO influye'} significativamente")
print(f"  Interaccion AxB:    Fc={Fc_AB:.4f} {'> SI influye' if Fc_AB > ft_AB else '< NO influye'} significativamente")

# ============================================================
# TUKEY MANUAL (correcto para diseno factorial)
# Factor A: T_alpha = q(alpha, a, gl_E) * sqrt(CM_E / (b*n))
# Factor B: T_alpha = q(alpha, b, gl_E) * sqrt(CM_E / (a*n))
# NOTA: pairwise_tukeyhsd ignora B y AxB -> MSE inflado -> INCORRECTO
# ============================================================
sc_E_v  = tabla_anova.loc['Residual', 'sum_sq']
gl_E_v  = 48; cm_E_v = sc_E_v / gl_E_v
a_lev = 6; b_lev = 4; n_rep = 3
n_A   = b_lev * n_rep    # 12 obs por nivel de Factor A
n_B   = a_lev * n_rep    # 18 obs por nivel de Factor B

q_A       = studentized_range.ppf(0.95, a_lev, gl_E_v)
q_B       = studentized_range.ppf(0.95, b_lev, gl_E_v)
T_alpha_A = q_A * np.sqrt(cm_E_v / n_A)
T_alpha_B = q_B * np.sqrt(cm_E_v / n_B)

medias_A = df.groupby('Maquina', observed=True)['Sacos'].mean()
medias_B = df.groupby('Hombre',  observed=True)['Sacos'].mean()

print("\n" + "=" * 65)
print("TUKEY MANUAL - FACTOR A: Maquina")
print(f"  CM_E={cm_E_v:.4f}  gl_E={gl_E_v}  n_A={n_A}")
print(f"  q(0.05,{a_lev},{gl_E_v})={q_A:.4f}   T_alpha={T_alpha_A:.4f}")
print("=" * 65)
nivs_A = medias_A.sort_values(ascending=False).index.tolist()
for i in range(len(nivs_A)):
    for j in range(i+1, len(nivs_A)):
        ni, nj = nivs_A[i], nivs_A[j]
        dif = abs(medias_A[ni] - medias_A[nj])
        sig = "SIGNIFICATIVO *" if dif > T_alpha_A else "no significativo"
        print(f"  {ni} vs {nj}: |{medias_A[ni]:.4f}-{medias_A[nj]:.4f}| = {dif:.4f} {'>' if dif>T_alpha_A else '<'} {T_alpha_A:.4f} -> {sig}")

print("\n" + "=" * 65)
print("TUKEY MANUAL - FACTOR B: Hombre")
print(f"  CM_E={cm_E_v:.4f}  gl_E={gl_E_v}  n_B={n_B}")
print(f"  q(0.05,{b_lev},{gl_E_v})={q_B:.4f}   T_alpha={T_alpha_B:.4f}")
print("=" * 65)
nivs_B = medias_B.sort_values(ascending=False).index.tolist()
for i in range(len(nivs_B)):
    for j in range(i+1, len(nivs_B)):
        ni, nj = nivs_B[i], nivs_B[j]
        dif = abs(medias_B[ni] - medias_B[nj])
        sig = "SIGNIFICATIVO *" if dif > T_alpha_B else "no significativo"
        print(f"  {ni} vs {nj}: |{medias_B[ni]:.4f}-{medias_B[nj]:.4f}| = {dif:.4f} {'>' if dif>T_alpha_B else '<'} {T_alpha_B:.4f} -> {sig}")

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
# GRAFICAS
# ============================================================
ORDEN_MAQ = ['M1','M2','M3','M4','M5','M6']
ORDEN_HOM = ['I','II','III','IV']
COLORES   = ['#1f77b4','#ff7f0e','#2ca02c','#d62728']

# ============================================================
# FIGURA 1: Efectos principales, interaccion y Tukey
# ============================================================
fig = plt.figure(figsize=(18, 13))
fig.suptitle('PROBLEMA #1 - Diseno Factorial: Maquina x Hombre\n(Sacos de harina defectuosos)',
             fontsize=14, fontweight='bold')
gs = gridspec.GridSpec(2, 3, figure=fig,
                       hspace=0.45, wspace=0.35,
                       top=0.83, bottom=0.07, left=0.07, right=0.97)

# -- 1. Efecto principal A -----------------------------------
ax1 = fig.add_subplot(gs[0, 0])
medias_A = df.groupby('Maquina', observed=True)['Sacos'].mean()[ORDEN_MAQ]
ax1.bar(ORDEN_MAQ, medias_A.values, color='steelblue', edgecolor='black')
ax1.axhline(df['Sacos'].mean(), color='red', linestyle='--', linewidth=1.5, label='Media global')
ax1.set_title('Efecto Principal\nFactor A: Maquina', fontweight='bold')
ax1.set_xlabel('Maquina'); ax1.set_ylabel('Media sacos defectuosos')
ax1.legend(fontsize=8); ax1.grid(axis='y', alpha=0.3)

# -- 2. Efecto principal B -----------------------------------
ax2 = fig.add_subplot(gs[0, 1])
medias_B = df.groupby('Hombre', observed=True)['Sacos'].mean()[ORDEN_HOM]
ax2.bar(ORDEN_HOM, medias_B.values, color='coral', edgecolor='black')
ax2.axhline(df['Sacos'].mean(), color='red', linestyle='--', linewidth=1.5, label='Media global')
ax2.set_title('Efecto Principal\nFactor B: Hombre', fontweight='bold')
ax2.set_xlabel('Operario'); ax2.set_ylabel('Media sacos defectuosos')
ax2.legend(fontsize=8); ax2.grid(axis='y', alpha=0.3)

# -- 3. Interaccion AxB --------------------------------------
ax3 = fig.add_subplot(gs[0, 2])
for i, hombre in enumerate(ORDEN_HOM):
    medias = df[df['Hombre'] == hombre].groupby('Maquina', observed=True)['Sacos'].mean()[ORDEN_MAQ]
    ax3.plot(ORDEN_MAQ, medias.values, marker='o', linewidth=2,
             color=COLORES[i], label=f'Hombre {hombre}')
ax3.set_title('Grafica de Interaccion\nAxB: Maquina x Hombre', fontweight='bold')
ax3.set_xlabel('Maquina'); ax3.set_ylabel('Media sacos defectuosos')
ax3.legend(fontsize=8); ax3.grid(alpha=0.3)

# -- 4. Tukey A ----------------------------------------------
ax4 = fig.add_subplot(gs[1, 0:2])
_tukey_plot(ax4, medias_A, T_alpha_A, 'Prueba de Tukey - Factor A: Maquina (IC 95% manual correcto)')

# -- 5. Tukey B ----------------------------------------------
ax5 = fig.add_subplot(gs[1, 2])
_tukey_plot(ax5, medias_B, T_alpha_B, 'Prueba de Tukey - Factor B: Hombre (IC 95% manual correcto)')

BASE = os.path.dirname(os.path.abspath(__file__))
ruta = os.path.join(BASE, 'P1_resultados.png')
plt.savefig(ruta, dpi=150, bbox_inches='tight')
plt.close()
print(f"Grafica guardada en: {ruta}")

# ============================================================
# FIGURA 2: Tabla ANOVA (imagen separada)
# ============================================================
sc_A  = tabla_anova.loc['C(Maquina)',            'sum_sq']
sc_B  = tabla_anova.loc['C(Hombre)',             'sum_sq']
sc_AB = tabla_anova.loc['C(Maquina):C(Hombre)', 'sum_sq']
sc_E  = tabla_anova.loc['Residual',              'sum_sq']
sc_T  = sc_A + sc_B + sc_AB + sc_E

encab_t = ['Fuente de Variacion', 'GL', 'SC', 'CM', 'Fc', 'Ft (a=5%)', 'Conclusion']
filas_t = [
    ['Factor A: Maquina',  '5',  f'{sc_A:.4f}',  f'{sc_A/5:.4f}',   f'{Fc_A:.4f}',  f'{ft_A:.4f}',  'Significativo ***'],
    ['Factor B: Hombre',   '3',  f'{sc_B:.4f}',  f'{sc_B/3:.4f}',   f'{Fc_B:.4f}',  f'{ft_B:.4f}',  'Significativo ***'],
    ['Interaccion AxB',    '15', f'{sc_AB:.4f}', f'{sc_AB/15:.4f}', f'{Fc_AB:.4f}', f'{ft_AB:.4f}', 'Significativo ***'],
    ['Error (Residual)',   '48', f'{sc_E:.4f}',  f'{sc_E/48:.4f}',  '-',            '-',            '-'],
    ['Total',              '71', f'{sc_T:.4f}',  '-',               '-',            '-',            '-'],
]
todas_filas = [encab_t] + filas_t

fig2, ax_t = plt.subplots(figsize=(14, 4))
ax_t.set_xlim(0, 1); ax_t.set_ylim(0, 1); ax_t.axis('off')
fig2.suptitle('Tabla ANOVA - Diseno Factorial Completamente Aleatorizado\nPROBLEMA #1: Maquina x Hombre',
              fontsize=13, fontweight='bold', y=0.98)

col_x   = [0.00, 0.28, 0.34, 0.46, 0.56, 0.66, 0.78, 1.00]
n_filas = len(todas_filas)
row_h   = 0.82 / n_filas
y_start = 0.88

for i, fila in enumerate(todas_filas):
    y_top = y_start - i * row_h
    y_bot = y_top - row_h
    y_mid = (y_top + y_bot) / 2
    if i == 0:
        bg, fg, fw = '#2c3e50', 'white', 'bold'
    elif i in (1, 2, 3):
        bg, fg, fw = '#d5f5e3', 'black', 'normal'
    elif i == 4:
        bg, fg, fw = '#fdfefe', 'black', 'normal'
    else:
        bg, fg, fw = '#eaecee', 'black', 'normal'

    for j, texto in enumerate(fila):
        x0, x1 = col_x[j], col_x[j + 1]
        rect = plt.Rectangle((x0, y_bot), x1 - x0, row_h,
                              facecolor=bg, edgecolor='#555555', linewidth=0.8,
                              transform=ax_t.transAxes, clip_on=True)
        ax_t.add_patch(rect)
        ax_t.text((x0 + x1) / 2, y_mid, texto,
                  ha='center', va='center', fontsize=11,
                  color=fg, fontweight=fw,
                  transform=ax_t.transAxes, clip_on=True)

ruta_t = os.path.join(BASE, 'P1_tabla_anova.png')
plt.savefig(ruta_t, dpi=150, bbox_inches='tight')
plt.close()
print(f"Tabla ANOVA guardada en: {ruta_t}")
