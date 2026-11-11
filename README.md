# BMC Helix Client

A reusable Python client for interacting with the **BMC Helix ITSM REST API**.

The goal of this project is to provide a simple and reusable interface for developers who need to integrate Python applications with BMC Helix ITSM.

## Features

- JWT authentication.
- Centralized HTTP request handling.
- Search incidents.
- Search configuration items (CIs).
- Search business services.
- Search users and support groups.
- Validate user membership in support groups.
- Associate configuration items with incidents.
- Create incidents and worklogs.
- Search incident worklogs.
- Search incident templates.
- Automatic offset-based pagination.
- Flexible search criteria, including `LIKE` queries.

## Requirements

- Python 3.9 or later.
- Requests 2.32.3 or later.

## Installation

The package is currently under development and is not yet published on PyPI.

Clone the repository:

```bash
git clone https://github.com/brunoamorim-j/bmc-helix-client.git
cd bmc-helix-client
```

Install the package:

```bash
python -m pip install .
```

## Quick Start

```python
from bmc_helix_client import HelixClient

client = HelixClient(
    base_url="https://your-helix-instance",
    username="your_username",
    password="your_password"
)

client.authenticate()

incidents = client.search_incident(
    search_criteria={"Status": "open"}
)

print(incidents)
```

## Basic Examples

### Search Configuration Items

```python
cis = client.search_ci(
    search_criteria={"Name": "SERVER01"}
)

print(cis)
```

### Search Using LIKE

```python
cis = client.search_ci(
    search_criteria={"Name": "SERVER"},
    use_like=True
)

print(cis)
```

### Create an Incident

Incident creation is supported through `create_incident()`.

The required payload fields depend on your BMC Helix ITSM configuration.

See the [Incidents documentation](docs/incidents.md) for details.

## Documentation

Detailed documentation and usage examples:

| Document | Description |
|---|---|
| [Authentication](docs/authentication.md) | Client initialization, JWT authentication and SSL configuration |
| [Incidents](docs/incidents.md) | Search and create incidents, associate CIs and manage incident worklogs |
| [Configuration Items](docs/configuration_items.md) | Search configuration items |
| [Services](docs/services.md) | Search business services |
| [Users and Groups](docs/users_and_groups.md) | Search users and support groups and validate memberships |
| [Worklogs](docs/worklogs.md) | Search and create incident worklogs |
| [Templates](docs/templates.md) | Search incident templates |
| [Pagination](docs/pagination.md) | Understand pagination, sorting and result limits |

## Contributing

Contributions, suggestions, bug reports, and improvements are welcome.

Please read [CONTRIBUTING.md](CONTRIBUTING.md) before submitting a pull request.

## License

This project is licensed under the **GNU General Public License v3.0 (GPL-3.0)**.

See the [LICENSE](LICENSE) file for the full license text.
