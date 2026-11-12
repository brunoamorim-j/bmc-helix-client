

# Configuration Items

This document describes how to search for Configuration Items (CIs) using the `HelixClient`.

## Search Configuration Items

Use the `search_ci()` method to retrieve Configuration Items from BMC Helix.

```python
search_ci(
    search_criteria=None,
    fields=None,
    use_like=False
)
```

### Parameters

| Parameter | Description |
|---|---|
| `search_criteria` | Dictionary containing the fields and values used to filter the search. Optional. |
| `fields` | List of fields to return. If omitted, all fields are requested. |
| `use_like` | Enables partial matching for the `Name` field. Defaults to `False`. |

### Basic Example

Search for a CI using its exact name:

```python
cis = client.search_ci(
    search_criteria={
        "Name": "EXAMPLE-SERVER"
    }
)

for ci in cis:
    print(ci)
```

### Partial Matching

Set `use_like=True` to perform a partial match on the `Name` field.

```python
cis = client.search_ci(
    search_criteria={
        "Name": "EXAMPLE-SERVER"
    },
    use_like=True
)
```

This allows the search to return CIs whose names contain the specified text.

### Selecting Specific Fields

You can specify which fields should be returned:

```python
cis = client.search_ci(
    search_criteria={
        "Name": "EXAMPLE-SERVER"
    },
    fields=[
        "Name",
        "Reconciliation Identity",
        "AssetLifecycleStatus",
        "Environment Specification"
    ]
)
```

The available fields depend on the BMC Helix environment and the form configuration.

### Search Without Filters

If `search_criteria` is omitted or set to `None`, the method performs a search without filtering criteria.

```python
cis = client.search_ci()
```

**Warning:** Searching without filters may return a large number of records.

## Pagination

The method uses offset-based pagination internally to retrieve results from Helix.

See [Pagination](pagination.md) for more details.

## Error Handling

API errors, authentication failures, and other request-related problems are raised as `HelixClientError`.

```python
from bmc_helix_client import HelixClientError

try:
    cis = client.search_ci(
        search_criteria={
            "Name": "EXAMPLE-SERVER"
        }
    )

except HelixClientError as error:
    print(f"CI search failed: {error}")
```
