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
    print(f"Đang tìm kiếm các sản phẩm với tiền tố: '{training_prefix}'...")

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

            # Tạo một "dòng" dữ liệu phẳng cho mỗi variant
            row = {
                "product_id": product_id,
                "product_title": product_title,
                "variant_id": variant.get("id"),
                "variant_title": variant.get("title"),
                "price": variant.get("price"),
            }
            rows.append(row)

    # - Print a short summary
    print(f"Tóm tắt: Đã lấy được {len(raw_products)} sản phẩm.")
    print(f"Bóc tách thành công {len(rows)} dòng dữ liệu (variants).")

    # In thử 1 dòng đầu tiên để kiểm tra cấu trúc
    if rows:
        print("Ví dụ dòng đầu tiên:", rows[0])
    else:
        print("Không có dữ liệu nào được trả về. Hãy kiểm tra lại Step 1!")

    # Step 3: Save queried products to SQLite
    # TODO:
    # - repo.create_tables()
    # - repo.insert_products(rows)
    # - verify with repo.list_products()
    raise NotImplementedError


if __name__ == "__main__":
    main()
