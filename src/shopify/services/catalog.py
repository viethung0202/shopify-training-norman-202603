from __future__ import annotations
from typing import Any, Dict, Optional

from src.shopify.client import ShopifyGraphQLClient


class CatalogService:
    """
    Catalog service includes Products and Collections to keep training code easy to navigate.
    Inventory is intentionally excluded from this template.
    """

    def __init__(self, client: ShopifyGraphQLClient) -> None:
        self.client = client

    # ----------------------
    # Products
    # ----------------------
    def create_simple_product(self, title: str) -> Dict[str, Any]:
        """
        TODO:
        - Implement productCreate for a product without options.
        - Return response JSON.
        """
        raise NotImplementedError

    def create_product_with_variants(self, title: str) -> Dict[str, Any]:
        """
        TODO:
        - Implement productCreate for a product with options (Size, Color) and variants.
        - Return response JSON.
        """
        raise NotImplementedError

    def query_products(
        self, first: int = 10, query: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        TODO:
        - Implement products query (by first, optional search query).
        - Return response JSON.
        """
        # 1. Định nghĩa câu GraphQL, nhận tham số động $first và $query
        graphql_query = """
        query GetProducts($first: Int!, $query: String) {
          products(first: $first, query: $query) {
            edges {
              node {
                id
                title
                variants(first: 10) {
                  edges {
                    node {
                      id
                      title
                      price
                    }
                  }
                }
              }
            }
          }
        }
        """

        # 2. Tạo dictionary variables để truyền vào GraphQL
        variables = {"first": first, "query": query}

        # 3. Gửi request qua client (Giả định hàm gửi tên là execute)
        # Tùy code của bạn mà hàm này có thể là self.client.execute() hoặc self.client.post()
        response = self.client.execute(query=graphql_query, variables=variables)

        # 4. Trả về đúng cục JSON (Dict[str, Any]) theo yêu cầu của Type Hint
        return response

    def delete_product(self, product_gid: str) -> Dict[str, Any]:
        """
        TODO:
        - Implement productDelete mutation.
        """
        raise NotImplementedError

    # ----------------------
    # Collections
    # ----------------------
    def create_custom_collection(self, title: str) -> Dict[str, Any]:
        """
        TODO:
        - Implement collection creation for your API version.
        """
        raise NotImplementedError

    def create_smart_collection(self, title: str) -> Dict[str, Any]:
        """
        TODO:
        - Implement smart collection creation (if supported by your API version).
        """
        raise NotImplementedError

    def delete_collection(self, collection_gid: str) -> Dict[str, Any]:
        """
        TODO:
        - Implement collection deletion for your API version.
        """
        raise NotImplementedError
