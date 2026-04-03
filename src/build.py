"""
Build the org chart HTML from roster.xlsx + access.yaml.

Usage:
    python -m src.build
    python -m src.build --roster data/roster.xlsx --access data/access.yaml --out output/org_chart.html
"""

import json
from pathlib import Path
import click
from jinja2 import Environment, FileSystemLoader
from src.loader import load_roster
from src.access import load_access, merge_access_into_tree

REPO_ROOT = Path(__file__).parent.parent


@click.command()
@click.option("--roster", default="data/roster.xlsx", show_default=True,
              help="Path to the XLSX employee roster.")
@click.option("--access", default="data/access.yaml", show_default=True,
              help="Path to the access config YAML.")
@click.option("--out", default="output/org_chart.html", show_default=True,
              help="Output HTML file path.")
def build(roster, access, out):
    """Generate the org chart HTML."""
    roster_path = REPO_ROOT / roster
    access_path = REPO_ROOT / access
    out_path = REPO_ROOT / out

    click.echo(f"Loading roster:  {roster_path}")
    tree = load_roster(roster_path)

    click.echo(f"Loading access:  {access_path}")
    access_data = load_access(access_path)

    click.echo("Merging data…")
    merge_access_into_tree(tree, access_data)

    click.echo("Rendering template…")
    env = Environment(loader=FileSystemLoader(str(REPO_ROOT / "templates")))
    template = env.get_template("chart.html.jinja")

    html = template.render(
        tree_json=json.dumps(tree, ensure_ascii=False),
        tools_json=json.dumps(access_data["tools"], ensure_ascii=False),
    )

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(html, encoding="utf-8")
    click.echo(f"✓ Written to:    {out_path}")


if __name__ == "__main__":
    build()
