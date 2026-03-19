"""
Exercise 02 — Customers + Draft Orders

Goal:
- Create a customer
- Create a draft order for that customer and one of the created variants
- Save created entity IDs into SQLite registry using raw SQL

Note:
- Draft orders are recommended for training.
"""

from src.app.config import load_settings
from src.shopify.client import ShopifyGraphQLClient
from src.shopify.services.sales import SalesService
from src.storage import repo


def main() -> None:
    settings = load_settings()
    client = ShopifyGraphQLClient(settings)
    sales = SalesService(client)

    # TODO:
    # - Create customer
    # - Read a variant_id from DB (from products table) or query Shopify
    # - Create draft order
    # - Register IDs into DB registry
    email = "buyer-05@example.com"
    first_name = "Jon"
    last_name = "Doe1"

    print(f"Calling API to create customer: {first_name} {last_name} ({email})...")

    customer_res = sales.create_customer(
        email=email, first_name=first_name, last_name=last_name
    )

    customer_id = None
    try:
        # Bóc tách ID từ JSON trả về
        customer_id = customer_res["data"]["customerCreate"]["customer"]["id"]
    except (KeyError, TypeError):
        print(f"❌ Lỗi bóc tách Customer ID. Dữ liệu trả về: {customer_res}")
        return  # Dừng chương trình nếu lỗi tạo khách hàng

    if customer_id and isinstance(customer_id, str):
        print(f"✅ Success! Customer ID: {customer_id}")
        # Lưu vào SQLite
        repo.register_entity("Customer", customer_id, "Training Buyer")


if __name__ == "__main__":
    main()
