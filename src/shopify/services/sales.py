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

    def delete_customer(self, customer_gid: str) -> Dict[str, Any]:
        """
        Xóa một khách hàng dựa trên Customer GID.
        """
        mutation = """
        mutation customerDelete($input: CustomerDeleteInput!) {
          customerDelete(input: $input) {
            deletedCustomerId
            userErrors {
              field
              message
            }
          }
        }
        """
        variables = {"input": {"id": customer_gid}}
        return self.client.execute(query=mutation, variables=variables)

    def create_order(
        self, customer_gid: str, variant_gid: str, quantity: int
    ) -> Dict[str, Any]:
        """
        TODO:
        - Implement OrderCreate mutation.
        """
        mutation = """
        mutation CreateDraftOrder($input: DraftOrderInput!) {
          draftOrderCreate(input: $input) {
            draftOrder {
              id
              name
              status
              totalPrice
            }
            userErrors {
              field
              message
            }
          }
        }
        """

        # Cấu trúc DraftOrderInput yêu cầu lineItems là một mảng (món hàng)
        variables = {
            "input": {
                "customerId": customer_gid,
                "lineItems": [{"variantId": variant_gid, "quantity": quantity}],
            }
        }

        return self.client.execute(query=mutation, variables=variables)

    def delete_order(self, draft_order_gid: str) -> Dict[str, Any]:
        """
        TODO:
        - Implement OrderDelete mutation.
        """
        mutation = """
        mutation draftOrderDelete($input: DraftOrderDeleteInput!) {
          draftOrderDelete(input: $input) {
            deletedId
            userErrors {
              field
              message
            }
          }
        }
        """
        variables = {"input": {"id": draft_order_gid}}
        return self.client.execute(query=mutation, variables=variables)
