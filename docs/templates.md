# Incident Templates

This document describes how to search for incident templates using the `HelixClient`.

## Search Incident Templates

Use `search_template()` to retrieve incident templates from BMC Helix.

```python
search_template(
    search_criteria=None,
    fields=None,
    use_like=False
)
```

### Parameters

| Parameter | Description |
|---|---|
| `search_criteria` | Dictionary containing the fields and values used to filter the search. Optional. |
| `fields` | List of fields to return. Optional. |
| `use_like` | Enables partial matching on `Template Name`. Defaults to `False`. |

### Basic Example

Search for a template by its exact name:

```python
templates = client.search_template(
    search_criteria={
        "Template Name": "Server CPU Alert"
    }
)

for template in templates:
    print(template)
```

### Partial Matching

Set `use_like=True` to search for templates whose names contain the specified text.

```python
templates = client.search_template(
    search_criteria={
        "Template Name": "Server"
    },
    use_like=True
)
```

### Selecting Specific Fields

You can specify which fields should be returned:

```python
templates = client.search_template(
    search_criteria={
        "Template Name": "Server CPU Alert"
    },
    fields=[
        "Template Name",
        "InstanceId"
    ]
)
```

The available fields depend on the BMC Helix environment and form configuration.

### Search Without Filters

If `search_criteria` is omitted or set to `None`, the method performs a search without filtering criteria.

```python
templates = client.search_template()
```

**Warning:** Searching without filters may return a large number of records.

## Pagination

The method uses offset-based pagination internally.

See [Pagination](pagination.md) for more details.

## Scope

This method only searches for existing incident templates. It does not create, update, delete, or apply templates to incidents.

## Error Handling

API errors, authentication failures, and other request-related problems are raised as `HelixClientError`.

```python
from bmc_helix_client import HelixClientError

try:
    templates = client.search_template(
        search_criteria={
            "Template Name": "Server CPU Alert"
        }
    )

except HelixClientError as error:
    print(f"Template search failed: {error}")
```
