import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from detector import PackageDetector

console = Console()
detector = PackageDetector()

def risk_color(level):
    """Return color for risk level"""
    colors = {
        "SAFE": "green",
        "CAUTION": "yellow",
        "SUSPICIOUS": "red",
        "DANGEROUS": "bright_red"
    }
    return colors.get(level, "white")

def risk_emoji(level):
    """Return emoji for risk level"""
    emojis = {
        "SAFE": "✓",
        "CAUTION": "⚠",
        "SUSPICIOUS": "✕",
        "DANGEROUS": "⛔"
    }
    return emojis.get(level, "?")

@click.group()
def cli():
    """SlopSquat Shield: Detect AI-hallucinated package names before installation"""
    pass

@cli.command()
@click.argument("package_name")
def scan(package_name):
    """Scan a single package for risk"""
    console.print(f"\n[bold cyan]Scanning: {package_name}[/bold cyan]\n")
    
    result = detector.analyze_package(package_name)
    
    # Risk score badge
    score_color = risk_color(result["risk_level"])
    emoji = risk_emoji(result["risk_level"])
    
    console.print(
        Panel(
            f"[bold {score_color}]{emoji} {result['risk_level']}[/bold {score_color}] "
            f"(Score: {result['risk_score']}/100)",
            title=f"[bold]{package_name}[/bold]",
            border_style=score_color
        )
    )
    
    # Recommendation
    console.print(f"\n[bold]Recommendation:[/bold] {result['recommendation']}\n")
    
    # Flags
    if result["flags"]:
        console.print("[bold yellow]Warning Flags:[/bold yellow]")
        for flag in result["flags"]:
            console.print(f"  [yellow]•[/yellow] {flag}")
        console.print()
    
    # Registry info
    console.print("[bold]Registry Info:[/bold]")
    if result["pypi_info"].get("exists"):
        console.print(f"  [green]PyPI:[/green] Found")
        console.print(f"    Version: {result['pypi_info'].get('version', 'N/A')}")
        console.print(f"    Releases: {result['pypi_info'].get('num_releases', 'N/A')}")
    else:
        console.print(f"  [red]PyPI:[/red] Not found")
    
    if result["npm_info"].get("exists"):
        console.print(f"  [green]npm:[/green] Found")
        console.print(f"    Version: {result['npm_info'].get('version', 'N/A')}")
    else:
        console.print(f"  [red]npm:[/red] Not found")
    
    console.print()

@cli.command()
@click.argument("packages", nargs=-1, required=True)
def scan_multiple(packages):
    """Scan multiple packages"""
    console.print(f"\n[bold cyan]Scanning {len(packages)} packages...[/bold cyan]\n")
    
    table = Table(title="Package Risk Assessment", show_header=True, header_style="bold magenta")
    table.add_column("Package", style="cyan")
    table.add_column("Risk Level", justify="center")
    table.add_column("Score", justify="center")
    table.add_column("Recommendation", style="dim")
    
    for package in packages:
        result = detector.analyze_package(package)
        risk_style = risk_color(result["risk_level"])
        emoji = risk_emoji(result["risk_level"])
        
        table.add_row(
            result["package"],
            f"[{risk_style}]{emoji} {result['risk_level']}[/{risk_style}]",
            str(result["risk_score"]),
            result["recommendation"][:40] + "..." if len(result["recommendation"]) > 40 else result["recommendation"]
        )
    
    console.print(table)
    console.print()

@cli.command()
@click.argument("requirements_file")
def scan_requirements(requirements_file):
    """Scan a requirements.txt file"""
    try:
        with open(requirements_file, "r") as f:
            lines = f.readlines()
        
        packages = []
        for line in lines:
            line = line.strip()
            if line and not line.startswith("#"):
                # Extract package name (handle version specifiers)
                pkg = line.split("==")[0].split(">=")[0].split("<=")[0].split(">")[0].split("<")[0].split("~")[0].strip()
                packages.append(pkg)
        
        if not packages:
            console.print("[yellow]No packages found in requirements file[/yellow]")
            return
        
        console.print(f"\n[bold cyan]Scanning {len(packages)} packages from {requirements_file}[/bold cyan]\n")
        
        table = Table(title="Requirements Risk Assessment", show_header=True, header_style="bold magenta")
        table.add_column("Package", style="cyan")
        table.add_column("Risk Level", justify="center")
        table.add_column("Score", justify="center")
        table.add_column("Status", style="dim")
        
        for package in packages:
            result = detector.analyze_package(package)
            risk_style = risk_color(result["risk_level"])
            emoji = risk_emoji(result["risk_level"])
            
            table.add_row(
                result["package"],
                f"[{risk_style}]{emoji} {result['risk_level']}[/{risk_style}]",
                str(result["risk_score"]),
                "✓ OK" if result["risk_score"] < 20 else "⚠ Review"
            )
        
        console.print(table)
        console.print()
    
    except FileNotFoundError:
        console.print(f"[red]Error:[/red] File not found: {requirements_file}")

@cli.command()
def info():
    """Show project info"""
    info_text = """
[bold cyan]SlopSquat Shield[/bold cyan] v1.0

[bold]Security Research Project:[/bold]
Detecting AI-hallucinated package names in AI-generated code recommendations.

[bold]Capabilities:[/bold]
- Detects hallucinated packages from LLM responses
- Checks PyPI and npm registries in real-time
- Calculates risk scores based on multiple factors
- Scans requirements.txt files
- Provides actionable recommendations

[bold]Risk Factors:[/bold]
- Package in hallucination database
- Does not exist on PyPI/npm
- Recently created (last 7 days)
- Very low download count
- Single maintainer
- Suspicious naming patterns

[bold]Usage:[/bold]
scan <package>              - Scan a single package
scan-multiple <pkg1> <pkg2> - Scan multiple packages
scan-requirements <file>    - Scan requirements.txt file

[bold]Repository:[/bold]
https://github.com/shashansksn413/SlopSquat-Shield
"""
    console.print(Panel(info_text, title="[bold]About[/bold]", border_style="cyan"))

if __name__ == "__main__":
    cli()