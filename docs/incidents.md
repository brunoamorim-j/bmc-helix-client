

# Incidents

This document describes the incident-related operations available in `bmc_helix_client`.

## 1. Search Incidents

Use `search_incident()` to search incidents using one or more supported fields.

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
| `search_criteria` | Dictionary containing the search fields and their values. At least one valid criterion is required. |
| `summary_search` | Matching operator for the `Description` field only. Supports `equal` (exact match) and `like` (partial match). Other search fields are not affected. |
| `fields` | List of fields to return. If omitted, all fields are returned. |
| `limit` | Maximum number of records retrieved per API request. Default: `500`. |
| `sleep_between_pages` | Delay in seconds between pagination requests. Default: `0.1`. |
| `max_records` | Maximum total number of records to retrieve. If omitted, pagination continues until all available records are retrieved. |

### Example — Exact Match

```python
incidents = client.search_incident(
    search_criteria={
        "Assigned Group": "Example Support Group",
        "Status": "open",
        "Description": "Database connection failed"
    }
)
```

### Example — Partial Match

```python
incidents = client.search_incident(
    search_criteria={
        "Description": "database connection"
    },
    summary_search="like"
)
```

### Example — Multiple Criteria

```python
incidents = client.search_incident(
    search_criteria={
        "Assigned Group": "Example Support Group",
        "Status": "open",
        "Description": "database"
    },
    summary_search="like",
    fields=[
        "Incident Number",
        "Description",
        "Status",
        "Assigned Group"
    ],
    max_records=100
)
```

### Supported Search Fields

The following fields are supported by `search_incident()`:

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

The `Status` field accepts the following values:

| Value | Behavior |
|---|---|
| `open` | Returns incidents with status values below `4`. |
| `completed` | Returns incidents with status values above `3`. |
| `new` | Maps to status value `0`. |
| `assigned` | Maps to status value `1`. |
| `in_progress` | Maps to status value `2`. |
| `pending` | Maps to status value `3`. |
| `resolved` | Maps to status value `4`. |
| `closed` | Maps to status value `5`. |
| `cancelled` | Maps to status value `6`. |

### Important

- Search criteria are combined using the `AND` operator.
- At least one valid search criterion must be provided.
- By default, search criteria use equality matching (`=`), except for the special `Status` values described above.
- The `summary_search` parameter applies exclusively to the `Description` field.
- When `summary_search="like"` is used, partial matching is applied to `Description` using wildcards on both sides (`%value%`).
- Other fields are not affected by `summary_search` and retain their default matching behavior.
- If `Description` is not included in `search_criteria`, `summary_search` has no effect.
- Results are retrieved using automatic pagination with `limit` and `offset`.
- Results are sorted by `Incident Number` in ascending order.
- Duplicate incidents are removed using `Incident Number`.
- `max_records` limits the total number of records retrieved across pagination requests.

---

## 2. Create Incidents

Use `create_incident()` to create a new incident.

### Method

```python
create_incident(incident_data, fields=None)
```

### Parameters

| Parameter | Description |
|---|---|
| `incident_data` | Dictionary containing the incident data to be submitted. |
| `fields` | List of fields to return. If omitted, only `Incident Number` is returned. |

### Example

```python
incident_data = {
    "values": {
        "Description": "Database connection failed",
        "Detailed Description": "The application cannot connect to the database.",
        "Impact": "1-Extensive/Widespread",
        "Urgency": "1-Critical",
        "Reported Source": "Other",
        "Service Type": "User Service Restoration",
        "Assigned Group": "Example Support Group"
    }
}

incident = client.create_incident(incident_data)

print(incident["Incident Number"])
```

### Returning All Fields

Use `fields=["*"]` to request all available fields in the response.

```python
incident = client.create_incident(
    incident_data,
    fields=["*"]
)
```

### Important

- The incident payload is submitted directly to the Helix API.
- Required fields and accepted values depend on the configuration of the Helix instance.
- This method does not apply templates or business rules. Those responsibilities belong to the application using the library.
- The default response contains the `Incident Number`.

---

## 3. Search Incident Worklogs

Use `search_incident_worklog()` to retrieve worklogs associated with a specific incident.

### Method

```python
search_incident_worklog(incident_number, fields=None)
```

### Parameters

| Parameter | Description |
|---|---|
| `incident_number` | Incident number used to filter the worklogs. |
| `fields` | List of fields to return. If omitted, only `Submit Date` is returned. |

### Example

```python
worklogs = client.search_incident_worklog(
    incident_number="EXAMPLE-INCIDENT-ID",
    fields=[
        "Work Log ID",
        "Submit Date",
        "Description",
        "Detailed Description"
    ]
)

for worklog in worklogs:
    print(worklog)
```

### Important

- Worklogs are filtered using an exact match on `Incident Number`.
- Results are retrieved using automatic pagination.
- If `fields` is omitted, only `Submit Date` is requested.

---

## 4. Create Incident Worklogs

Use `create_incident_worklog()` to add a worklog to an incident.

### Method

```python
create_incident_worklog(worklog_data, fields=None)
```

### Parameters

| Parameter | Description |
|---|---|
| `worklog_data` | Dictionary containing the worklog data. The payload must include a `values` dictionary. |
| `fields` | List of fields to return. If omitted, only `Work Log ID` is returned. |

### Example

```python
worklog_data = {
    "values": {
        "Incident Number": "EXAMPLE-INCIDENT-ID",
        "Description": "Incident investigation",
        "Detailed Description": "Initial investigation has been completed."
    }
}

worklog = client.create_incident_worklog(worklog_data)

print(worklog["Work Log ID"])
```

### Returning All Fields

```python
worklog = client.create_incident_worklog(
    worklog_data,
    fields=["*"]
)
```

### Important

- The payload must contain a `values` dictionary.
- Required fields and accepted values depend on the Helix instance configuration.
- The default response contains the `Work Log ID`.

---

## 5. Associate a Configuration Item with an Incident

Use `associate_ci_to_incident()` to create an association between a configuration item (CI) and an incident.

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
| `incident_number` | Incident number to associate with the CI. |
| `ci_name` | Name of the configuration item. |
| `ci_recon_id` | Reconciliation Identity of the configuration item. |

### Example

```python
result = client.associate_ci_to_incident(
    incident_number="EXAMPLE-INCIDENT-ID",
    ci_name="EXAMPLE-SERVER",
    ci_recon_id="EXAMPLE-RECONCILIATION-ID"
)

print(result)
```

### Important

- Creates an association record linking a configuration item to an incident through the Helix API.
- The association uses the `Related to` association type.
- The association status is set to `Enabled`.
- The method does not perform a prior search to verify the existence of the CI or incident.
- The CI must be identified using its Reconciliation Identity.

---

## 6. Error Handling

All operations require authentication before execution.

The library raises `HelixClientError` when an operation fails, including authentication errors, invalid parameters, and API request failures.

### Example

```python
from bmc_helix_client import HelixClient, HelixClientError

try:
    client = HelixClient(
        base_url="https://helix.example.com",
        username="your_username",
        password="your_password"
    )

    client.authenticate()

    incidents = client.search_incident(
        search_criteria={
            "Status": "open"
        }
    )

except HelixClientError as error:
    print(f"Helix operation failed: {error}")
```

---

## 7. Notes

- Call `authenticate()` before using incident-related methods.
- Search methods return a list of dictionaries.
- Create methods return a dictionary containing the requested response fields.
- Use `fields=["*"]` when the complete API response is required.
- Pagination is handled internally by the library for supported search operations.
- The library provides API communication and does not implement application-specific incident management workflows.
