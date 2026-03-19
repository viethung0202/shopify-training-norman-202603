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
    
    # 1. Tạo khách hàng
    email = "buyer-06@example.com"
    first_name = "Jon"
    last_name = "Doe2"

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
       # return  # Dừng chương trình nếu lỗi tạo khách hàng

    if customer_id and isinstance(customer_id, str):
        print(f"✅ Success! Customer ID: {customer_id}")
        # Lưu vào SQLite
        repo.register_entity("Customer", customer_id, "Training Buyer")

    # 2. Đọc variant_id từ DB hoặc query Shopify
    target_product_id = "gid://shopify/Product/8863709364381"
    variant_gid = repo.get_variant_id_by_product_id(target_product_id)

    if not variant_gid:
        print(f"❌ THẤT BẠI: Không tìm thấy bất kỳ Variant nào thuộc Product ID {target_product_id} trong Database.")
        print(f"💡 Gợi ý: Hãy kiểm tra bảng 'training_variants' xem bạn đã chạy Exercise 01 để lưu dữ liệu chưa.")
        return
    
    print(f"✅ THÀNH CÔNG: Đã tìm thấy Variant GID: {variant_gid}")
    
    # 3. Tạo Draft Order
    quantity = 2
    print(f"Calling API to create draft order for Customer ID {customer_id} with Variant ID {variant_gid} and quantity {quantity}...")
    order_res = sales.create_order(
        customer_gid=customer_id, variant_gid=variant_gid, quantity=quantity
    )
    try:
        draft_order_data = order_res["data"]["draftOrderCreate"]["draftOrder"]
        if draft_order_data and draft_order_data.get("id"):
            draft_order_id = draft_order_data["id"]
            print(f"✅ Success! Draft Order ID: {draft_order_id}")
            # repo.register_entity("DraftOrder", draft_order_id, "Training Draft Order")
        else:
            print(f"❌ Lỗi tạo Draft Order. Dữ liệu trả về: {order_res}")
    except (KeyError, TypeError):
        print(f"❌ Lỗi bóc tách Draft Order ID. Dữ liệu trả về: {order_res}")
    
    # 4 Register IDs into DB registry
    repo.register_entity("DraftOrder", draft_order_id, "Training Draft Order")
    
if __name__ == "__main__":
    main()
