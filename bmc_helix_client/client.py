import requests as req
import time

from typing import Any, Dict, List, Optional, Set
from .exceptions import HelixClientError

ERROR_PREFIX = "[HELIX_CLIENT]"

class HelixClient:
    """
    Client for interacting with the BMC Helix REST API.

    This class provides:
    - JWT authentication
    - Authenticated HTTP requests
    - Helix AR System query construction
    - Automatic result pagination
    - Search and creation operations for incidents, users, CIs, and other records
    """

    FIELD_MAP_HPD_HELP_DESK: Dict[str, str] = {
        "First_Name": "1000000019",
        "Last_Name": "1000000018",
        "Description": "1000000000",
        "Detailed_Description": "1000000151",
        "Impact": "1000000163",
        "Urgency": "1000000162",
        "ServiceCI": "200000020",
        "Status": "7",
        "Reported Source": "1000000215",
        "Assigned Support Company": "1000000426",
        "Assigned Support Organization": "1000000014",
        "Assigned Group": "1000000217",
        "Categorization Tier 1": "1000000063",
        "Categorization Tier 2": "1000000064",
        "Categorization Tier 3": "1000000065",
        "Service_Type": "1000000099",
        "Request ID": "1",
        "Incident Number": "1000000161"
    }
    
    FIELD_MAP_INCIDENT_STATUS: Dict[str, int] = {
        "new": 0,
        "assigned": 1,
        "in_progress": 2,
        "pending": 3,
        "resolved": 4,
        "closed": 5,
        "cancelled": 6
    }

    FIELD_MAP_HPD_WORKLOG: Dict[str, str] = {
        "Submit Date": "3",
        "Incident Number": "1000000161"
    }
    
    def __init__(
        self,
        base_url: str,
        username: str,
        password: str,
        timeout: int=60,
        verify_ssl: bool=True
    ) -> None:
        """
        Initialize the Helix client.

        Args:
            base_url: Base URL of the Helix instance.
            username: Username used for authentication.
            password: Password used for authentication.
            timeout: Maximum time in seconds to wait for an HTTP request.
            verify_ssl: Whether to verify the server's SSL certificate.

        Notes:
            - The JWT token is not obtained automatically.
            - Call `authenticate()` before performing authenticated operations.
        """
        if not base_url:
            raise HelixClientError(f"{ERROR_PREFIX}: base_url não pode ser vazio")

        if not username:
            raise HelixClientError(f"{ERROR_PREFIX}: username não pode ser vazio")

        if not password:
            raise HelixClientError(f"{ERROR_PREFIX}: password não pode ser vazio")

        if timeout <= 0:
            raise HelixClientError(f"{ERROR_PREFIX}: timeout deve ser maior que zero")
        
        self.base_url = base_url.rstrip("/")
        self.username = username
        self.password = password
        self.timeout = timeout
        self.verify_ssl = verify_ssl
        self.jwt_token: Optional[str] = None

    def authenticate(self) -> None:
        """
        Authenticate with the Helix API and retrieve a JWT token.

        Sends an HTTP POST request to the Helix authentication endpoint
        (`/api/jwt/login`) using the credentials provided during
        client initialization.

        The API is expected to return the token in the response body
        (`response.text`). The token is stored in `self.jwt_token` and
        automatically included in subsequent authenticated requests.

        Authentication flow:
            - Send a POST request to `/api/jwt/login`.
            - Validate the HTTP response status.
            - Extract the JWT token from the response body.
            - Store the token in `self.jwt_token`.

        Notes:
            - The token is only checked for an empty value; its structure is not validated.
            - This method must be called before any authenticated operation.
            - If authentication fails, the client's authentication state remains unchanged.

        Raises:
            HelixClientError: If the request times out, an HTTP or connection error
                occurs, the API returns an empty token, or an unexpected error occurs.
        """
        url: str = f"{self.base_url}/api/jwt/login"
        response: Optional[req.Response] = None
        
        try:
            response = req.post(
                url,
                data={"username": self.username,"password": self.password},
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=self.timeout,
                verify=self.verify_ssl
            )
            
            response.raise_for_status()
            token: str = response.text
            if not token:
                raise HelixClientError(f"{ERROR_PREFIX}: Token JWT vazio retornado pelo Helix.")
            
            self.jwt_token = token

        except req.exceptions.Timeout as timeout_err:
            raise HelixClientError(f"{ERROR_PREFIX}: Timeout ao obter token JWT: {timeout_err}") from timeout_err

        except req.exceptions.HTTPError as http_err:
            resp_text = getattr(response, "text", "N/A")
            status_code = getattr(response, "status_code", "N/A")
            raise HelixClientError(
                f"{ERROR_PREFIX}: Erro HTTP ao obter Token JWT: "
                f"status={status_code}, erro={http_err}, resposta={resp_text}"
            ) from http_err

        except req.exceptions.ConnectionError as conn_err:
            raise HelixClientError(f"{ERROR_PREFIX}: Erro de conexão ao tentar obter token JWT de {url}: {conn_err}.") from conn_err
        

        except req.exceptions.RequestException as req_err:
            raise HelixClientError(f"{ERROR_PREFIX}: Erro de requisição ao autenticar no Helix: {req_err}.") from req_err

        except Exception as err:
            raise HelixClientError(f"{ERROR_PREFIX}: Erro inesperado durante autenticação no Helix: {err}") from err

    def _request_helix(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str,Any]]=None,
        json_data: Optional[Dict[str,Any]]=None
    ) -> req.Response:
        """
        Execute an authenticated HTTP request to the Helix API.

        Centralizes HTTP communication and ensures that:
            - The client is authenticated.
            - The JWT authorization header is included automatically.
            - JSON payloads are sent correctly for POST and PUT requests.
            - HTTP and network errors are handled consistently.

        Args:
            method: HTTP method (GET, POST, PUT, or DELETE).
            endpoint: Relative API endpoint, such as `/api/arsys/v1/entry/...`.
            params: Optional query string parameters.
            json_data: Optional JSON payload sent in the request body.

        Returns:
            requests.Response: The HTTP response returned by the requests library.
                Access the response content through `.json()` or `.text`.

        Raises:
            HelixClientError: If the client is not authenticated, the request times
                out, an HTTP or connection error occurs, or an unexpected error occurs.

        ValueError:
            If an absolute URL is provided instead of a relative endpoint.
        """
 
        if not self.jwt_token:
            raise HelixClientError(f"{ERROR_PREFIX}: Cliente não autenticado. Use authenticate() primeiro.")
        
        if endpoint.startswith(("http://", "https://")):
            raise ValueError("Endpoint must be a relative URL.")

        url: str = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        
        headers: Dict[str, str] = {"Authorization": f"AR-JWT {self.jwt_token}"}
        
        if method.upper() in ("POST","PUT"):
            headers["Content-Type"] = "application/json"
        
        try:
            response = req.request(
                method=method,
                url = url,
                headers=headers,
                params=params,
                json = json_data,
                timeout= self.timeout,
                verify=self.verify_ssl
            )
        
            response.raise_for_status()
            return response


        except req.exceptions.Timeout as timeout_err:
            raise HelixClientError(
                f"{ERROR_PREFIX}: Timeout ao acessar endpoint '{endpoint}' "
                f"(método {method.upper()})."
            ) from timeout_err

        except req.exceptions.HTTPError as http_err:
            status_code = (
                http_err.response.status_code
                if http_err.response is not None
                else "N/A"
            )

            raise HelixClientError(
                f"{ERROR_PREFIX}: Erro HTTP {status_code} "
                f"ao acessar endpoint '{endpoint}' "
                f"(método {method.upper()})."
            ) from http_err

        except req.exceptions.ConnectionError as conn_err:
            raise HelixClientError(
                f"{ERROR_PREFIX}: Erro de conexão ao acessar endpoint "
                f"'{endpoint}' (método {method.upper()})."
            ) from conn_err

        except req.exceptions.RequestException as req_err:
            raise HelixClientError(
                f"{ERROR_PREFIX}: Falha na requisição para endpoint "
                f"'{endpoint}' (método {method.upper()})."
            ) from req_err

        except Exception as err:
            raise HelixClientError(
                f"{ERROR_PREFIX}: Erro inesperado ao acessar endpoint "
                f"'{endpoint}' (método {method.upper()})."
            ) from err

    def _build_query(
        self,
        criteria: Optional[Dict[str, Any]] = None,
        use_like: bool = False,
        like_field: Optional[str] = None
    ) -> Optional[str]:
        """
        Build a query in Helix AR System Query Language from a criteria dictionary.

        Converts structured filter parameters into a query string compatible
        with the Helix API, applying value escaping, operators, and type validation.

        Query construction rules:
            - Default operator: '='
            - LIKE is supported for a single field specified by `like_field`.
            - None values and empty strings are ignored.
            - String values are escaped automatically.
            - Integer values are used without quotes.
            - Returns None when no valid criteria are provided (interpreted as an unfiltered search).

        LIKE rules:
            - Only one field can use LIKE per call.
            - LIKE is applied only to the field specified by `like_field`.
            - The value is wrapped in wildcards: "%value%".

        Escaping:
            - Double quotes (") are escaped.
            - Backslashes (\\) are escaped.
            - Wildcard characters (% and _) are escaped.

        Args:
            criteria: Dictionary containing field names and filter values.
                Example: {"Status": "open", "Company": "Example"}.
            use_like: If True, enables partial matching on the field specified by `like_field`.
            like_field: Field that uses LIKE instead of equality.
                Required when `use_like=True` and must exist in `criteria`.

        Returns:
            Optional[str]: Formatted Helix query, or None if no valid criteria are found.

        Raises:
            HelixClientError: If `like_field` is missing or not present in `criteria`,
                or if a value has an unsupported type. Only strings and integers are accepted.
        """
        if not criteria:
            return None

        if use_like:
            if not like_field:
                raise HelixClientError(
                    f"{ERROR_PREFIX}: like_field é obrigatório quando use_like=True"
                )
            if like_field not in criteria:
                raise HelixClientError(
                    f"{ERROR_PREFIX}: like_field '{like_field}' não está presente em criteria"
                )

        def escape(value: Any) -> str:
            """
            Escape seguro para Helix query language.
            """
            value = str(value)
            value = value.replace("\\", "\\\\")
            value = value.replace('"', '""')
            value = value.replace("%", "\\%")
            value = value.replace("_", "\\_")
            return value

        conditions: List[str] = []

        for field, value in criteria.items():

            # ignora vazios
            if value is None or (isinstance(value, str) and not value.strip()):
                continue

            # valida tipo
            if not isinstance(value, (str, int)):
                raise HelixClientError(
                    f"{ERROR_PREFIX}: Tipo inválido para '{field}'. "
                    f"Esperado str ou int, recebido {type(value).__name__}"
                )

            # LIKE controlado
            if use_like and field == like_field:
                escaped_value = escape(value)
                conditions.append(f"'{field}' LIKE \"%{escaped_value}%\"")

            # igualdade
            else:
                if isinstance(value, int):
                    conditions.append(f"'{field}' = {value}")
                else:
                    escaped_value = escape(value)
                    conditions.append(f"'{field}' = \"{escaped_value}\"")

        if not conditions:
            return None

        return "(" + " AND ".join(conditions) + ")"

    def _paginated_search(
        self,
        endpoint: str,
        base_query: Optional[str],
        id_field: Optional[str] = None,
        fields: Optional[List[str]] = None,
        limit: int = 500,
        sort: Optional[str] = None,
        sleep_between_pages: float = 0.1,
        max_records: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve records from the Helix API using offset-based pagination.

        Sends multiple API requests to retrieve available records while
        respecting page limits and optionally removing duplicates.

        Features:
            - Automatic pagination using limit and offset.
            - Optional deduplication based on `id_field`.
            - Result count control through `max_records`.
            - Configurable result sorting.
            - Configurable delay between requests (throttling).

        Args:
            endpoint: Helix API endpoint.
            base_query: Helix query string, such as `('Status' = "Open")`.
            id_field: Field used to identify and deduplicate records.
            fields: List of fields to return. If None, all fields are requested.
            limit: Maximum number of records per page.
            sort: Result sorting expression, such as `"Submit Date.desc"`.
            sleep_between_pages: Delay in seconds between paginated requests.
            max_records: Maximum number of records to return.

        Returns:
            List[Dict[str, Any]]: Records returned by the API.

        Raises:
            HelixClientError: If pagination parameters are invalid, the API
                response is not valid JSON, the response structure is invalid,
                or communication with the API fails.
        """
        try:
            if not isinstance(limit, int) or limit <= 0:
                raise HelixClientError(f"{ERROR_PREFIX}: limit inválido")

            if not isinstance(sleep_between_pages, (int, float)) or sleep_between_pages < 0:
                raise HelixClientError(f"{ERROR_PREFIX}: sleep_between_pages inválido")

            all_results: List[Dict[str, Any]] = []
            seen_ids: Set[Any] = set()

            offset = 0
            page = 0

            # -------------------------
            # FIELDS
            # -------------------------
            fields_param = f"values({','.join(fields)})" if fields else "values(*)"

            # -------------------------
            # LOOP PAGINADO (OFFSET)
            # -------------------------
            while True:

                page += 1

                params: Dict[str, Any] = {
                    "limit": limit,
                    "offset": offset
                }

                if base_query:
                    params["q"] = base_query

                if sort:
                    params["sort"] = sort
                elif id_field:
                    params["sort"] = f"{id_field}.asc"

                if fields_param:
                    params["fields"] = fields_param

                response = self._request_helix(
                    "GET",
                    endpoint=endpoint,
                    params=params
                )

                try:
                    data = response.json()
                except ValueError as err:
                    raise HelixClientError(f"{ERROR_PREFIX}: Resposta não é JSON válido em {endpoint}") from err

                if not isinstance(data, dict):
                    raise HelixClientError(f"{ERROR_PREFIX}: Resposta inválida da API Helix (esperado JSON objeto).")

                entries = data.get("entries")

                if not entries:
                    break

                if not isinstance(entries, list):
                    raise HelixClientError(f"{ERROR_PREFIX}: Campo 'entries' inválido (esperado lista)")

                new_in_page = 0

                for entry in entries:
                    if max_records and len(all_results) >= max_records:
                        break
                    
                    values: Dict[str, Any] = entry.get("values", entry)

                    unique_id = None
                    if id_field and isinstance(values, dict):
                        unique_id = values.get(id_field)

                    if unique_id:
                        if unique_id not in seen_ids:
                            seen_ids.add(unique_id)
                            all_results.append(values)
                            new_in_page += 1
                    else:
                        all_results.append(values)
                        new_in_page += 1

                # -------------------------
                # CONTROLE
                # -------------------------
                if new_in_page == 0:
                    break

                offset += limit

                if max_records and len(all_results) >= max_records:
                    break

                if len(entries) < limit:
                    break

                if sleep_between_pages:
                    time.sleep(sleep_between_pages)

            return all_results

        except HelixClientError:
            raise
                
        except Exception as err:
            raise HelixClientError(f"{ERROR_PREFIX}: Erro durante paginação: {err}") from err
                
    def search_incident(
        self,
        search_criteria: Dict[str, Any],
        summary_search: str = "equal",
        fields: Optional[List[str]] = None,
        limit: int = 500,
        sleep_between_pages: float = 0.1,
        max_records: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for incidents in Helix using dynamic criteria.

        Search rules:
            - Fields must exist in `FIELD_MAP_HPD_HELP_DESK`.
            - Status supports:
                - "open": status values below 4.
                - "completed": status values above 3.
                - Named values defined in `FIELD_MAP_INCIDENT_STATUS`.
            - Description supports "equal" and "like" matching.
            - Multiple criteria are combined using AND.

        Args:
            search_criteria: Dictionary containing search fields and values.
            summary_search: Matching mode for the Description field.
                Supported values are "equal" and "like".
            fields: List of fields to return from the Helix API.
            limit: Maximum number of records per page.
            sleep_between_pages: Delay in seconds between paginated requests.
            max_records: Maximum number of records to return.

        Returns:
            List[Dict[str, Any]]: Matching incidents.

        Raises:
            HelixClientError: If a search field or status is invalid, the matching
                mode is unsupported, no valid criteria are provided, or the API
                request fails.
        """

        try:
            endpoint = "/api/arsys/v1/entry/HPD:Help Desk"

            field_map = self.FIELD_MAP_HPD_HELP_DESK
            status_map = self.FIELD_MAP_INCIDENT_STATUS

            processed_criteria: Dict[str, Any] = {}

            for key, value in search_criteria.items():

                if key not in field_map:
                    raise HelixClientError(f"{ERROR_PREFIX}: Campo de busca inválido: {key}")

                if value in (None, ""):
                    continue

                # STATUS: mantém lógica especial
                if key == "Status":
                    if value in ("open", "completed") or value in status_map:
                        processed_criteria[key] = value
                    else:
                        raise HelixClientError(f"{ERROR_PREFIX}: Status inválido: {value}")

                # DESCRIPTION: só valida operador
                elif key == "Description":
                    if summary_search not in ("equal", "like"):
                        raise HelixClientError(
                            f"{ERROR_PREFIX}: summary_search deve ser 'equal' ou 'like'"
                        )
                    processed_criteria[key] = value

                else:
                    processed_criteria[key] = value

            if not processed_criteria:
                raise HelixClientError(
                    f"{ERROR_PREFIX}: Nenhum critério de busca válido foi fornecido."
                )


            query = self._build_query(criteria=processed_criteria)

            if "'Status'" in query:
                # open
                if "open" in processed_criteria.get("Status", ""):
                    query = query.replace(
                        "'Status' = \"open\"",
                        "'Status' < 4"
                    )

                # completed
                elif "completed" in processed_criteria.get("Status", ""):
                    query = query.replace(
                        "'Status' = \"completed\"",
                        "'Status' > 3"
                    )

                # mapeado
                elif processed_criteria.get("Status") in status_map:
                    mapped = status_map[processed_criteria["Status"]]
                    query = query.replace(
                        f"'Status' = \"{processed_criteria['Status']}\"",
                        f"'Status' = {mapped}"
                    )

            if summary_search == "like":
                query = query.replace("= \"", "LIKE \"%")
                query = query.replace("\"", "%\"")

            return self._paginated_search(
                endpoint=endpoint,
                base_query=query,
                id_field="Incident Number",
                fields=fields,
                limit=limit,
                sort="Incident Number.asc",
                sleep_between_pages=sleep_between_pages,
                max_records=max_records
            )

        except HelixClientError:
            raise

        except Exception as err:
            raise HelixClientError(f"{ERROR_PREFIX}: Erro ao buscar incidentes no Helix: {err}") from err

    def search_service(
        self,
        search_criteria: Optional[Dict[str, Any]] = None,
        fields: Optional[List[str]] = None,
        use_like: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Search for business services in Helix (BMC.CORE:BMC_BusinessService).

        Search rules:
            - Uses `ReconciliationIdentity` as the record identifier.
            - Supports optional LIKE matching on the `Name` field.
            - Uses automatic pagination through `_paginated_search`.
            - Search criteria are optional. If omitted, no filters are applied.

        Args:
            search_criteria: Optional dictionary of search filters.
            fields: List of fields to return from the API.
            use_like: If True, uses LIKE matching on the `Name` field.

        Returns:
            List[Dict[str, Any]]: Matching business service records.

        Raises:
            HelixClientError: If query construction or the API request fails.
        """
        try:
            endpoint = "/api/arsys/v1/entry/BMC.CORE:BMC_BusinessService"
            id_field = "ReconciliationIdentity"

            query = self._build_query(
                criteria=search_criteria,
                use_like=use_like,
                like_field="Name"
            )

            return self._paginated_search(
                endpoint=endpoint,
                base_query=query,
                id_field=id_field,
                fields=fields,
                sort="Name.asc"
            )
        except HelixClientError:
            raise
        except Exception as err:
            raise HelixClientError(f"{ERROR_PREFIX}: Erro ao buscar Business Services no Helix: {err}") from err
    
    def search_ci(
        self,
        search_criteria: Optional[Dict[str, Any]] = None,
        fields: Optional[List[str]] = None,
        use_like: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Search for configuration items (CIs) in Helix (AST:ComputerSystem).

        Queries infrastructure assets registered in the Helix CMDB,
        supporting dynamic filters and optional partial name matching.

        Search rules:
            - Uses the `AST:ComputerSystem` form.
            - Uses `Reconciliation Identity` as the record identifier.
            - Supports optional LIKE matching on the `Name` field.
            - Uses automatic pagination through `_paginated_search`.

        Args:
            search_criteria: Optional dictionary of CI search filters.
                Example: {"Name": "example-server"}.
            fields: List of fields to return from the API.
            use_like: If True, applies partial matching to the `Name` field.

        Returns:
            List[Dict[str, Any]]: Matching configuration items.

        Raises:
            HelixClientError: If query construction, the API request, or pagination fails.
        """
        try:
            endpoint = "/api/arsys/v1/entry/AST:ComputerSystem"
            id_field = "Reconciliation Identity"
            
            query = self._build_query(
                criteria=search_criteria,
                use_like=use_like,
                like_field="Name"
            )        
            
            return self._paginated_search(
                    endpoint=endpoint,
                    base_query=query,
                    id_field=id_field,
                    fields=fields,
                    sort="Name.asc",
            )
        except HelixClientError:
            raise
        except Exception as err:
            raise HelixClientError(f"{ERROR_PREFIX}: Erro ao buscar CIs no Helix: {err}") from err
        
    def search_incident_worklog(
        self,
        incident_number: str,
        fields: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve worklogs associated with a specific incident (HPD:WorkLog).

        The incident number is used as a required filter for the search.

        Search rules:
            - `incident_number` is required and must be a non-empty string.
            - Matching is based on exact equality with `Incident Number`.
            - If `fields` is omitted, only `Submit Date` is requested.
            - Results are retrieved using automatic pagination.

        Args:
            incident_number: Helix incident number.
                Example: "EXAMPLE-INCIDENT-ID".
            fields: List of fields to return. If None, only `Submit Date` is requested.

        Returns:
            List[Dict[str, Any]]: Worklogs associated with the incident.

        Raises:
            HelixClientError: If the incident number is invalid or query construction,
                API communication, or pagination fails.
        """
        try:
            if not incident_number or not isinstance(incident_number, str):
                raise HelixClientError(f"{ERROR_PREFIX}: incident_number deve ser uma string válida.")

            endpoint = "/api/arsys/v1/entry/HPD:WorkLog"
            id_field = "Work Log ID"

            field_incident_number = self.FIELD_MAP_HPD_WORKLOG['Incident Number']

            # O critério sempre é o numero do incidente 7 : {numero incident}
            query = self._build_query(
                criteria={field_incident_number: incident_number}
            )

            if not fields:
                field_submit_date = self.FIELD_MAP_HPD_WORKLOG['Submit Date']
                fields = [field_submit_date]

            return self._paginated_search(
                endpoint=endpoint,
                base_query=query,
                id_field=id_field,
                fields=fields,
                sort="Work Log ID.asc"
            )
        except HelixClientError:
            raise

        except Exception as err:
            raise HelixClientError(f"{ERROR_PREFIX}: Erro ao buscar WorkLogs do incidente {incident_number}: {err}") from err
            
    def search_template(
        self,
        search_criteria: Optional[Dict[str, Any]] = None,
        fields: Optional[List[str]] = None,
        use_like: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Search for incident templates in Helix (HPD:Template).

        Supports dynamic filters and optional partial matching by template name.

        Search rules:
            - Uses the `HPD:Template` form.
            - Uses `InstanceId` as the record identifier.
            - Supports optional search criteria.
            - Supports LIKE matching on the `Template Name` field.
            - Uses automatic pagination through `_paginated_search`.

        Args:
            search_criteria: Optional dictionary of search filters.
            fields: List of fields to return from the API.
            use_like: If True, applies partial matching to `Template Name`.

        Returns:
            List[Dict[str, Any]]: Matching incident templates.

        Raises:
            HelixClientError: If query construction, the API request, or pagination fails.
        """
        try:
            endpoint = "/api/arsys/v1/entry/HPD:Template"
            id_field = "InstanceId"
            

            query = self._build_query(
                criteria=search_criteria,
                use_like=use_like,
                like_field="Template Name"
            )
            
            return self._paginated_search(
                    endpoint=endpoint,
                    base_query=query,
                    id_field=id_field,
                    fields=fields,
                )
        except HelixClientError:
            raise

        except Exception as err:
            raise HelixClientError(f"{ERROR_PREFIX}: Erro ao buscar Templates no Helix: {err}") from err

    def search_user(
        self,
        search_criteria: Optional[Dict[str, Any]] = None,
        fields: Optional[List[str]] = None,
        like_field: str = "Internet E-mail",
        id_field: str = "Remedy Login ID",
        use_like: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Search for users in Helix (CTM:People).

        Queries user records in the Helix people catalog, supporting
        dynamic filters and configurable partial matching.

        Search rules:
            - Uses the `CTM:People` form.
            - Defaults to `Remedy Login ID` as the record identifier.
            - Defaults to `Internet E-mail` as the LIKE search field.
            - Supports optional search criteria.
            - Uses automatic pagination through `_paginated_search`.

        Args:
            search_criteria: Optional dictionary of search filters.
            fields: List of fields to return from the API.
            like_field: Field used for partial matching.
            id_field: Field used to identify unique user records.
            use_like: If True, applies LIKE matching to `like_field`.

        Returns:
            List[Dict[str, Any]]: Matching user records.

        Raises:
            HelixClientError: If query construction, the API request, or pagination fails.
        """
        try:
            endpoint = "/api/arsys/v1/entry/CTM:People"

            query = self._build_query(
                criteria=search_criteria,
                use_like=use_like,
                like_field=like_field
            )
            
            return self._paginated_search(
                    endpoint=endpoint,
                    base_query=query,
                    id_field=id_field,
                    fields=fields,
                )
        except HelixClientError:
            raise

        except Exception as err:
            raise HelixClientError(f"{ERROR_PREFIX}: Erro ao buscar usuários no Helix: {err}") from err
  
    def search_support_groups(
        self,
        search_criteria: Optional[Dict[str, Any]] = None,
        fields: Optional[List[str]] = None,
        use_like: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Search for support groups in Helix (CTM:Support Group).

        Supports dynamic filters and optional partial matching by group name.

        Search rules:
            - Uses the `CTM:Support Group` form.
            - Uses `Support Group ID` as the record identifier.
            - Supports optional search criteria.
            - Supports LIKE matching on the `Support Group Name` field.
            - Uses automatic pagination through `_paginated_search`.

        Args:
            search_criteria: Optional dictionary of search filters.
            fields: List of fields to return from the API.
            use_like: If True, applies partial matching to `Support Group Name`.

        Returns:
            List[Dict[str, Any]]: Matching support groups.

        Raises:
            HelixClientError: If query construction, the API request, or pagination fails.
        """
        try:
            endpoint:str = "/api/arsys/v1/entry/CTM:Support Group"
            id_field = "Support Group ID"

            query = self._build_query(
                criteria=search_criteria,
                use_like=use_like,
                like_field="Support Group Name"
            )
            
            return self._paginated_search(
                    endpoint=endpoint,
                    base_query=query,
                    id_field=id_field,
                    fields=fields,
                )
        except Exception as err:
            raise HelixClientError(f"{ERROR_PREFIX}: Erro ao buscar Support Groups no Helix: {err}") from err

    def validate_user_in_group(
        self,
        person_id: str,
        support_group_id: str
    )->bool:
        """
        Check whether a user has an active association with a support group.

        Queries the `CTM:Support Group Association` form to verify whether
        an enabled association exists between a person and a support group.

        Validation rules:
            - Both parameters are required and must be non-empty strings.
            - Only associations with `Status = "Enabled"` are considered.
            - Returns True if at least one active association exists.
            - Returns False otherwise.

        Args:
            person_id: Helix Person ID of the user.
            support_group_id: Helix ID of the support group.

        Returns:
            bool: True if the user has an active association with the group;
                otherwise, False.

        Raises:
            HelixClientError: If either parameter is invalid or query construction,
                API communication, pagination, or validation fails.
        """
        try:
            if not person_id or not isinstance(person_id, str):
                raise HelixClientError(f"{ERROR_PREFIX}: login_id inválido em validação de usuário no grupo")
            
            if not support_group_id or not isinstance(support_group_id, str):
                raise HelixClientError(f"{ERROR_PREFIX}: Group Name inválido em validação de usuário no grupo")
            
            endpoint:str = "/api/arsys/v1/entry/CTM:Support Group Association"
            id_field = "Support Group Association ID"
            
            criteria = {
                "Person ID": person_id,
                "Support Group ID": support_group_id
            }

            query = self._build_query(criteria=criteria)

            results = self._paginated_search(
                endpoint=endpoint,
                base_query=query,
                id_field=id_field,
                fields=[
                    "Person ID",
                    "Support Group ID",
                    "Status"
                ]
            )

            if not results:
                return False

            for r in results:
                if r.get("Status") == "Enabled":
                    return True

            return False


        except HelixClientError:
            raise

        except Exception as err:
            raise HelixClientError(f"{ERROR_PREFIX}: Erro ao validar usuário '{person_id}' no grupo '{support_group_id}': {err}") from err

    def associate_ci_to_incident(
        self,
        incident_number: str,
        ci_name: str,
        ci_recon_id: str
    ) -> bool:
        """
        Associate a configuration item (CI) with an incident in Helix.

        Creates a record in `HPD:Associations`, linking a CI from
        `AST:ComputerSystem` to an incident from `HPD:Help Desk`.

        Association rules:
            - All parameters are required and must be non-empty strings.
            - The association is created with `Status = "Enabled"`.
            - The default association type is `"Related to"`.
            - Returns True if the API request succeeds.

        Args:
            incident_number: Helix incident number.
            ci_name: Name of the configuration item.
            ci_recon_id: Reconciliation ID of the configuration item.

        Returns:
            bool: True if the association was created successfully.

        Raises:
            HelixClientError: If input validation fails or the API request
                returns an error.
        """
        
        try:
            if not incident_number or not isinstance(incident_number, str):
                raise HelixClientError(f"{ERROR_PREFIX}: incident_number inválido na associação CI → incidente")
            
            if not ci_name or not isinstance(ci_name, str):
                raise HelixClientError(f"{ERROR_PREFIX}: ci_name inválido na associação CI → incidente")
            
            if not ci_recon_id or not isinstance(ci_recon_id, str):
                raise HelixClientError(f"{ERROR_PREFIX}: ci_recon_id inválido na associação CI → incidente")
            
            endpoint = "/api/arsys/v1/entry/HPD:Associations"
            association_payload = {
                "values": {
                    # --- Lado 01: O Item de Configuração ---
                    "Request ID01": ci_recon_id,
                    "Form Name01": "AST:ComputerSystem", # Nome do formulário do IC na interface de associações
                    "Request Type01": "Configuration Item",
                    "Request Description01": ci_name,
                    # --- Lado 02: O Incidente ---
                    "Request ID02": incident_number,
                    "Form Name02": "HPD:Help Desk",
                    # --- Metadados da Associação ---
                    "Association Type01": "Related to",
                    "Status": "Enabled"
                }
            }

        
            response = self._request_helix('POST', endpoint, json_data=association_payload)
            if response:
                return True

        except HelixClientError:
            raise

        except Exception as err:
            raise HelixClientError(
                f"{ERROR_PREFIX}: Falha ao criar associação CI '{ci_name}' "
                f"para incidente '{incident_number}': {err}"
            ) from err
    
    def create_incident(
        self,
        incident_data: Dict[str, Any],
        fields: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Create an incident in BMC Helix ITSM using the
        `HPD:IncidentInterface_Create` form.

        This operation creates a new incident and returns the requested
        fields after the record has been persisted.

        Args:
            incident_data: Incident payload following the Helix API schema.
            fields: Fields to return after creation.
                If None, only `Incident Number` is returned.
                If ["*"], all available fields are requested.

        Returns:
            Dict[str, Any]: Incident data returned by Helix.

        Raises:
            HelixClientError: If the payload is invalid, the API request fails,
                or the API returns an invalid or unexpected response.
        """

        try:
            
            if not isinstance(incident_data, dict) or not incident_data:
                raise HelixClientError(f"{ERROR_PREFIX}: incident_data inválido para criação de incidente")
            
            fields_str = ",".join(fields) if fields else "Incident Number"

            endpoint = (
                f"/api/arsys/v1/entry/HPD:IncidentInterface_Create"
                f"?fields=values({fields_str})"
            )

            response = self._request_helix(
                "POST",
                endpoint,
                json_data=incident_data
            )

            if not response:
                raise HelixClientError(f"{ERROR_PREFIX}: resposta vazia ao criar incidente")
            
            try:
                payload = response.json()
            except Exception as err:
                raise HelixClientError(f"{ERROR_PREFIX}: resposta inválida (JSON parsing error): {err}") from err

            if "values" not in payload:
                raise HelixClientError(f"{ERROR_PREFIX}: resposta sem campo 'values' ao criar incidente")

            return payload["values"]

        except HelixClientError:
            raise

        except Exception as err:
            raise HelixClientError(f"{ERROR_PREFIX}: falha ao criar incidente no Helix: {err}") from err

    def create_incident_worklog(
        self,
        worklog_data: Dict[str, Any],
        fields: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Create a worklog associated with an incident in Helix (HPD:WorkLog).

        A worklog represents a note or activity record linked to an incident.

        Args:
            worklog_data: Worklog payload following the Helix API schema.
                Must contain a `values` dictionary.
            fields: Fields to return after creation.
                - None: Returns only `Work Log ID`.
                - ["*"]: Returns all available fields.
                - A list of field names: Returns the specified fields.

        Returns:
            Dict[str, Any]: Worklog data returned by Helix after creation.

        Raises:
            HelixClientError: If the payload is invalid, the request fails,
                or the API returns an invalid response.
        """

        try:
            if (
                not isinstance(worklog_data, dict)
                or "values" not in worklog_data
                or not isinstance(worklog_data["values"], dict)
            ):
                raise HelixClientError(f"{ERROR_PREFIX}: worklog_data inválido (esperado dict com 'values')")

            if fields == ["*"]:
                fields_param = "*"
            elif fields:
                fields_param = f"values({','.join(fields)})"
            else:
                fields_param = "values(Work Log ID)"

            endpoint = (
                f"/api/arsys/v1/entry/HPD:WorkLog"
                f"?fields={fields_param}"
            )

            response = self._request_helix(
                "POST",
                endpoint,
                json_data=worklog_data
            )

            if not response:
                raise HelixClientError(f"{ERROR_PREFIX}: resposta vazia ao criar WorkLog")

            try:
                payload = response.json()
            except Exception as err:
                raise HelixClientError(f"{ERROR_PREFIX}: erro ao parsear resposta JSON: {err}") from err

            if "values" not in payload:
                raise HelixClientError(f"{ERROR_PREFIX}: resposta inválida da API (sem 'values')")

            return payload["values"]

        except HelixClientError:
            raise

        except Exception as err:
            raise HelixClientError(f"{ERROR_PREFIX}: falha ao criar WorkLog: {err}") from err

  