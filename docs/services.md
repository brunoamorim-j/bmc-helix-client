# Business Services

This document describes how to search for Business Services using the `HelixClient`.

## Search Business Services

Use the `search_service()` method to retrieve Business Services from BMC Helix.

```python
search_service(
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

Search for a Business Service by its exact name:

```python
services = client.search_service(
    search_criteria={
        "Name": "Example Service"
    }
)

for service in services:
    print(service)
```

### Partial Matching

Set `use_like=True` to perform a partial match on the `Name` field.

```python
services = client.search_service(
    search_criteria={
        "Name": "Example Service"
    },
    use_like=True
)
```

This allows the search to return services whose names contain the specified text.

### Selecting Specific Fields

You can specify which fields should be returned:

```python
services = client.search_service(
    search_criteria={
        "Name": "Example Service"
    },
    fields=[
        "Name",
        "ReconciliationIdentity"
    ]
)
```

Available fields depend on the BMC Helix environment and form configuration.

### Search Without Filters

If `search_criteria` is omitted or set to `None`, the method performs a search without filtering criteria.

```python
services = client.search_service()
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
    services = client.search_service(
        search_criteria={
            "Name": "Example Service"
        }
    )

except HelixClientError as error:
    print(f"Business Service search failed: {error}")
```
