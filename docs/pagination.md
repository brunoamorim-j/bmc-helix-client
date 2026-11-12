

# Pagination

This document describes how pagination is handled internally by the `HelixClient`.

## Overview

BMC Helix search results may contain multiple pages of records. The client handles pagination automatically using the `limit` and `offset` parameters.

You do not need to implement pagination manually when using the public search methods.

The internal pagination mechanism uses:

- `limit`: Maximum number of records requested per API request.
- `offset`: Position from which the next set of records is retrieved.

## Default Behavior

The internal pagination method uses the following defaults:

| Parameter | Default | Description |
|---|---:|---|
| `limit` | `500` | Maximum number of records per request. |
| `sleep_between_pages` | `0.1` | Delay in seconds between requests. |
| `max_records` | `None` | Optional maximum number of records returned. |

The client automatically retrieves subsequent pages until there are no more records to retrieve or another stopping condition is reached.

## Automatic Pagination

Public search methods use the internal pagination mechanism.

For example:

```python
cis = client.search_ci(
    search_criteria={
        "Name": "EXAMPLE"
    }
)
```

Even if the search returns more than 500 records, the client automatically requests additional pages.

## Maximum Number of Records

The `max_records` parameter can limit the total number of records returned by supported search methods.

For example:

```python
incidents = client.search_incident(
    search_criteria={
        "Status": "open"
    },
    limit=500,
    max_records=1000
)
```

**Note:** `_paginated_search()` is an internal method. Public search methods should be preferred for normal usage.

## Duplicate Handling

When an `id_field` is provided, the client uses that field to avoid adding duplicate records to the result set.

Each record is identified using the value of the configured ID field.

## Stopping Conditions

Pagination stops when one of the following conditions occurs:

- Helix returns an empty page.
- A page does not contain any new records.
- The configured `max_records` limit is reached.
- The number of records returned by Helix is smaller than the requested page size.

## Request Delay

The `sleep_between_pages` parameter controls the delay between pagination requests.

This can help reduce the frequency of consecutive API requests.

A value of `0` disables the delay.

## Error Handling

Errors during pagination, including API request failures and invalid response structures, are raised as `HelixClientError`.
