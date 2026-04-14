from rich.console import Console

console = Console(stderr=True)

def info(msg: str) -> None:
    console.print(f"[cyan]INFO[/cyan]  {msg}")

def success(msg: str) -> None:
    console.print(f"[green]OK[/green]    {msg}")

def warn(msg: str) -> None:
    console.print(f"[yellow]WARN[/yellow]  {msg}")

def error(msg: str) -> None:
    console.print(f"[red]ERROR[/red] {msg}")
