from rich.console import Console
from rich.table import Table
from datetime import datetime
import json
import os
import time

console = Console()
FILE = 'study_data.json'

def load_data():
    if not os.path.exists(FILE):
        return {}
    
    with open(FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(FILE, "w") as f:
        json.dump(data, f, indent=4)
        
        
def mark_today(data):
    materia = input("Materia estudiada: ")
    today = datetime.now().strftime("%Y-%m-%d")
    
    if today not in data:
        data[today] = []

    data[today].append(materia)

    save_data(data)

    console.print(f"[green]✔ Agregaste '{materia}' al día {today}[/green]")
    
def show_calendar(data):
    today = datetime.now().strftime("%Y-%m-%d")
    table = Table(title="Study Tracker")
    
    table.add_column("Fecha", justify="center", style="bold red")
    table.add_column("Materias", justify="center", style="bold green")
    table.add_column("Estado", justify="center", style="bold yellow")
    
    for day, materia in sorted(data.items()):
        if len(materia) > 0:
            estado = "[green]✔ Estudiado[/green]" if day == today else "[red]✘ No estudiado[/red]"
            status_str = ", ".join(materia)
            table.add_row(day, status_str, estado)
            
    console.print(table)



def show_stats(data):
    total = len(data)
    done = sum(1 for v in data.values() if v)

    if total == 0:
        console.print("[yellow]Aún no hay datos[/yellow]")
        return

    porcentaje = (done / total) * 100
    console.print(f"[cyan]Progreso:[/cyan] {done}/{total} días ({porcentaje:.2f}%)")


def main():
    data = load_data()

    while True:
        console.print("\n[bold blue]Study Tracker[/bold blue]")
        console.print("1. Marcar hoy como estudiado")
        console.print("2. Ver calendario")
        console.print("3. Ver estadísticas")
        console.print("4. Salir")

        choice = input("Elige opción: ")

        if choice == "1":
            mark_today(data)
        elif choice == "2":
            show_calendar(data)
        elif choice == "3":
            show_stats(data)
        elif choice == "4":
            break
        else:
            console.print("[red]Opción inválida[/red]")


if __name__ == "__main__":
    main()


