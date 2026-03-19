"""
Exercise 01 — Collections

Goal:
- Create a custom collection
- Create a smart collection (if supported by API/store)
- Query collections (optional)
- Save created entity IDs into SQLite registry using raw SQL
"""

import os
from src.app.config import load_settings
from src.shopify.client import ShopifyGraphQLClient
from src.shopify.services.catalog import CatalogService
from src.storage import repo


def main() -> None:
    settings = load_settings()
    client = ShopifyGraphQLClient(settings)
    catalog = CatalogService(client)
    training_prefix = os.getenv("TRAINING_PREFIX", "dev-training")

    # Step 1: Create Collections (Custom and Smart)
    # TODO:
    # - Create collections
    # - Register IDs into registry table

    print("Đang kiểm tra và khởi tạo Database...")
    repo.create_tables()
    # --- 1. Create Custom Collection ---
    custom_title = f"{training_prefix} Custom Collection"
    print(f"Calling API to create: {custom_title}...")

    custom_id = catalog.create_custom_collection(title=custom_title)

    if custom_id:
        print(f"Success! Custom Collection ID: {custom_id}")
        # Ghi vào SQLite
        repo.register_entity(
            entity_type="Collection", shopify_gid=custom_id, note="Manual Collection"
        )
    else:
        print("Error creating Custom Collection (Check catalog service).")
    # --- 2. Create Smart Collection ---
    smart_title = f"{training_prefix} Smart Collection"
    print(f"Calling API to create: {smart_title}...")

    smart_id = catalog.create_smart_collection(title=smart_title)

    smart_response = catalog.create_smart_collection(title=smart_title)
    smart_data = smart_response.get("data", {}).get("collectionCreate", {})

    # Kiểm tra xem Shopify có báo lỗi logic (userErrors) không
    user_errors = smart_data.get("userErrors")
    if user_errors:
        print(f"Shopify từ chối tạo Smart Collection. Lỗi chi tiết: {user_errors}")
    else:
        # Nếu không có lỗi, bóc ID ra
        smart_collection = smart_data.get("collection")
        if smart_collection and smart_collection.get("id"):
            smart_id = smart_collection.get("id")
            print(f"Success! Smart Collection ID: {smart_id}")
            repo.register_entity("Collection", smart_id, "Automated Collection")
        else:
            print(f"Có lỗi lạ xảy ra, không tìm thấy ID: {smart_response}")

    # Step 2: Create Simple Product and Product with Variants (Assign to collections)
    # TODO:
    # - Use catalog.create_simple_product(...)
    # - Use catalog.create_product_with_variants(...)
    # - Register created entity IDs into DB registry (repo.register_entity)

    print("\n--- Step 2: Creating Products & Assigning to Collections ---")
    # --- 1. Create Simple Product ---
    simple_title = f"{training_prefix} Simple Product"
    print(f"Calling API to create: {simple_title}...")

    # Truyền custom_id vào dạng list (vì Shopify thường cho phép 1 sản phẩm nằm ở nhiều collection)
    simple_response = catalog.create_simple_product(title=simple_title)

    # 2. Kiểm tra lỗi nghiệp vụ từ Shopify trước
    data = simple_response.get("data", {}).get("productCreate", {})
    product_node = data.get("product")
    errors = data.get("userErrors", [])

    if errors:
        print(f"❌ Shopify bận/lỗi: {errors}")
        return # Dừng lại vì không có ID để làm bước sau

    if product_node:
        simple_id = product_node.get("id")
        print(f"✅ Success! Simple Product ID: {simple_id}")
        
        # Đừng quên lấy cả inventory_item_id để dùng cho Step 3 nhé!
        # Vì bạn cần nó để bật 'tracked=True' sau này
        try:
            inv_item_id = product_node["variants"]["edges"][0]["node"]["inventoryItem"]["id"]
            print(f"📦 Inventory Item ID: {inv_item_id}")
        except (KeyError, IndexError):
            print("⚠️ Không lấy được Inventory Item ID")

        # Lưu vào registry
        repo.register_entity("Product", simple_id, "Simple Product Ex 03")
    else:
        print(f"❌ Không tạo được sản phẩm. Response: {simple_response}")

    # --- 2. Create Product with Variants ---
    variant_title = f"{training_prefix} Variant Product"
    print(f"Calling API to create: {variant_title}...")

    # Gán sản phẩm này vào Smart Collection
    variant_response = catalog.create_product_with_variants(title=variant_title)

    # Bóc tách ID an toàn
    variant_id = None
    try:
        variant_id = variant_response["data"]["productCreate"]["product"]["id"]
    except (KeyError, TypeError):
        print(f"Error extracting Variant Product ID. Response: {variant_response}")

    if variant_id and isinstance(variant_id, str):
        print(f"Success! Variant Product ID: {variant_id}")
        # Lưu vào registry để cleanup
        repo.register_entity(
            entity_type="Product",
            shopify_gid=variant_id,
            note="Variant Product in Smart Collection",
        )

    print("\nEXERCISE 01 COMPLETED SUCCESSFULLY!")


if __name__ == "__main__":
    main()
