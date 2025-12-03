# 🎌 Navi-CLI: Tu Anime en Terminal
![Python](https://img.shields.io/badge/python-3.8+-b.svg)
![Terminal](https://img.shields.io/badge/Interface-Terminal-purple)
---
**Navi-CLI** es una herramienta de línea de comandos escrita en Python que te permite buscar, explorar y reproducir anime directamente desde la terminal, sin anuncios, sin abrir el navegador y con una interfaz clara gracias a **Rich**.

Utiliza **JKanime** como fuente de contenido, **Cloudscraper** para saltar protecciones de Cloudflare y **MPV** como reproductor.



## 🎥 Demo

https://github.com/user-attachments/assets/e4d83102-7b9e-4e2b-a20e-8dc338f3fd99


---
## ✨ Características

* 🔍 **Búsqueda Dinámica:** Encuentra animes por nombre rápidamente y muestra si es Serie, Película, OVA o Especial
* 📄 **Navegación Inteligente:** Cambia entre páginas, salta a capítulos específicos o selecciona directamente.
* 🎨 **Interfaz Moderna:** Tablas y paneles coloridos gracias a la librería `Rich`
* 🛡️ **Anti-Bloqueo:** Utiliza `cloudscraper` para evadir la protección de Cloudflare
* 🎥 **Reproducción Nativa:** Extrae el enlace `.m3u8` y reproduce el video usando **MPV**.
* ♻️ **Modo Continuo:** Después de ver un episodio, elige ver otro sin salir

---

## 🛠️ Requisitos Previos

1. **Python 3.8+** instalado
2. **Reproductor MPV** (motor de reproducción):
   * *Linux:* `sudo apt install mpv` (Debian/Ubuntu) o `sudo pacman -S mpv` (Arch)
   * *macOS:* `brew install mpv`
   * *Windows:* Descargar desde [mpv.io](https://mpv.io/)

---
## 🚀 Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/Agustin027/NaviCLI
cd naviCLI
```


### 2. Crear entorno virtual

#### Linux / macOS
```
python3 -m venv venv
source venv/bin/activate
```

#### Windows
```
python -m venv venv
venv\Scripts\activate
```

### 3. Instalar dependencias

```
pip install -r requirements.txt
```

---

## 💻 Uso

> **⚠️ IMPORTANTE:** Siempre activa el entorno virtual antes de ejecutar

### Paso 1: Activar entorno virtual

#### Linux / macOS
```bash
cd naviCLI
source venv/bin/activate
```

#### Windows
```bash
cd naviCLI
venv\Scripts\activate
```

Verás `(venv)` al inicio de tu terminal cuando esté activado ✅

### Paso 2: Ejecutar Navi

**Opción 1 - Como ejecutable (recomendado):**
```bash
chmod +x navi.py  # Solo la primera vez
./navi.py
```

**Opción 2 - Con Python:**
```bash
python3 navi.py
```

### Flujo de trabajo

1. **Buscar:** Escribe el nombre del anime
2. **Seleccionar:** Elige de la lista usando el número
3. **Navegar:** 
   - Escribe el número del capítulo para reproducir
   - **S** / **A** para siguiente/anterior página
   - **P** para ir a página específica
   - **C** para saltar a un capítulo directo
   - **Q** para salir
4. **¡Disfruta!** MPV se abrirá automáticamente

### Salir del entorno virtual

Cuando termines de usar Navi:
```bash
deactivate
```

---

