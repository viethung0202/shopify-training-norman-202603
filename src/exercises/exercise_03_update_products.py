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

from src.app.config import load_settings
from src.shopify.client import ShopifyGraphQLClient
from src.shopify.services.catalog import CatalogService
from src.storage import repo


def main() -> None:
    settings = load_settings()
    client = ShopifyGraphQLClient(settings)
    catalog = CatalogService(client)

    # Step 0: Ensure tables exist
    # TODO: repo.create_tables()
    repo.create_tables()

    # Step 1: Get and store one location (needed for inventory quantity updates)
    # TODO:
    # - Call catalog.list_locations()
    # - Pick one location_gid
    # - repo.upsert_location(location_gid, name)
    locations_response = catalog.list_locations()
    locations_edges = locations_response.get("data", {}).get("locations", {}).get("edges", [])   
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
    raise NotImplementedError

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
    raise NotImplementedError

    # Step 4: Update tags and titles for both products
    # TODO:
    # - catalog.update_product_tags(product_gid, tags=[...])
    # - catalog.update_product_title(product_gid, new_title=...)
    raise NotImplementedError

    # Step 5: Create a new collection and add the two products to it
    # TODO:
    # - collection = catalog.create_custom_collection(...)
    # - catalog.add_products_to_collection(collection_gid, [product_gid_1, product_gid_2])
    # - repo.register_entity("collection", collection_gid, note="created in exercise_03")
    raise NotImplementedError


if __name__ == "__main__":
    main()
