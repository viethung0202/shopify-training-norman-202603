from __future__ import annotations
from typing import Any, Dict, Optional

import requests

from src.app.config import Settings


class ShopifyGraphQLClient:
    """
    Shopify Admin GraphQL client (skeleton).

    Trainee tasks:
    - Implement execute()
    - Handle HTTP errors
    - Handle GraphQL top-level 'errors'
    - Return parsed JSON
    """

    def __init__(self, settings: Settings, timeout_seconds: int = 30) -> None:
        self.settings = settings
        self.timeout_seconds = timeout_seconds
        self.endpoint = f"https://{settings.shop_domain}/admin/api/{settings.api_version}/graphql.json"

    def _headers(self) -> Dict[str, str]:
        return {
            "Content-Type": "application/json",
            "X-Shopify-Access-Token": self.settings.access_token,
        }

    def execute(
        self, query: str, variables: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute a GraphQL operation.

        TODO:
        - POST to self.endpoint with JSON payload {"query": query, "variables": variables}
        - Raise on non-2xx response codes
        - Parse JSON
        - If response contains top-level "errors", raise with details
        - Return parsed JSON
        """
        # 1. Tạo JSON payload
        payload = {"query": query}
        if variables:
            payload["variables"] = variables

        # 2. POST to self.endpoint
        # GỌI HÀM self._headers() để lấy token và truyền thêm timeout
        response = requests.post(
            self.endpoint,
            json=payload,
            headers=self._headers(),
            timeout=self.timeout_seconds,
        )

        # 3. Raise on non-2xx response codes
        response.raise_for_status()

        # 4. Parse JSON
        response_json = response.json()

        # 5. If response contains top-level "errors", raise with details
        if "errors" in response_json:
            raise ValueError(f"Lỗi từ GraphQL Shopify: {response_json['errors']}")

        # 6. Return parsed JSON
        return response_json
