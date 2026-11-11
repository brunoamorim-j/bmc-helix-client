# Users and Support Groups

This document describes how to search for users and support groups, and how to validate user membership in a support group.

## Search Users

Use `search_user()` to retrieve user records from BMC Helix.

```python
search_user(
    search_criteria=None,
    fields=None,
    like_field="Internet E-mail",
    id_field="Remedy Login ID",
    use_like=False
)
```

### Parameters

| Parameter | Description |
|---|---|
| `search_criteria` | Dictionary containing the search filters. Optional. |
| `fields` | List of fields to return. Optional. |
| `like_field` | Field used for partial matching when `use_like=True`. Defaults to `Internet E-mail`. |
| `id_field` | Field used internally to identify records during pagination. Defaults to `Remedy Login ID`. |
| `use_like` | Enables partial matching on the field specified by `like_field`. Defaults to `False`. |

### Example

Search for a user by login:

```python
users = client.search_user(
    search_criteria={
        "Remedy Login ID": "example.user"
    }
)

for user in users:
    print(user)
```

To search using partial matching:

```python
users = client.search_user(
    search_criteria={
        "Internet E-mail": "example"
    },
    like_field="Internet E-mail",
    use_like=True
)
```

## Search Support Groups

Use `search_support_groups()` to retrieve support groups.

```python
search_support_groups(
    search_criteria=None,
    fields=None,
    use_like=False
)
```

### Parameters

| Parameter | Description |
|---|---|
| `search_criteria` | Dictionary containing the search filters. Optional. |
| `fields` | List of fields to return. Optional. |
| `use_like` | Enables partial matching on `Support Group Name`. Defaults to `False`. |

### Example

Search for a support group by name:

```python
groups = client.search_support_groups(
    search_criteria={
        "Support Group Name": "Example Support Group"
    }
)

for group in groups:
    print(group)
```

Partial matching:

```python
groups = client.search_support_groups(
    search_criteria={
        "Support Group Name": "Monitoração"
    },
    use_like=True
)
```

## Validate User Membership in a Support Group

Use `validate_user_in_group()` to check whether a user belongs to a specific support group and has an enabled association.

```python
validate_user_in_group(
    person_id,
    support_group_id
)
```

### Parameters

| Parameter | Description |
|---|---|
| `person_id` | Person ID of the user. |
| `support_group_id` | ID of the support group. |

### Example

```python
is_member = client.validate_user_in_group(
    person_id="EXAMPLE_PERSON_ID",
    support_group_id="EXAMPLE_GROUP_ID"
)

if is_member:
    print("User belongs to the support group.")
else:
    print("User does not have an enabled association with the support group.")
```

The method returns:

- `True` if at least one enabled association exists.
- `False` if no enabled association exists.

Invalid parameters or API errors raise `HelixClientError`.

## Search Without Filters

Both `search_user()` and `search_support_groups()` accept searches without filters.

```python
users = client.search_user()
groups = client.search_support_groups()
```

**Warning:** Searching without filters may return a large number of records.

## Pagination

Search methods use offset-based pagination internally.

See [Pagination](pagination.md) for more details.

## Error Handling

API errors, authentication failures, and other request-related problems are raised as `HelixClientError`.

```python
from bmc_helix_client import HelixClientError

try:
    users = client.search_user(
        search_criteria={
            "Remedy Login ID": "example.user"
        }
    )

except HelixClientError as error:
    print(f"User search failed: {error}")
```

