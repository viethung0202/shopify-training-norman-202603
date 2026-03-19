from __future__ import annotations
from typing import Any, Dict

from src.shopify.client import ShopifyGraphQLClient


class SalesService:
    """
    Sales service includes Customers and Orders/Draft Orders.
    Draft orders are recommended for training because direct order creation can be restricted.
    """

    def __init__(self, client: ShopifyGraphQLClient) -> None:
        self.client = client

    def create_customer(
        self, email: str, first_name: str, last_name: str
    ) -> Dict[str, Any]:
        """
        TODO:
        - Implement customerCreate mutation.
        """

        mutation = """
        mutation CreateCustomer($input: CustomerInput!) {
          customerCreate(input: $input) {
            customer {
              id
            }
            userErrors {
              field
              message
            }
          }
        }
        """

        variables = {
            "input": {"email": email, "firstName": first_name, "lastName": last_name}
        }

        return self.client.execute(query=mutation, variables=variables)

    def create_order(
        self, customer_gid: str, variant_gid: str, quantity: int
    ) -> Dict[str, Any]:
        """
        TODO:
        - Implement OrderCreate mutation.
        """
        raise NotImplementedError

    def delete_order(self, draft_order_gid: str) -> Dict[str, Any]:
        """
        TODO:
        - Implement OrderDelete mutation.
        """
        raise NotImplementedError
