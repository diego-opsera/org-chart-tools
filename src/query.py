"""
CLI query tool for access data.

Usage:
    python -m src.query who --tool github
    python -m src.query who --tool jira --role org_admin --min
    python -m src.query tools --person "Lance, Christian"
    python -m src.query reports-to --person "Lance, Christian"
    python -m src.query reports-to --person "Lance, Christian" --recursive
"""

from pathlib import Path
import click
from rich.console import Console
from rich.table import Table
from rich import box
from src.loader import load_roster, flatten
from src.access import load_access, query_who_has_role, query_person_access

REPO_ROOT = Path(__file__).parent.parent
console = Console()


def _load(roster_opt, access_opt):
    roster_path = REPO_ROOT / roster_opt
    access_path = REPO_ROOT / access_opt
    tree = load_roster(roster_path)
    access_data = load_access(access_path)
    return tree, access_data


@click.group()
@click.option("--roster", default="data/roster.xlsx", show_default=True)
@click.option("--access", default="data/access.yaml", show_default=True)
@click.pass_context
def cli(ctx, roster, access):
    """Query the org chart and access configuration."""
    ctx.ensure_object(dict)
    ctx.obj["roster"] = roster
    ctx.obj["access"] = access


@cli.command()
@click.option("--tool", required=True, help="Tool ID (e.g. github, jira, aws)")
@click.option("--role", default=None, help="Role ID to filter by")
@click.option("--min", "min_role", is_flag=True, default=False,
              help="Match this role or any more-privileged role")
@click.pass_context
def who(ctx, tool, role, min_role):
    """Show who has access to a tool (optionally filtered by role)."""
    _, access_data = _load(ctx.obj["roster"], ctx.obj["access"])

    if tool not in access_data["tools"]:
        console.print(f"[red]Unknown tool '{tool}'. Known tools: "
                      f"{', '.join(access_data['tools'].keys())}[/red]")
        return

    results = query_who_has_role(access_data, tool, role, min_role)

    if not results:
        console.print(f"[yellow]No matches found.[/yellow]")
        return

    tool_def = access_data["tools"][tool]
    tool_color = tool_def["color"].lstrip("#")
    title = f"{tool_def['display_name']} access"
    if role:
        qualifier = "≥" if min_role else "="
        title += f"  (role {qualifier} {role})"

    t = Table(title=title, box=box.ROUNDED, show_header=True, header_style="bold")
    t.add_column("Name", style="bold")
    t.add_column("Role")
    t.add_column("Scope", style="dim")
    t.add_column("Source", style="dim")

    for r in sorted(results, key=lambda x: x["name"]):
        role_label = next(
            (rl["label"] for rl in tool_def["roles"] if rl["id"] == r["role"]),
            r["role"]
        )
        t.add_row(r["name"], role_label, r.get("scope") or "—", r.get("source", "manual"))

    console.print(t)


@cli.command()
@click.option("--person", required=True, help="Person name in 'Last, First' format")
@click.pass_context
def tools(ctx, person):
    """Show all tool access grants for a person."""
    _, access_data = _load(ctx.obj["roster"], ctx.obj["access"])

    results = query_person_access(access_data, person)

    if not results:
        console.print(f"[yellow]No access entries found for '{person}'.[/yellow]")
        return

    t = Table(title=f"Access grants for {person}", box=box.ROUNDED, header_style="bold")
    t.add_column("Tool")
    t.add_column("Role")
    t.add_column("Scope", style="dim")
    t.add_column("Source", style="dim")

    for r in sorted(results, key=lambda x: x["tool"]):
        tool_def = access_data["tools"].get(r["tool"], {})
        role_label = next(
            (rl["label"] for rl in tool_def.get("roles", []) if rl["id"] == r["role"]),
            r["role"]
        )
        t.add_row(
            tool_def.get("display_name", r["tool"]),
            role_label,
            r.get("scope") or "—",
            r.get("source", "manual"),
        )

    console.print(t)


@cli.command("reports-to")
@click.option("--person", required=True, help="Manager name in 'Last, First' format")
@click.option("--recursive", is_flag=True, default=False,
              help="Include all indirect reports (full subtree)")
@click.pass_context
def reports_to(ctx, person, recursive):
    """Show who reports to a given person."""
    tree, _ = _load(ctx.obj["roster"], ctx.obj["access"])
    all_employees = flatten(tree)

    # Find the subtree rooted at person
    target = next((e for e in all_employees if e["name"] == person), None)
    if target is None:
        console.print(f"[red]'{person}' not found in roster.[/red]")
        return

    if recursive:
        # All descendants except the person themselves
        subtree = flatten(target)[1:]
        title = f"All reports under {person} ({len(subtree)} people)"
    else:
        subtree = target.get("children", [])
        title = f"Direct reports of {person} ({len(subtree)} people)"

    if not subtree:
        console.print(f"[yellow]No reports found for '{person}'.[/yellow]")
        return

    t = Table(title=title, box=box.ROUNDED, header_style="bold")
    t.add_column("Name", style="bold")
    t.add_column("Reports To", style="dim")

    for emp in sorted(subtree, key=lambda x: x["name"]):
        t.add_row(emp["name"], emp.get("reports_to", "—"))

    console.print(t)


if __name__ == "__main__":
    cli()
