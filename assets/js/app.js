/* ============================================================
   app.js — Examen PC3 · Control Estadístico de la Calidad
   Interactividad del sitio (vanilla JS, sin dependencias):
   menú móvil · pestañas · figuras faltantes · lightbox ·
   visor de código · aparición al hacer scroll
   ============================================================ */

document.addEventListener('DOMContentLoaded', () => {
    iniciarMenuMovil();
    iniciarPestanas();
    iniciarFigurasFaltantes();
    iniciarLightbox();
    iniciarVisorCodigo();
    iniciarAparicion();
});

/* ---------- Menú lateral en pantallas chicas ---------- */
function iniciarMenuMovil() {
    const boton = document.querySelector('.btn-menu');
    const panel = document.querySelector('.panel-lateral');
    const velo = document.querySelector('.velo');
    if (!boton || !panel || !velo) return;

    const cerrar = () => {
        panel.classList.remove('abierto');
        velo.classList.remove('activo');
        boton.setAttribute('aria-expanded', 'false');
    };
    boton.addEventListener('click', () => {
        const abierto = panel.classList.toggle('abierto');
        velo.classList.toggle('activo', abierto);
        boton.setAttribute('aria-expanded', String(abierto));
    });
    velo.addEventListener('click', cerrar);
    document.addEventListener('keydown', e => { if (e.key === 'Escape') cerrar(); });
}

/* ---------- Pestañas de herramientas (Excel/Minitab/Python/R) ---------- */
function iniciarPestanas() {
    document.querySelectorAll('[data-pestanas]').forEach(grupo => {
        const botones = Array.from(grupo.querySelectorAll('.pestana'));
        const paneles = Array.from(
            document.querySelectorAll(`[data-grupo="${grupo.dataset.pestanas}"]`)
        );

        function activar(boton) {
            botones.forEach(b => {
                const activo = b === boton;
                b.setAttribute('aria-selected', String(activo));
                b.tabIndex = activo ? 0 : -1;
            });
            paneles.forEach(p => {
                p.classList.toggle('visible', p.id === boton.getAttribute('aria-controls'));
            });
        }

        botones.forEach((b, i) => {
            b.addEventListener('click', () => activar(b));
            // navegación con flechas dentro del tablist
            b.addEventListener('keydown', e => {
                let destino = null;
                if (e.key === 'ArrowRight') destino = botones[(i + 1) % botones.length];
                if (e.key === 'ArrowLeft') destino = botones[(i - 1 + botones.length) % botones.length];
                if (destino) { e.preventDefault(); destino.focus(); activar(destino); }
            });
        });
    });
}

/* ---------- Ocultar figuras cuyas capturas aún no existen ---------- */
function iniciarFigurasFaltantes() {
    document.querySelectorAll('.figura img').forEach(img => {
        const figura = img.closest('.figura');
        const ocultar = () => {
            figura.classList.add('oculta');
            figura.style.display = 'none';
            actualizarAvisoVacio(figura);
        };
        img.addEventListener('error', ocultar);
        if (img.complete && img.naturalWidth === 0) ocultar();
    });
}

function actualizarAvisoVacio(figura) {
    // si un panel de pestaña se queda sin ninguna captura, muestra el aviso
    const panel = figura.closest('.panel-tab');
    if (!panel) return;
    const visibles = panel.querySelectorAll('.figura:not(.oculta)').length;
    const aviso = panel.querySelector('.sin-capturas');
    if (aviso && visibles === 0) aviso.style.display = 'block';
}

/* ---------- Lightbox: ampliar cualquier figura con clic ---------- */
function iniciarLightbox() {
    const dialogo = document.createElement('dialog');
    dialogo.className = 'caja-lightbox';
    dialogo.setAttribute('aria-label', 'Imagen ampliada');
    dialogo.innerHTML = `
        <div class="cuerpo">
            <img src="" alt="Vista ampliada">
            <div class="pie">
                <span></span>
                <a class="boton primario" download>Descargar</a>
                <button class="boton" type="button" data-cerrar>Cerrar (Esc)</button>
            </div>
        </div>`;
    document.body.appendChild(dialogo);

    const imagen = dialogo.querySelector('img');
    const nombre = dialogo.querySelector('.pie span');
    const enlace = dialogo.querySelector('.pie a');

    document.querySelectorAll('.figura img').forEach(img => {
        img.addEventListener('click', () => {
            const src = img.getAttribute('src');
            imagen.src = src;
            imagen.alt = img.alt || 'Vista ampliada';
            nombre.textContent = src.split('/').pop();
            enlace.href = src;
            enlace.setAttribute('download', src.split('/').pop());
            dialogo.showModal();
        });
    });

    dialogo.querySelector('[data-cerrar]').addEventListener('click', () => dialogo.close());
    // clic fuera del contenido cierra el diálogo
    dialogo.addEventListener('click', e => {
        if (e.target === dialogo) dialogo.close();
    });
}

