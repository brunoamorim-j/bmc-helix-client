# Incident Management

This document describes the incident-related operations available in `HelixClient`.

All operations require authentication before execution:

```python
from bmc_helix_client import HelixClient

client = HelixClient(
    base_url="https://your-helix-instance",
    username="your_username",
    password="your_password"
)

client.authenticate()
```

## 1. Search Incidents

Use `search_incident()` to retrieve incidents using one or more search criteria.

### Method

```python
search_incident(
    search_criteria,
    summary_search="equal",
    fields=None,
    limit=500,
    sleep_between_pages=0.1,
    max_records=None
)
```

### Parameters

| Parameter | Description |
|---|---|
| `search_criteria` | Dictionary containing search fields and values. Required. |
| `summary_search` | Search operator for the Description field: `equal` or `like`. |
| `fields` | List of fields to return. If omitted, all available fields are requested. |
| `limit` | Maximum number of records per page. |
| `sleep_between_pages` | Delay between paginated requests, in seconds. |
| `max_records` | Maximum number of records to return. `None` means no explicit limit. |

### Supported Search Fields

The following fields are supported:

- `First_Name`
- `Last_Name`
- `Description`
- `Detailed_Description`
- `Impact`
- `Urgency`
- `ServiceCI`
- `Status`
- `Reported Source`
- `Assigned Support Company`
- `Assigned Support Organization`
- `Assigned Group`
- `Categorization Tier 1`
- `Categorization Tier 2`
- `Categorization Tier 3`
- `Service_Type`
- `Request ID`
- `Incident Number`

### Status Values

The `Status` field supports the following values:

| Value | Behavior |
|---|---|
| `open` | Returns incidents with status below 4. |
| `completed` | Returns incidents with status above 3. |
| `new` | Status 0 |
| `assigned` | Status 1 |
| `in_progress` | Status 2 |
| `pending` | Status 3 |
| `resolved` | Status 4 |
| `closed` | Status 5 |
| `cancelled` | Status 6 |

### Examples

Search by incident number:

```python
incidents = client.search_incident(
    search_criteria={
        "Incident Number": "EXAMPLE-INCIDENT-ID"
    }
)

print(incidents)
```

Search open incidents:

```python
incidents = client.search_incident(
    search_criteria={
        "Status": "open"
    },
    fields=[
        "Incident Number",
        "Description",
        "Status",
        "Assigned Group"
    ]
)
```

Search using partial description:

```python
incidents = client.search_incident(
    search_criteria={
        "Description": "database connection"
    },
    summary_search="like"
)
```

Limit the number of returned records:

```python
incidents = client.search_incident(
    search_criteria={
        "Status": "completed"
    },
    limit=100,
    max_records=250
)
```

**Important:**

- Search criteria are combined using the `AND` operator.
- At least one valid search criterion must be provided.
- The `like` operator applies to the `Description` field.
- Results are retrieved using automatic pagination.

## 2. Create Incidents

Use `create_incident()` to create a new incident through the `HPD:IncidentInterface_Create` form.

### Method

```python
create_incident(
    incident_data,
    fields=None
)
```

### Parameters

| Parameter | Description |
|---|---|
| `incident_data` | Dictionary containing the incident payload according to the Helix API schema. |
| `fields` | List of fields to return after creation. If omitted, only `Incident Number` is returned. Use `["*"]` to request all available fields. |

### Example – Minimal Incident Creation

The following example demonstrates a minimal payload for creating an incident:

```python
incident_data = {
    "values": {
        "Description": "CPU utilization above threshold",
        "Impact": "3-Moderate/Limited",
        "Urgency": "3-Medium",
        "Reported Source": "Other"
    }
}

created_incident = client.create_incident(
    incident_data=incident_data
)

print(f"Incident created: {created_incident['Incident Number']}")
```

**Note:** The example represents a minimal payload for the library. Additional mandatory fields may depend on your BMC Helix configuration, incident templates, and business rules.

### Requesting Additional Fields

By default, the method returns only the incident number.

You can request additional fields:

```python
created_incident = client.create_incident(
    incident_data=incident_data,
    fields=[
        "Incident Number",
        "Description",
        "Impact",
        "Urgency"
    ]
)

print(created_incident)
```

To request all available fields:

```python
created_incident = client.create_incident(
    incident_data=incident_data,
    fields=["*"]
)
```

