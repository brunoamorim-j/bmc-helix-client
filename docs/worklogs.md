

# Incident Worklogs

This document describes how to search and create worklogs associated with incidents.

## Search Incident Worklogs

Use `search_incident_worklog()` to retrieve worklogs associated with a specific incident.

```python
search_incident_worklog(
    incident_number,
    fields=None
)
```

### Parameters

| Parameter | Description |
|---|---|
| `incident_number` | Incident Number used to filter the worklogs. Required. |
| `fields` | List of fields to return. Optional. |

### Example

```python
worklogs = client.search_incident_worklog(
    incident_number="EXAMPLE-INCIDENT-ID"
)

for worklog in worklogs:
    print(worklog)
```

By default, the method requests the field with ID `3` (Submit Date).

You can specify additional fields:

```python
worklogs = client.search_incident_worklog(
    incident_number="EXAMPLE-INCIDENT-ID",
    fields=[
        "3",
        "Description",
        "Work Log Type"
    ]
)
```

The available fields depend on the BMC Helix form configuration.

## Create Incident Worklogs

Use `create_incident_worklog()` to add a worklog to an existing incident.

```python
create_incident_worklog(
    worklog_data,
    fields=None
)
```

### Parameters

| Parameter | Description |
|---|---|
| `worklog_data` | Dictionary containing the worklog data. Must include a `values` dictionary. |
| `fields` | List of response fields to return. Optional. |

### Example

```python
worklog_data = {
    "values": {
        "Incident Number": "EXAMPLE-INCIDENT-ID",
        "Description": "Investigation performed by the monitoring team.",
        "Work Log Type": "General Information",
        "View Access": "Internal"
    }
}

response = client.create_incident_worklog(worklog_data)

print(response)
```

The example fields are illustrative. Required fields and accepted values may vary depending on your BMC Helix configuration.

### Selecting Response Fields

You can specify which fields should be returned:

```python
response = client.create_incident_worklog(
    worklog_data,
    fields=[
        "Work Log ID",
        "Submit Date"
    ]
)
```

To request all response fields:

```python
response = client.create_incident_worklog(
    worklog_data,
    fields=["*"]
)
```

## Error Handling

The methods raise `HelixClientError` when validation or API requests fail.

```python
from bmc_helix_client import HelixClientError

try:
    worklogs = client.search_incident_worklog(
        incident_number="EXAMPLE-INCIDENT-ID"
    )

except HelixClientError as error:
    print(f"Worklog operation failed: {error}")
```
