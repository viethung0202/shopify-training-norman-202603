"""
Exercise 00 — Onboarding + Products + SQL

Goal:
1) Understand the repo structure and how the GraphQL client works.
2) Create two test products in Shopify:
   - One simple product (no options)
   - One product with variants (Size, Color)
3) Implement a product query to fetch products (including variants).
4) Store queried products into SQLite using raw SQL.

Rules:
- Prefix created titles with TRAINING_PREFIX
- Do not hardcode Shopify IDs
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

    # Step 1: Create two test products (Manual)
    # Step 2: Query products
    # TODO:
    # - Implement catalog.query_products(...)
    # - Extract the product fields into a list of dict rows
    # - Print a short summary

    # Lấy prefix từ biến môi trường
    training_prefix = os.getenv("TRAINING_PREFIX", "dev-training")
    print(f"Finding products with prefix: '{training_prefix}'...")

    # - Implement catalog.query_products(...)
    # Gọi hàm từ catalog service (bạn sẽ phải viết logic gọi API trong hàm này sau)
    response_json = catalog.query_products(query=f"title:{training_prefix}*")

    # Bóc tách để lấy danh sách các sản phẩm (nodes) từ cục JSON
    edges = response_json.get("data", {}).get("products", {}).get("edges", [])
    raw_products = [edge.get("node", {}) for edge in edges]

    # - Extract the product fields into a list of dict rows
    rows = []

    # Giả định raw_products là một list các dictionary chứa thông tin product (node)
    for product in raw_products:
        product_id = product.get("id")
        product_title = product.get("title")

        # Bóc tách variants (Vì một product có thể có nhiều variant)
        variants_edges = product.get("variants", {}).get("edges", [])

        for edge in variants_edges:
            variant = edge.get("node", {})

            # row each variant
            row = {
                "product_id": product_id,
                "product_title": product_title,
                "variant_id": variant.get("id"),
                "variant_title": variant.get("title"),
                "price": variant.get("price"),
            }
            rows.append(row)

    # - Print a short summary
    print(f"Summary: Fetched {len(raw_products)} products.")
    print(f"Successfully extracted {len(rows)} data rows (variants).")

    # Print the first row to verify the structure
    if rows:
        print("First row example:", rows[0])
    else:
        print("No data returned. Please double-check Step 1!")

    # Step 3: Save queried products to SQLite
    # TODO:
    # - repo.create_tables()
    # - repo.insert_products(rows)
    # - verify with repo.list_products()

    print("\n--- Start store data in SQLite ---")

    # Create tables (repo.create_tables)
    repo.create_tables()
    print("Successfully created tables.")

    # 2. Insert data (upsert_product và upsert_variant)
    for row in rows:
        # upsert Product
        repo.upsert_product(
            product_gid=row["product_id"],
            title=row["product_title"],
            handle=None,
            status=None,
        )

        # upsert Variant
        repo.upsert_variant(
            variant_gid=row["variant_id"],
            product_gid=row["product_id"],
            title=row["variant_title"],
            sku=None,
            price=row["price"],
            inventory_item_gid=None,
        )

    print(f"Successfully inserted {len(rows)} variant records into the database.")

    # - verify with repo.list_products()
    print("\n" + "=" * 50)
    print("VERIFICATION: Fetching data from SQLite")
    print("=" * 50)

    # Gọi hàm repo để lấy dữ liệu đã JOIN
    final_data = repo.list_products_with_variants()

    if not final_data:
        print("Verification failed: No data found in database.")
    else:
        print(f"Success! Found {len(final_data)} records in database.\n")

        # In tiêu đề cột cho đẹp
        print(f"{'Product Title':<30} | {'Variant GID':<20}")
        print("-" * 60)

        for record in final_data:
            # record ở đây là sqlite3.Row, ta truy cập như dictionary
            p_title = record["product_title"]
            v_gid = record["variant_gid"].split("/")[-1]  # Cắt bớt GID cho ngắn gọn

            print(f"{p_title:<30} | {v_gid:<20}")

    print("\n" + "=" * 50)


if __name__ == "__main__":
    main()