**Important:**

- The method sends the provided payload directly to the Helix API.
- It does not automatically apply templates or business rules.
- Required fields and accepted values depend on your Helix configuration.
- The method returns a dictionary containing the fields requested from the API.

## 3. Search Incident Worklogs

Use `search_incident_worklog()` to retrieve worklogs associated with a specific incident.

### Method

```python
search_incident_worklog(
    incident_number,
    fields=None
)
```

### Parameters

| Parameter | Description |
|---|---|
| `incident_number` | Incident number. Required. |
| `fields` | List of fields to return. If omitted, only Submit Date is requested. |

### Examples

Search worklogs for an incident:

```python
worklogs = client.search_incident_worklog(
    incident_number="EXAMPLE-INCIDENT-ID"
)

print(worklogs)
```

Request specific fields:

```python
worklogs = client.search_incident_worklog(
    incident_number="EXAMPLE-INCIDENT-ID",
    fields=[
        "3",
        "1000000161",
        "Description",
        "Work Log ID"
    ]
)

print(worklogs)
```

**Important:**

- The search always filters by incident number.
- The incident number must be a valid string.
- Results are retrieved using automatic pagination.
- If no fields are specified, only the Submit Date field is requested.

## 4. Create Incident Worklogs

Use `create_incident_worklog()` to add a worklog to an existing incident.

### Method

```python
create_incident_worklog(
    worklog_data,
    fields=None
)
```

### Parameters

| Parameter | Description |
|---|---|
| `worklog_data` | Dictionary containing a `values` object with the worklog fields. |
| `fields` | List of fields to return. If omitted, only Work Log ID is returned. Use `["*"]` to request all available fields. |

### Example

```python
worklog_data = {
    "values": {
        "Incident Number": "EXAMPLE-INCIDENT-ID",
        "Description": "Investigation started.",
        "Work Log Type": "General Information",
        "View Access": "Internal"
    }
}

created_worklog = client.create_incident_worklog(
    worklog_data=worklog_data
)

print(created_worklog)
```

Request additional fields:

```python
created_worklog = client.create_incident_worklog(
    worklog_data=worklog_data,
    fields=[
        "Work Log ID",
        "Incident Number",
        "Description"
    ]
)

print(created_worklog)
```

**Important:**

- `worklog_data` must be a dictionary containing a `values` dictionary.
- Required fields and accepted values depend on your Helix configuration.
- The method returns the fields requested from the API.

## 5. Associate a Configuration Item with an Incident

Use `associate_ci_to_incident()` to associate an existing Configuration Item (CI) with an incident.

### Method

```python
associate_ci_to_incident(
    incident_number,
    ci_name,
    ci_recon_id
)
```

### Parameters

| Parameter | Description |
|---|---|
| `incident_number` | Incident number. |
| `ci_name` | Configuration Item name. |
| `ci_recon_id` | CI Reconciliation Identity. |

All parameters are required.

### Example

```python
success = client.associate_ci_to_incident(
    incident_number="EXAMPLE-INCIDENT-ID",
    ci_name="EXAMPLE-SERVER",
    ci_recon_id="RECONCILIATION_ID"
)

print(success)
```

The association is created with the following properties:

| Field | Value |
|---|---|
| CI Form | `AST:ComputerSystem` |
| Incident Form | `HPD:Help Desk` |
| Request Type | `Configuration Item` |
| Association Type | `Related to` |
| Status | `Enabled` |

The method returns `True` when the association is successfully created. API or validation failures raise `HelixClientError`.

## 6. Error Handling

All incident-related operations may raise `HelixClientError` when validation, authentication, communication, or API processing fails.

Example:

```python
from bmc_helix_client import HelixClientError

try:
    incidents = client.search_incident(
        search_criteria={
            "Incident Number": "EXAMPLE-INCIDENT-ID"
        }
    )

except HelixClientError as error:
    print(f"Helix operation failed: {error}")
```

## Notes

`HelixClient` provides direct access to the incident-related operations exposed by the BMC Helix REST API.

It does not implement application-specific workflows such as:

- Automatic incident deduplication.
- Template selection.
- Business-hours rules.
- Zabbix event processing.
- Automatic incident updates based on monitoring events.

These behaviors should be implemented by applications using the library, according to their own business requirements.