/* ---------- Visor de código (recursos.html) ---------- */
function iniciarVisorCodigo() {
    const botones = document.querySelectorAll('[data-codigo]');
    if (!botones.length) return;

    const dialogo = document.createElement('dialog');
    dialogo.className = 'caja-codigo';
    dialogo.setAttribute('aria-label', 'Código fuente');
    dialogo.innerHTML = `
        <div class="cuerpo">
            <div class="cabecera-codigo">
                <div class="semaforo"><i></i><i></i><i></i></div>
                <span></span>
                <button class="boton oscuro" type="button" data-copiar>Copiar</button>
                <a class="boton oscuro" download>Descargar</a>
                <button class="boton oscuro" type="button" data-cerrar>Cerrar</button>
            </div>
            <pre><code></code></pre>
        </div>`;
    document.body.appendChild(dialogo);

    const titulo = dialogo.querySelector('.cabecera-codigo span');
    const enlace = dialogo.querySelector('.cabecera-codigo a');
    const codigo = dialogo.querySelector('code');
    const btnCopiar = dialogo.querySelector('[data-copiar]');
    let textoActual = '';

    botones.forEach(btn => {
        btn.addEventListener('click', () => {
            const ruta = btn.dataset.codigo;
            const archivo = ruta.split('/').pop();
            titulo.textContent = ruta;
            enlace.href = ruta;
            enlace.setAttribute('download', archivo);
            codigo.innerHTML = '<span class="com"># Cargando…</span>';
            dialogo.showModal();

            fetch(ruta)
                .then(r => { if (!r.ok) throw new Error(r.status); return r.text(); })
                .then(texto => {
                    textoActual = texto;
                    codigo.innerHTML = resaltar(texto);
                })
                .catch(() => {
                    textoActual = '';
                    codigo.innerHTML =
                        '<span class="com"># No se pudo leer el archivo desde aquí.\n' +
                        '# Si abriste la página con doble clic (file://), el navegador\n' +
                        '# bloquea fetch(): usa el botón Descargar o sirve el sitio con\n' +
                        '#   python -m http.server 8080</span>';
                });
        });
    });

    btnCopiar.addEventListener('click', () => {
        if (!textoActual) return;
        navigator.clipboard.writeText(textoActual).then(() => {
            btnCopiar.textContent = '¡Copiado!';
            setTimeout(() => { btnCopiar.textContent = 'Copiar'; }, 1600);
        });
    });
    dialogo.querySelector('[data-cerrar]').addEventListener('click', () => dialogo.close());
    dialogo.addEventListener('click', e => { if (e.target === dialogo) dialogo.close(); });
}

/* resaltado mínimo: comentarios (#) y cadenas, suficiente para .py y .R */
function resaltar(texto) {
    const escapado = texto
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;');
    return escapado.split('\n').map(linea => {
        const idx = posicionComentario(linea);
        if (idx === -1) return marcarCadenas(linea);
        return marcarCadenas(linea.slice(0, idx)) +
            '<span class="com">' + linea.slice(idx) + '</span>';
    }).join('\n');
}

function posicionComentario(linea) {
    let enCadena = null;
    for (let i = 0; i < linea.length; i++) {
        const c = linea[i];
        if (enCadena) {
            if (c === enCadena && linea[i - 1] !== '\\') enCadena = null;
        } else if (c === '"' || c === "'") {
            enCadena = c;
        } else if (c === '#') {
            return i;
        }
    }
    return -1;
}

function marcarCadenas(fragmento) {
    return fragmento.replace(/("[^"]*"|'[^']*')/g, '<span class="str">$1</span>');
}

/* ---------- Aparición progresiva de secciones ---------- */
function iniciarAparicion() {
    const elementos = document.querySelectorAll('.aparece');
    if (!elementos.length) return;
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
        elementos.forEach(el => el.classList.add('en-vista'));
        return;
    }
    const observador = new IntersectionObserver(entradas => {
        entradas.forEach(en => {
            if (en.isIntersecting) {
                en.target.classList.add('en-vista');
                observador.unobserve(en.target);
            }
        });
    }, { threshold: 0.08 });
    elementos.forEach(el => observador.observe(el));
}
