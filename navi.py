#!/usr/bin/env python3
import cloudscraper 
import re
import os
import sys
import shutil
import subprocess
from bs4 import BeautifulSoup
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()

def buscar_animes(query):

    url = f"https://jkanime.net/buscar/{query}/"
    scraper = cloudscraper.create_scraper() 
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task(f"[cyan]Buscando: {query}...", total=None)
        
        try:
            respuesta = scraper.get(url, timeout=15)
            respuesta.raise_for_status()
            progress.update(task, completed=True)
        except Exception as e:
            progress.stop()
            console.print(f"[red]❌ Error de conexión: {e}[/red]")
            return None, None
    
    sopa = BeautifulSoup(respuesta.text, 'html.parser')
    animes = sopa.find_all("div", class_="anime__item")
    
    if not animes:
        console.print("[yellow]⚠️ No se encontraron resultados[/yellow]")
        return None, None
    
    console.print(f"[green]✓[/green] {len(animes)} resultado(s) encontrado(s)")
    return animes, scraper

def extraer_tipo_anime(anime):

    ul = anime.find("ul")
    if not ul:
        return "Serie"
    
    items = ul.find_all("li")
    for item in items:
        texto = item.text.strip().lower()
        
        if "película" in texto or "pelicula" in texto or "movie" in texto:
            return "Película"
        elif "ova" in texto:
            return "OVA"
        elif "ona" in texto:
            return "ONA"
        elif "especial" in texto:
            return "Especial"
    
    return "Serie"

def mostrar_tabla_animes(animes, query):

    table = Table(
        title=f"[bold]Resultados para:[/bold] [green]{query}[/green]",
        border_style="cyan"
    )
    table.add_column("N°", style="cyan", justify="right", width=4)
    table.add_column("Título", style="magenta", no_wrap=False)
    table.add_column("Tipo", style="yellow", justify="center", width=10)
    
    for i, anime in enumerate(animes, 1):
        titulo_elem = anime.find("div", class_="anime__item__text")
        if titulo_elem and titulo_elem.find("h5"):
            titulo = titulo_elem.find("h5").text.strip()
            tipo = extraer_tipo_anime(anime)
            table.add_row(str(i), titulo, tipo)
    
    console.print(table)

def solicitar_seleccion(max_opciones, mensaje="👉 Elige número"):

    while True:
        try:
            entrada = Prompt.ask(mensaje)
            idx = int(entrada) - 1
            
            if 0 <= idx < max_opciones:
                return idx
            
            console.print(f"[yellow]⚠️ Debe estar entre 1 y {max_opciones}[/yellow]")
        except ValueError:
            console.print("[yellow]⚠️ Por favor ingresa un número válido[/yellow]")
        except KeyboardInterrupt:
            console.print("\n[red]Operación cancelada[/red]")
            sys.exit(0)

def inicializar_anime(link_anime, scraper):

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("[cyan]Obteniendo información del anime...", total=None)
        
        try:
            resp = scraper.get(link_anime, timeout=15)
            resp.raise_for_status()
            
            sopa = BeautifulSoup(resp.text, 'html.parser')
            
            # Buscar el ID del anime
            div_id = sopa.find("div", id="guardar-anime")
            if not div_id or "data-anime" not in div_id.attrs:
                progress.stop()
                console.print("[red]❌ No se pudo extraer el ID del anime[/red]")
                return None, None
            
            anime_id = div_id["data-anime"]
            
            # Buscar el token CSRF
            token_meta = sopa.find("meta", attrs={"name": "csrf-token"})
            if not token_meta or "content" not in token_meta.attrs:
                progress.stop()
                console.print("[red]❌ No se pudo extraer el token CSRF[/red]")
                return None, None
            
            token = token_meta["content"]
            progress.update(task, completed=True)
            
            return anime_id, token
            
        except Exception as e:
            progress.stop()
            console.print(f"[red]❌ Error al inicializar anime: {e}[/red]")
            return None, None

