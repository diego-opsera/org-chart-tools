# org-chart-tools

A Python tool for building interactive organizational charts from employee roster data and managing access control across multiple tools (GitHub, Jira, Salesforce, Okta, AWS, and more).

## Features

- **Org chart visualization** — converts an Excel roster into an interactive HTML org chart
- **Access management** — tracks who has access to which tools, with role hierarchies per tool
- **CLI queries** — look up direct reports, team trees, and access grants from the terminal
- **Data validation** — JSON Schema validation keeps `access.yaml` well-formed

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Build the org chart

```bash
python -m src.build
# options:
#   --roster  data/roster.xlsx        (default)
#   --access  data/access.yaml        (default)
#   --out     output/org_chart.html   (default)
```

### Query the org chart

```bash
# List everyone with access to a tool
python -m src.query who --tool github

# Filter by role (returns users with at least that role)
python -m src.query who --tool jira --role org_admin --min

# List all tools a person has access to
python -m src.query tools --person "Last, First"

# Show direct reports
python -m src.query reports-to --person "Last, First"

# Show full team tree recursively
python -m src.query reports-to --person "Last, First" --recursive
```

## Data files

| File | Description |
|------|-------------|
| `data/roster.xlsx` | Employee roster with `NAME` and `REPORTS TO` columns |
| `data/access.yaml` | Tool definitions, role hierarchies, and access grants |
| `templates/chart.html.jinja` | Jinja2 template for the rendered HTML org chart |

### access.yaml structure

```yaml
tools:
  github:
    roles: [member, admin, org_owner]  # ordered lowest → highest
    grants:
      - person: "Last, First"
        role: admin
```

## Project layout

```
src/
  build.py       # main build script
  loader.py      # reads Excel roster, builds tree
  query.py       # CLI query commands
  access.py      # loads/validates access.yaml, merges with tree
  schema.py      # JSON Schema for access.yaml
integrations/
  base.py        # abstract base for future API sync integrations
data/
templates/
output/          # generated files (git-ignored)
```

## Tech stack

Python 3 · openpyxl · PyYAML · Jinja2 · Click · Rich · jsonschema
