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
    def create_simple_product(
        self, title: str, track_quantity: bool = False
    ) -> Dict[str, Any]:
        """
        TODO:
        - Implement productCreate for a product without options.
        - Return response JSON.
        """
        mutation = """
        mutation CreateSimpleProduct($input: ProductInput!) {
          productCreate(input: $input) {
            product {
              id
              title
              variants(first: 1) {
                edges {
                  node {
                    id
                    inventoryItem { id tracked }
                  }
                }
              }
            }
            userErrors { field message }
          }
        }
        """

        # SỬA Ở ĐÂY: Đảm bảo cấu trúc variants đúng chuẩn ProductInput
        variables = {"input": {"title": title}}
        return self.client.execute(query=mutation, variables=variables)

    def create_product_with_variants(
        self, title: str, initial_variant_qty=100
    ) -> Dict[str, Any]:
        """
        TODO:
        - Implement productCreate for a product with options (Size, Color) and variants.
        - Return response JSON.
        """

        mutation = """
        mutation CreateVariantProduct($input: ProductInput!) {
          productCreate(input: $input) {
            product {
              id
              title
              variants(first: 10) {
                edges {
                  node {
                    id
                    title
                    inventoryItem { id }
                  }
                }
              }
            }
            userErrors {
              field
              message
            }
          }
        }
        """

        # Bước 2: Định nghĩa variables bao gồm cả variants và inventoryQuantities
        variables = {
            "input": {
                "title": title,
                "status": "ACTIVE",
                "productOptions": [
                    {"name": "Color", "values": [{"name": "Red"}, {"name": "Blue"}]},
                    {"name": "Size", "values": [{"name": "Small"}, {"name": "Large"}]},
                ],
            }
        }
        return self.client.execute(query=mutation, variables=variables)

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
        mutation = """
        mutation productDelete($input: ProductDeleteInput!) {
          productDelete(input: $input) {
            deletedProductId
            userErrors {
              field
              message
            }
          }
        }
        """
        variables = {"input": {"id": product_gid}}
        return self.client.execute(query=mutation, variables=variables)

    def create_product_with_variants_v2(
        self, title: str, initial_variant_qty: int = 100
    ) -> Dict[str, Any]:
        """
        Tạo product với options (Color, Size) và đầy đủ 4 variants bằng bulk create.
        - Sử dụng productCreate + productOptions để tạo product & options.
        - Sau đó productVariantsBulkCreate với strategy REMOVE_STANDALONE_VARIANT để:
          - Xóa default variant thừa.
          - Tạo 4 variants + set inventory ngay.
        - Return response của bulk create (có danh sách variants đã tạo).
        """
        # Bước 1: Lấy location ID (cần cho inventoryQuantities)
        loc_query = """
          query {
            locations(first: 1) {
              edges {
                node { id }
              }
            }
          }
      """
        loc_res = self.client.execute(query=loc_query)

        try:
            location_id = loc_res["data"]["locations"]["edges"][0]["node"]["id"]
        except (KeyError, IndexError):
            raise ValueError("Không tìm thấy location active nào trong store.")

        # Bước 2: Tạo product + options (tạo default variant tạm thời)
        create_mutation = """
      mutation productCreate($input: ProductInput!) {
        productCreate(input: $input) {
          product {
            id
            title
          }
          userErrors {
            field
            message
          }
        }
      }
      """

        create_variables = {
            "input": {
                "title": title,
                "status": "ACTIVE",
                "productOptions": [
                    {"name": "Color", "values": [{"name": "Red"}, {"name": "Blue"}]},
                    {"name": "Size", "values": [{"name": "Small"}, {"name": "Large"}]},
                ],
            }
        }

        create_res = self.client.execute(
            query=create_mutation, variables=create_variables
        )

        if create_res.get("data", {}).get("productCreate", {}).get("userErrors"):
            return create_res  # Trả lỗi nếu create product fail

        product_id = create_res["data"]["productCreate"]["product"]["id"]

        # Bước 3: Bulk create 4 variants + xóa default variant cũ
        bulk_mutation = """
      mutation productVariantsBulkCreate(
        $productId: ID!
        $variants: [ProductVariantsBulkInput!]!
        $strategy: ProductVariantsBulkCreateStrategy
      ) {
        productVariantsBulkCreate(
          productId: $productId
          variants: $variants
          strategy: $strategy
        ) {
          product {
            id
            title
            options(first: 10) {
              name
              values
            }
          }
          productVariants {
            id
            title
            price
            sku
            inventoryItem {
              id
            }
            inventoryQuantity
          }
          userErrors {
            field
            message
          }
        }
      }
      """

        bulk_variables = {
            "productId": product_id,
            "strategy": "REMOVE_STANDALONE_VARIANT",  # Xóa default variant thừa
            "variants": [
                # Red / Small
                {
                    "optionValues": [
                        {"optionName": "Color", "name": "Red"},
                        {"optionName": "Size", "name": "Small"},
                    ],
                    "price": "29.99",
                    "inventoryQuantities": [
                        {
                            "locationId": location_id,
                            "availableQuantity": initial_variant_qty,
                        }
                    ],
                },
                # Red / Large
                {
                    "optionValues": [
                        {"optionName": "Color", "name": "Red"},
                        {"optionName": "Size", "name": "Large"},
                    ],
                    "price": "34.99",
                    "inventoryQuantities": [
                        {
                            "locationId": location_id,
                            "availableQuantity": initial_variant_qty,
                        }
                    ],
                },
                # Blue / Small
                {
                    "optionValues": [
                        {"optionName": "Color", "name": "Blue"},
                        {"optionName": "Size", "name": "Small"},
                    ],
                    "price": "29.99",
                    "inventoryQuantities": [
                        {
                            "locationId": location_id,
                            "availableQuantity": initial_variant_qty,
                        }
                    ],
                },
                # Blue / Large
                {
                    "optionValues": [
                        {"optionName": "Color", "name": "Blue"},
                        {"optionName": "Size", "name": "Large"},
                    ],
                    "price": "34.99",
                    "inventoryQuantities": [
                        {
                            "locationId": location_id,
                            "availableQuantity": initial_variant_qty,
                        }
                    ],
                },
            ],
        }

        bulk_res = self.client.execute(query=bulk_mutation, variables=bulk_variables)

        # Trả về response của bulk create (chứa variants đầy đủ)
        return bulk_res

    def update_product_tags(self, product_gid: str, tags: list):
        """Cập nhật danh sách tags cho sản phẩm."""
        mutation = """
        mutation productUpdate($input: ProductInput!) {
          productUpdate(input: $input) {
            product {
              id
              tags
            }
            userErrors {
              field
              message
            }
          }
        }
        """
        variables = {
            "input": {
                "id": product_gid,
                "tags": tags,
            }
        }
        return self.client.execute(query=mutation, variables=variables)

    def update_product_title(self, product_gid: str, new_title: str):
        """Cập nhật tên mới cho sản phẩm."""
        mutation = """
        mutation productUpdate($input: ProductInput!) {
          productUpdate(input: $input) {
            product {
              id
              title
            }
            userErrors {
              field
              message
            }
          }
        }
        """
        variables = {"input": {"id": product_gid, "title": new_title}}
        return self.client.execute(query=mutation, variables=variables)

    # ----------------------
    # Collections
    # ----------------------
    def create_custom_collection(self, title: str) -> Dict[str, Any]:
        """
        TODO:
        - Implement collection creation for your API version.
        """

        # 1. Định nghĩa Mutation
        mutation = """
        mutation CreateCustomCollection($input: CollectionInput!) {
          collectionCreate(input: $input) {
            collection {
              id
              title
            }
            userErrors {
              field
              message
            }
          }
        }
        """

        # 2. Truyền tham số (Chỉ cần title)
        variables = {"input": {"title": title}}

        # 3. Thực thi
        response = self.client.execute(query=mutation, variables=variables)

        # 4. Bóc tách kết quả
        data = response.get("data", {}).get("collectionCreate", {})

        # Kiểm tra lỗi từ phía người dùng (ví dụ: thiếu quyền, tên không hợp lệ)
        if data.get("userErrors"):
            print(f"Lỗi khi tạo Custom Collection: {data['userErrors']}")
            return None

        return data.get("collection", {}).get("id")

    def create_smart_collection(self, title: str) -> Dict[str, Any]:
        """
        TODO:
        - Implement smart collection creation (if supported by your API version).
        """

        mutation = """
        mutation CreateSmartCollection($input: CollectionInput!) {
          collectionCreate(input: $input) {
            collection {
              id
              title
            }
            userErrors {
              field
              message
            }
          }
        }
        """

        # Mẹo: Giả sử title là "dev-training Smart Collection",
        # ta cắt lấy chữ đầu tiên "dev-training" để làm điều kiện Rule
        prefix = title.split()[0]

        variables = {
            "input": {
                "title": title,
                "ruleSet": {
                    "appliedDisjunctively": False,
                    "rules": [
                        {
                            "column": "TITLE",
                            "relation": "STARTS_WITH",
                            "condition": prefix,
                        }
                    ],
                },
            }
        }
        # Trả về nguyên cục JSON
        return self.client.execute(query=mutation, variables=variables)

    def delete_collection(self, collection_gid: str) -> Dict[str, Any]:
        """
        TODO:
        - Implement collection deletion for your API version.
        """
        mutation = """
        mutation collectionDelete($input: CollectionDeleteInput!) {
          collectionDelete(input: $input) {
            deletedCollectionId
            userErrors {
              field
              message
            }
          }
        }
        """
        variables = {"input": {"id": collection_gid}}
        return self.client.execute(query=mutation, variables=variables)

    def list_locations(self) -> Dict[str, Any]:
        """
        Truy vấn danh sách các Locations (kho hàng) của Store.
        Cần thiết để lấy Location ID phục vụ việc cập nhật tồn kho.
        """
        query = """
        query GetLocations {
          locations(first: 1) {
            edges {
              node {
                id
                name
                isActive
              }
            }
          }
        }
        """
        return self.client.execute(query=query)

    def add_products_to_collection(self, collection_gid: str, product_gids: list):
        mutation = """
        mutation collectionAddProducts($id: ID!, $productIds: [ID!]!) {
          collectionAddProducts(id: $id, productIds: $productIds) {
            collection {
              id
              title
              productsCount {
                count
              }
            }
            userErrors {
              field
              message
            }
          }
        }
        """
        variables = {"id": collection_gid, "productIds": product_gids}
        return self.client.execute(query=mutation, variables=variables)

    # ----------------------
    # iventory
    # ----------------------
    def set_inventory_tracked(
        self, inventory_item_gid: str, tracked: bool = True
    ) -> Dict[str, Any]:
        """
        Bật/tắt tracking inventory cho một InventoryItem.
        """
        mutation = """
        mutation InventoryItemUpdate($id: ID!, $input: InventoryItemInput!) {
        inventoryItemUpdate(id: $id, input: $input) {
              inventoryItem {
                id
                tracked
              }
              userErrors {
                field
                message
              }
            }
          }
        """

        variables = {"id": inventory_item_gid, "input": {"tracked": tracked}}

        response = self.client.execute(query=mutation, variables=variables)

        # Kiểm tra lỗi
        user_errors = (
            response.get("data", {})
            .get("inventoryItemUpdate", {})
            .get("userErrors", [])
        )
        if user_errors:
            raise ValueError(f"Lỗi set tracked: {user_errors}")

        return response

    def set_on_hand_quantity(
        self, inventory_item_gid: str, location_gid: str, quantity: int = 200
    ) -> Dict[str, Any]:
        """
        Set absolute on-hand quantity = 200 tại location cụ thể.
        Sử dụng inventorySetQuantities (hỗ trợ absolute set, có compare-and-swap để an toàn concurrent).
        """
        mutation = """
        mutation inventorySetQuantities($input: InventorySetQuantitiesInput!) {
          inventorySetQuantities(input: $input) {
            inventoryAdjustmentGroup {
              id
            }
            userErrors {
              field
              message
              code
            }
          }
        }
        """

        variables = {
            "input": {
                "name": "on_hand",
                "reason": "correction",
                "ignoreCompareQuantity": True,
                "quantities": [
                    {
                        "inventoryItemId": inventory_item_gid,
                        "locationId": location_gid,
                        "quantity": quantity,
                    }
                ],
            }
        }

        response = self.client.execute(query=mutation, variables=variables)

        user_errors = (
            response.get("data", {})
            .get("inventorySetQuantities", {})
            .get("userErrors", [])
        )
        if user_errors:
            raise ValueError(f"Lỗi set on-hand quantity: {user_errors}")

        return response