def cargar_pagina_episodios(anime_id, token, pagina, scraper):

    url = f"https://jkanime.net/ajax/episodes/{anime_id}/{pagina}/"
    
    try:
        respuesta = scraper.post(
            url, 
            data={"_token": token},
            timeout=15
        )
        respuesta.raise_for_status()
        datos = respuesta.json()
        
        if 'data' not in datos:
            console.print("[red]❌ Respuesta de API inválida[/red]")
            return None
        
        return datos
        
    except Exception as e:
        console.print(f"[red]❌ Error al cargar episodios: {e}[/red]")
        return None

def navegar_episodios(anime_id, token, scraper):

    pagina_actual = 1
    
    while True:
        datos = cargar_pagina_episodios(anime_id, token, pagina_actual, scraper)
        
        if not datos or not datos.get('data'):
            console.print("[red]❌ No se pudieron cargar los episodios[/red]")
            return None
        
        episodios = datos['data']
        ultima_pagina = datos.get('last_page', 1)
        per_page = datos.get('per_page', 12)  # Default a 12 si no viene
        
        table = Table(
            title=f"[bold cyan]📺 Episodios[/bold cyan] [dim](Página {pagina_actual}/{ultima_pagina})[/dim]",
            border_style="blue",
            show_lines=True
        )
        table.add_column("Capítulo", justify="right", style="green bold", width=8)
        table.add_column("Título", style="white")
        
        mapa_episodios = {}
        for ep in episodios:
            num = str(ep['number'])
            tit = ep.get('title', 'Sin título')
            table.add_row(num, tit)
            mapa_episodios[num] = ep
        
        console.print("\n")
        console.print(table)
        
        opciones_texto = []
        opciones_validas = []
        
        if pagina_actual > 1:
            opciones_texto.append("[cyan]A[/cyan]nterior")
            opciones_validas.append('a')
        
        if pagina_actual < ultima_pagina:
            opciones_texto.append("[cyan]S[/cyan]iguiente")
            opciones_validas.append('s')
        
        opciones_texto.extend([
            "[cyan]P[/cyan]ágina específica",
            "[cyan]C[/cyan]apítulo directo",
            "[red]Q[/red]uit"
        ])
        opciones_validas.extend(['p', 'c', 'q'])
        
        menu = Panel(
            f"[bold]Escribe el número de capítulo para reproducir[/bold]\n\n"
            f"Opciones: {' | '.join(opciones_texto)}",
            border_style="cyan"
        )
        console.print(menu)
        
        opcion = Prompt.ask("👉 Acción").strip().lower()
        
        if opcion == 'q':
            console.print("[yellow]👋 Saliendo...[/yellow]")
            return None
        
        elif opcion == 's' and 's' in opciones_validas:
            pagina_actual += 1
            console.print(f"[cyan]➡️  Página {pagina_actual}[/cyan]")
        
        elif opcion == 'a' and 'a' in opciones_validas:
            pagina_actual -= 1
            console.print(f"[cyan]⬅️  Página {pagina_actual}[/cyan]")
        
        elif opcion == 'p':
            try:
                nueva_pag = int(Prompt.ask(f"Ir a página [1-{ultima_pagina}]"))
                if 1 <= nueva_pag <= ultima_pagina:
                    pagina_actual = nueva_pag
                    console.print(f"[green]✓[/green] Saltando a página {nueva_pag}")
                else:
                    console.print(f"[yellow]⚠️ Página inválida (debe ser 1-{ultima_pagina})[/yellow]")
            except ValueError:
                console.print("[yellow]⚠️ Debes ingresar un número[/yellow]")
        
        elif opcion == 'c':
            try:
                cap_deseado = int(Prompt.ask("Número de capítulo"))
                pag_calculada = ((cap_deseado - 1) // per_page) + 1
                
                if 1 <= pag_calculada <= ultima_pagina:
                    pagina_actual = pag_calculada
                    console.print(f"[green]🚀 Saltando a página {pag_calculada}[/green]")
                else:
                    console.print("[yellow]⚠️ Ese capítulo parece estar fuera de rango[/yellow]")
            except ValueError:
                console.print("[yellow]⚠️ Debes ingresar un número[/yellow]")
        
        elif opcion in mapa_episodios:
            return mapa_episodios[opcion]
        
        else:
            console.print("[yellow]⚠️ Opción no válida o capítulo no disponible en esta página[/yellow]")

def extraer_m3u8(link_episodio, scraper):
    """Extrae la URL del archivo m3u8 del episodio."""
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("[cyan]Buscando video...", total=None)
        
        try:
            resp = scraper.get(link_episodio, timeout=15)
            resp.raise_for_status()
            
            patron_embed = r'https://jkanime\.net/jkplayer/[^"]+'
            match = re.search(patron_embed, resp.text)
            
            if not match:
                progress.stop()
                console.print("[red]❌ No se encontró el reproductor[/red]")
                return None
            
            url_embed = match.group(0).replace('\\', '')
            progress.update(task, description="[cyan]Accediendo al reproductor...")
            
            resp_vid = scraper.get(url_embed, timeout=15)
            resp_vid.raise_for_status()
            
            patron_m3u8 = r"https://[^']+\.m3u8[^']*"
            match_m3u8 = re.search(patron_m3u8, resp_vid.text)
            
            if not match_m3u8:
                progress.stop()
                console.print("[red]❌ No se encontró el archivo de video (.m3u8)[/red]")
                return None
            
            progress.update(task, completed=True)
            return match_m3u8.group(0)
            
        except Exception as e:
            progress.stop()
            console.print(f"[red]❌ Error al extraer video: {e}[/red]")
            return None

def reproducir_video(url):
    """Reproduce el video usando mpv."""
    if not shutil.which("mpv"):
        console.print("[red]❌ MPV no está instalado en el sistema[/red]")
        console.print("[yellow]💡 Instala mpv con: sudo apt install mpv (Linux) o brew install mpv (Mac)[/yellow]")
        return False
    
    panel = Panel(
        f"[bold green]{url}[/bold green]",
        title="🎬 Video encontrado",
        border_style="green"
    )
    console.print(panel)
    console.print("\n[cyan]▶️  Abriendo en MPV...[/cyan]\n")
    
    try:
        subprocess.run(
            ["mpv", "--msg-level=ffmpeg=no", url], # Mantenemos el flag para silenciar errores de red
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL 
        )
        return True
    except Exception as e:
        console.print(f"[red]❌ Error al reproducir: {e}[/red]")
        return False

def main():
    """Función principal del programa."""
    console.print(Panel.fit(
        "[bold magenta]🎌NaviCLI🎌[/bold magenta]\n",
        border_style="magenta"
    ))
    
    while True:
        try:
            query = Prompt.ask("\n[bold]🔎 Buscar anime[/bold] (o Enter para salir)").strip()
            
            if not query:
                console.print("[yellow]👋 ¡Hasta luego![/yellow]")
                break
            
            animes, scraper = buscar_animes(query)
            if not animes:
                continue
            
            mostrar_tabla_animes(animes, query)
            idx_anime = solicitar_seleccion(len(animes))
            anime = animes[idx_anime]
            
            link_anime = anime.find("a")["href"]
            titulo_elem = anime.find("h5")
            titulo = titulo_elem.text.strip() if titulo_elem else "Anime seleccionado"
            
            console.print(f"\n[green]✅ Seleccionado:[/green] [bold]{titulo}[/bold]")
            
            anime_id, token = inicializar_anime(link_anime, scraper)
            if not anime_id:
                continue
            
            while True:
                capitulo = navegar_episodios(anime_id, token, scraper)
                
                if not capitulo:
                    break  
                
                link_episodio = f"{link_anime}{capitulo['number']}/"
                
                url_final = extraer_m3u8(link_episodio, scraper)
                
                if url_final:
                    reproducir_video(url_final)
                else:
                    console.print("[red]❌ No se pudo obtener el video[/red]")
                
                continuar = Prompt.ask(
                    "\n¿Ver otro episodio del mismo anime?",
                    choices=["s", "n"],
                    default="s"
                )
                
                if continuar.lower() != 's':
                    break
            
        except KeyboardInterrupt:
            console.print("\n[yellow]👋 Programa interrumpido[/yellow]")
            break
        except Exception as e:
            console.print(f"\n[red]❌ Error inesperado: {e}[/red]")
            continue
    
    sys.exit(0)

if __name__ == "__main__":
    main()