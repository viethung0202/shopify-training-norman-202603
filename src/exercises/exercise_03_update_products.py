"""
Exercise 03 — Update Products data

Goal:
1) Create two products:
   - One simple product (inventory not tracked initially)
   - One product with variants (variant quantity starts at 100)
2) Save created products/variants and required inventory identifiers into SQLite (raw SQL).
3) Update both products:
   - Set quantity to 200 (for both)
   - Update tags
   - Create a new collection and add products to it
   - Update product titles

Rules:
- Prefix created titles with TRAINING_PREFIX
- Do not hardcode Shopify IDs; store and read them from SQLite
- SQL must be written by the trainee in storage/repo.py
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

    # Step 0: Ensure tables exist
    # TODO: repo.create_tables()
    repo.create_tables()

    # Step 1: Get and store one location (needed for inventory quantity updates)
    # TODO:
    # - Call catalog.list_locations()
    # - Pick one location_gid
    # - repo.upsert_location(location_gid, name)
    locations_response = catalog.list_locations()
    locations_edges = (
        locations_response.get("data", {}).get("locations", {}).get("edges", [])
    )
    for edge in locations_edges:
        location_node = edge.get("node", {})
        location_gid = location_node.get("id")
        location_name = location_node.get("name")

        if location_gid and location_name:
            repo.upsert_location(location_gid, location_name)
            print(f"✅ Đã lưu Location: {location_name} (GID: {location_gid}) vào DB.")
        else:
            print(f"⚠️ Bỏ qua một Location do thiếu thông tin: {location_node}")

    # Step 2: Create products with required inventory conditions
    # Requirements:
    # - Simple product: inventory not tracked initially
    # - Variant product: at least one variant starts at quantity=100
    #
    # TODO:
    # - Create simple product via catalog.create_simple_product(title, track_quantity=False)
    # - Create variant product via catalog.create_product_with_variants(title, initial_variant_qty=100)
    # - Extract product_gid, variant_gid(s), inventory_item_gid(s)
    # - Store:
    #   - repo.upsert_product(...)
    #   - repo.upsert_variant(...)
    # - Register created entities for cleanup:
    #   - repo.register_entity("product", product_gid, note=...)
    #   - repo.register_entity("collection", collection_gid, ...) when created

    # 1. Create simple product
    simple_title = f"{training_prefix} Simple Product ex3"
    print(f"Calling API to create: {simple_title}...")

    # Truyền custom_id vào dạng list (vì Shopify thường cho phép 1 sản phẩm nằm ở nhiều collection)
    simple_response = catalog.create_simple_product(title=simple_title)

    #  Kiểm tra lỗi nghiệp vụ từ Shopify trước
    data = simple_response.get("data", {}).get("productCreate", {})
    product_node = data.get("product")
    errors = data.get("userErrors", [])

    if errors:
        print(f"❌ Shopify bận/lỗi: {errors}")
        return  # Dừng lại vì không có ID để làm bước sau

    if product_node:
        simple_id = product_node.get("id")
        print(f"✅ Success! Simple Product ID: {simple_id}")

        # Đừng quên lấy cả inventory_item_id để dùng cho Step 3 nhé!
        # Vì bạn cần nó để bật 'tracked=True' sau này
        try:
            inv_item_id = product_node["variants"]["edges"][0]["node"]["inventoryItem"][
                "id"
            ]
            print(f"📦 Inventory Item ID: {inv_item_id}")
        except (KeyError, IndexError):
            print("⚠️ Không lấy được Inventory Item ID")

        # Lưu vào registry
        # repo.register_entity("Product", simple_id, "Custom product")
        repo.upsert_product(
            product_gid=simple_id,
            title=simple_title,
            handle=None,
            status=None,
        )

        repo.register_entity("Product", simple_id, "Custom product")
    else:
        print(f"❌ Không tạo được sản phẩm. Response: {simple_response}")

    # 2. Create product with variants
    product_variant_title = f"{training_prefix} Variant Product ex3"
    variant_response = catalog.create_product_with_variants_v2(
        title=product_variant_title, initial_variant_qty=100
    )

    # Extract các GID từ response của productVariantsBulkCreate

    try:
        # Kiểm tra lỗi trước (userErrors từ bulk create)
        bulk_data = variant_response.get("data", {}).get(
            "productVariantsBulkCreate", {}
        )
        user_errors = bulk_data.get("userErrors", [])

        if user_errors:
            print("Lỗi từ productVariantsBulkCreate:")
            for err in user_errors:
                print(f"  - {err.get('field')}: {err.get('message')}")
            raise ValueError("Bulk create variants thất bại")

        # 2.1. Product GID (từ product.id)
        product_gid = bulk_data.get("product", {}).get("id")
        if not product_gid:
            raise ValueError("Không tìm thấy product.id trong response")

        print(f"Product GID: {product_gid}")

        # 2.2. Variant GIDs (list tất cả variants mới tạo, thường 4 cái)
        product_variants = bulk_data.get("productVariants", [])
        variant_gids = []
        inventory_item_gids = []

        if not product_variants:
            raise ValueError(
                "Không tìm thấy productVariants trong response (bulk create không trả variants)"
            )

        for variant in product_variants:
            variant_gid = variant.get("id")
            if variant_gid:
                variant_gids.append(variant_gid)

            # Inventory Item GID (nếu có trong response)
            inv_item = variant.get("inventoryItem")
            if inv_item and inv_item.get("id"):
                inventory_item_gids.append(inv_item["id"])

        print(f"Variant GIDs ({len(variant_gids)} cái): {variant_gids}")
        print(
            f"Inventory Item GIDs ({len(inventory_item_gids)} cái): {inventory_item_gids}"
        )
        repo.upsert_product(
            product_gid=product_gid,
            title=product_variant_title,
            handle=None,
            status=None,
        )

        repo.register_entity("Product", product_gid, "Variant product")
        # Optional: In thêm thông tin để debug (ví dụ title variant)
        for variant in product_variants:
            print(
                f" - Variant: {variant.get('title')} | Price: {variant.get('price')} | Qty: {variant.get('inventoryQuantity')}"
            )
            # 2.3. Lưu vào DB

            repo.upsert_variant(
                variant_gid=variant.get("id"),
                product_gid=product_gid,
                title=variant.get("title"),
                sku=None,
                price=variant.get("price"),
                inventory_item_gid=variant.get("inventoryItem", {}).get("id"),
            )

    except (KeyError, TypeError, ValueError) as e:
        print("Lỗi khi extract GIDs:")
        print(e)
        print("\nResponse đầy đủ để debug:")
        import json

        print(json.dumps(variant_response, indent=2, ensure_ascii=False))

        # Step 3: Update both products
        # - Set quantity to 200 for both products
        #   For the simple product:
        #     - First enable tracking (tracked=True) on its inventory_item_gid
        #     - Then set on-hand quantity to 200
        #   For the variant product:
        #     - Set on-hand quantity to 200 for the target variant inventory_item_gid
        #
        # TODO:
        # - Read location_gid from DB (repo.get_any_location_gid())

        # - Read product+variant+inventory_item IDs from DB (repo.list_products_with_variants())
        # - Call:
        #   - catalog.set_inventory_tracked(inventory_item_gid, True) when needed
        #   - catalog.set_on_hand_quantity(inventory_item_gid, location_gid, 200)

    loc_gid = repo.get_any_location_gid()
    print(f"📍 Sử dụng Location GID: {loc_gid} cho bước update quantity")

    # set quantity for simple product
    inventory_tracked = catalog.set_inventory_tracked(inv_item_id, True)
    if inventory_tracked:
        print(f"✅ Đã bật tracking cho Inventory custom Item {inv_item_id}")
        catalog.set_on_hand_quantity(inv_item_id, loc_gid, 200)
        print(f"✅ Đã set quantity=200 cho Inventory custom Item {inv_item_id}")
    else:
        print(f"❌ Không bật được tracking cho Inventory custom Item {inv_item_id}")

    for variant in product_variants:
        inv_item_gid = variant.get("inventoryItem", {}).get("id")
        if inv_item_gid:
            catalog.set_on_hand_quantity(inv_item_gid, loc_gid, 200)
            print(f"✅ Đã set quantity=200 cho Variant Inventory Item {inv_item_gid}")
        else:
            print(
                f"⚠️ Không tìm thấy inventory_item_gid cho variant {variant.get('id')}"
            )

    # Step 4: Update tags and titles for both products
    # TODO:
    # - catalog.update_product_tags(product_gid, tags=[...])
    # - catalog.update_product_title(product_gid, new_title=...)

    catalog.update_product_tags(simple_id, tags=[f"{training_prefix}-updated"])
    catalog.update_product_title(
        simple_id, new_title=f"{training_prefix} - Updated Simple Product"
    )
    print(f"✅ Đã cập nhật tags và title cho Simple Product {simple_id}")

    catalog.update_product_tags(product_gid, tags=[f"{training_prefix}-updated"])
    catalog.update_product_title(
        product_gid, new_title=f"{training_prefix} - Updated Variant Product"
    )
    print(f"✅ Đã cập nhật tags và title cho Variant Product {product_gid}")
    # Step 5: Create a new collection and add the two products to it
    # TODO:
    # - collection = catalog.create_custom_collection(...)
    # - catalog.add_products_to_collection(collection_gid, [product_gid_1, product_gid_2])
    # - repo.register_entity("collection", collection_gid, note="created in exercise_03")

    collection_title = f"{training_prefix} Collection ex3"
    collection_gid = catalog.create_custom_collection(title=collection_title)

    if collection_gid:
        print(f"✅ Đã tạo Collection: {collection_title} (GID: {collection_gid})")
        catalog.add_products_to_collection(collection_gid, [simple_id, product_gid])
        print(f"✅ Đã thêm products vào collection {collection_title}")

        repo.register_entity("Collection", collection_gid, "Created in exercise_03")
    else:
        print(f"❌ Không tạo được collection. Response: {collection_gid}")


if __name__ == "__main__":
    main()
