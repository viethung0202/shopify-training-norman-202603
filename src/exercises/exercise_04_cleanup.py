"""
Exercise 04 — Cleanup

Goal:
- Delete all Shopify entities recorded in SQLite registry
- Delete corresponding rows from the registry
- Optionally clear local training tables

Recommended deletion order:
1) orders
2) products
3) collections
4) customers (if deletion is permitted)

Note:
- Shopify permissions may restrict certain deletions.
- Handle partial failures and log userErrors.
"""

from src.app.config import load_settings
from src.shopify.client import ShopifyGraphQLClient
from src.shopify.services.catalog import CatalogService
from src.shopify.services.sales import SalesService
from src.storage import repo


def main() -> None:
    settings = load_settings()
    client = ShopifyGraphQLClient(settings)
    catalog = CatalogService(client)
    sales = SalesService(client)

    # TODO:
    # - repo.list_entities()
    # - For each entity type, call the correct delete mutation
    # - repo.delete_entity_record(gid) after successful deletion

    # 1. Lấy danh sách tất cả entities đã lưu trong registry
    entities = repo.list_entities()
    if not entities:
        print("No entities found in registry. Nothing to delete.")
        return
    print(f"Found {len(entities)} entities in registry. Starting cleanup...")
    # Định nghĩa thứ tự ưu tiên xóa
    priority_order = ["Order", "Product", "Collection", "Customer"]

    # Sắp xếp entities theo thứ tự ưu tiên
    entities.sort(
        key=lambda x: (
            priority_order.index(x["entity_type"])
            if x["entity_type"] in priority_order
            else 99
        )
    )

    for entity in entities:
        gid = entity["shopify_gid"]
        etype = entity["entity_type"]
        success = False

        print(f"⏳ Attempting to delete {etype}: {gid}...")

        # 2. Gọi đúng hàm xóa dựa trên Type
        try:
            if etype == "Order":
                # Đơn hàng thường chỉ xóa được khi đã hủy hoặc là test order
                response = sales.delete_order(gid)
                success = not response.get("errors") and not response.get(
                    "data", {}
                ).get("orderDelete", {}).get("userErrors")

            elif etype == "Product":
                response = catalog.delete_product(gid)
                success = (
                    not response.get("data", {})
                    .get("productDelete", {})
                    .get("userErrors")
                )

            elif etype == "Collection":
                response = catalog.delete_collection(gid)
                success = (
                    not response.get("data", {})
                    .get("collectionDelete", {})
                    .get("userErrors")
                )
            elif etype == "Customer":
                response = sales.delete_customer(gid)
                success = (
                    not response.get("data", {})
                    .get("customerDelete", {})
                    .get("userErrors")
                )
            # 3. Nếu xóa trên Shopify THÀNH CÔNG -> Xóa dòng đó trong Registry SQLite
            if success:
                repo.delete_entity_record(gid)
                print(f"✅ Successfully deleted {etype} from Shopify and Registry.")
            else:
                # Nếu Shopify báo lỗi (ví dụ Product đang nằm trong Order không xóa được)
                # thì record vẫn nằm trong DB để bạn biết mà xử lý tay.
                print(
                    f"⚠️ Failed to delete {etype} on Shopify. Keeping record in DB for debugging."
                )

        except Exception as e:
            print(f"❌ System error during cleanup of {gid}: {e}")


if __name__ == "__main__":
    main()
