from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.columns import Columns
from rich.text import Text
from rich import box
from datetime import datetime, timedelta
from pyfiglet import figlet_format
from rich import print
import json
import os
import plotext as plt

console = Console()
FILE = 'study_data.json'
DATE_FMT = "%Y-%m-%d"

def migrate_data(data):
    migrated = {}
    for day, materias in data.items():
        normalized = list(dict.fromkeys(m.strip().title() for m in materias))
        migrated[day] = normalized
    return migrated


def load_data():
    if not os.path.exists(FILE):
        return {}
    with open(FILE, "r") as f:
        data = json.load(f)
    data = migrate_data(data)
    save_data(data)
    return data


def save_data(data):
    with open(FILE, "w") as f:
        json.dump(data, f, indent=4)


def mark_today(data):
    materia = input("Materia estudiada: ").strip().title()
    if not materia:
        console.print("[red]No ingresaste ninguna materia.[/red]")
        return
    today = datetime.now().strftime(DATE_FMT)
    if today not in data:
        data[today] = []
    if materia not in data[today]:
        data[today].append(materia)
        save_data(data)
        console.print(f"[green] Agregaste '{materia}' al día {today}[/green]")
    else:
        console.print(f"[yellow]'{materia}' ya estaba registrada hoy.[/yellow]")


def show_calendar(data):
    table = Table(title="Study Tracker — Últimos 7 días", box=box.ROUNDED)
    table.add_column("Fecha", justify="center", style="bold red")
    table.add_column("Materias", justify="center", style="bold green")
    table.add_column("Estado", justify="center", style="bold yellow")

    for i in range(6, -1, -1):
        day = (datetime.now() - timedelta(days=i)).strftime(DATE_FMT)
        materias = data.get(day, [])
        estado = "[green] Estudiado[/green]" if materias else "[red] No estudiado[/red]"
        materias_str = ", ".join(materias) if materias else "-"
        table.add_row(day, materias_str, estado)

    console.print(table)


def calcular_racha(data):
    streak = 0
    i = 0
    while True:
        day = (datetime.now() - timedelta(days=i)).strftime(DATE_FMT)
        if data.get(day):
            streak += 1
            i += 1
        else:
            break
    return streak


def calcular_racha_maxima(data):
    """Racha más larga de todos los tiempos."""
    if not data:
        return 0
    fechas = sorted(
        datetime.strptime(d, DATE_FMT)
        for d, materias in data.items()
        if materias
    )
    if not fechas:
        return 0
    max_streak = current = 1
    for i in range(1, len(fechas)):
        if (fechas[i] - fechas[i - 1]).days == 1:
            current += 1
            max_streak = max(max_streak, current)
        elif (fechas[i] - fechas[i - 1]).days > 1:
            current = 1
    return max_streak


def materia_favorita(data):
    """Materia con más sesiones registradas."""
    conteo = {}
    for materias in data.values():
        for m in materias:
            conteo[m] = conteo.get(m, 0) + 1
    if not conteo:
        return None, 0
    top = max(conteo, key=conteo.get)
    return top, conteo[top]


def dias_estudiados_mes(data):
    """Días únicos estudiados en el mes actual."""
    hoy = datetime.now()
    return sum(
        1
        for d, materias in data.items()
        if materias
        and datetime.strptime(d, DATE_FMT).month == hoy.month
        and datetime.strptime(d, DATE_FMT).year == hoy.year
    )


def build_stats_panels(data):
    """Devuelve una lista de Panels con KPIs."""
    racha = calcular_racha(data)
    racha_max = calcular_racha_maxima(data)
    total_dias = sum(1 for materias in data.values() if materias)
    total_sesiones = sum(len(materias) for materias in data.values())
    fav, fav_count = materia_favorita(data)
    dias_mes = dias_estudiados_mes(data)

    def kpi(titulo, valor, color="cyan"):
        t = Text(justify="center")
        t.append(f"\n{valor}\n", style=f"bold {color}")
        t.append(titulo, style="dim")
        return Panel(t, expand=True, border_style=color)

    panels = [
        kpi("Racha actual", f"{racha} día{'s' if racha != 1 else ''}", "yellow"),
        kpi("Racha máxima", f"{racha_max} día{'s' if racha_max != 1 else ''}", "gold1"),
        kpi("Días totales", str(total_dias), "green"),
        kpi("Sesiones totales", str(total_sesiones), "blue"),
        kpi("Este mes", f"{dias_mes} día{'s' if dias_mes != 1 else ''}", "magenta"),
        kpi("Favorita", f"{fav} ({fav_count}x)" if fav else "—", "red"),
    ]
    return panels


def show_subject_breakdown(data):
    """Tabla de materias con conteo de sesiones."""
    conteo = {}
    for materias in data.values():
        for m in materias:
            conteo[m] = conteo.get(m, 0) + 1
    if not conteo:
        return

    table = Table(title="Sesiones por materia", box=box.SIMPLE_HEAVY)
    table.add_column("Materia", style="bold cyan")
    table.add_column("Sesiones", justify="right", style="bold green")
    table.add_column("Barra", style="dim")

    max_v = max(conteo.values())
    for materia, count in sorted(conteo.items(), key=lambda x: -x[1]):
        bar_len = int((count / max_v) * 20)
        bar = "█" * bar_len + "░" * (20 - bar_len)
        table.add_row(materia, str(count), f"[cyan]{bar}[/cyan]")

    console.print(table)



def show_stats(data):
    console.print("\n")
    console.print(Columns(build_stats_panels(data)))
    console.print()
    show_subject_breakdown(data)
    console.print()


def mostrar_portada(texto="Study Tracker"):
    ascii_art = figlet_format(texto)
    print(f"[bold rainbow]{ascii_art}[/bold rainbow]")
    console.print("[bold cyan]by KOAVHS[/bold cyan]")


def main():
    data = load_data()
    mostrar_portada()

    while True:
        console.print("\n[bold blue]Study Tracker[/bold blue]")
        console.print("1. Marcar hoy como estudiado")
        console.print("2. Ver calendario")
        console.print("3. Ver estadísticas")
        console.print("4. Salir")
        choice = input("Elige opción: ")

        if choice == "1":
            mark_today(data)
            data = load_data()
        elif choice == "2":
            show_calendar(data)
        elif choice == "3":
            data = load_data()
            show_stats(data)
        elif choice == "4":
            break
        else:
            console.print("[red]Opción inválida[/red]")


if __name__ == "__main__":
    main()