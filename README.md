# Examen PC3 · Control Estadístico de la Calidad

Sitio web estático para presentar la resolución del examen PC3 (UNI — FIIS):
tres diseños experimentales resueltos en **Excel, Minitab, Python y R**.

Diseño propio estilo «informe técnico editorial»: papel marfil, tipografía
serif Fraunces + Figtree + IBM Plex Mono, navegación lateral y pestañas por
herramienta. **Sin frameworks ni build**: HTML + CSS + JS puros.

## Cómo abrir el sitio

- **Doble clic** en `index.html` (todo funciona salvo el botón *Ver código*).
- **Servidor local** (recomendado, habilita el visor de código):

```powershell
cd "C:\Users\ASUS\Desktop\PAGINA 2"
python -m http.server 8080
# luego abrir http://localhost:8080
```

## Estructura

```
PAGINA 2/
├── index.html          ← portada (carátula del informe)
├── ejercicio1.html     ← diseño factorial 6×4
├── ejercicio2.html     ← cuadrado latino con dato perdido
├── ejercicio3.html     ← cuadrado latino 4×4 (proveedores)
├── recursos.html       ← repositorio de scripts y datos
└── assets/
    ├── css/estilos.css ← todo el diseño (variables en :root)
    ├── js/app.js       ← pestañas, lightbox, visor de código, menú móvil
    ├── img/
    │   ├── marca/uni.png
    │   └── ej1/ ej2/ ej3/   ← capturas de cada ejercicio
    └── docs/
        └── ej1/ ej2/ ej3/   ← analisis.py · analisis.R · datos.xlsx
```

## Esquema de nombres de capturas (`assets/img/ejN/`)

| Archivo            | Contenido                                   | ¿Obligatorio? |
|--------------------|---------------------------------------------|---------------|
| `enunciado.png`    | enunciado oficial del ejercicio             | sí            |
| `hipotesis.png`    | formulación de hipótesis                    | sí            |
| `conclusiones.png` | interpretaciones y conclusiones             | sí            |
| `excel-1.png` … `excel-4.png`     | capturas de Excel (hasta 4)  | no            |
| `minitab-1.png` … `minitab-4.png` | capturas de Minitab (hasta 4)| no            |
| `python-1.png` … `python-4.png`   | capturas de Python (hasta 4) | no            |
| `r-1.png` … `r-4.png`             | capturas de R (hasta 4)      | no            |

Las capturas que falten **se ocultan solas** (no aparecen marcos vacíos);
si una herramienta no tiene ninguna, la pestaña muestra el aviso
«Aún no hay capturas…». Para actualizar una imagen basta reemplazar el
archivo manteniendo el nombre.

## Funcionalidades

- Lightbox: clic en cualquier lámina la amplía (cerrar con Esc o clic fuera);
  incluye botón de descarga.
- Botón **Descargar** sobre cada lámina al pasar el mouse.
- Pestañas Excel / Minitab / Python / R navegables con flechas del teclado.
- Visor de código en `recursos.html` (requiere servidor local) con botones
  *Copiar* y *Descargar*.
- Diseño responsive (menú lateral se vuelve desplegable en pantallas chicas),
  respeta `prefers-reduced-motion` y tiene estilos de impresión.

## Notas

- Los scripts de `assets/docs/` son material de consulta y descarga;
  no se ejecutan desde esta carpeta.
- Para cambiar la paleta del sitio basta editar las variables de
  `:root` al inicio de `assets/css/estilos.css`.
