"""
Exercise 08 — Gift cards

Goal:
- Create a gift card
- Query gift cards
- Disable or adjust gift card (if supported by API/store permissions)
- Store created IDs into SQLite registry using raw SQL
"""

from src.app.config import load_settings
from src.shopify.client import ShopifyGraphQLClient
from src.storage import repo


def main() -> None:
    settings = load_settings()
    _client = ShopifyGraphQLClient(settings)

    # TODO:
    # - Implement gift card creation mutation (if available)
    # - Query gift cards
    # - Save IDs to SQLite registry
    # --- 1. CREATE GIFT CARD (MUTATION) ---
    print("🎁 Step 1: Creating a Gift Card...")

    create_mutation = """
    mutation giftCardCreate($input: GiftCardCreateInput!) {
      giftCardCreate(input: $input) {
        giftCard {
          id
          lastCharacters
          note
        }
        userErrors { field message }
      }
    }
    """

    # Tạo một Gift Card trị giá 50.00 USD
    create_input = {
        "initialValue": "50.00",
        "note": "Training Exercise 08 - Gift Card for Viet Hung",
    }

    response = _client.execute(query=create_mutation, variables={"input": create_input})
    create_data = response.get("data", {}).get("giftCardCreate", {})

    if create_data.get("userErrors"):
        print(f"❌ Lỗi Create: {create_data['userErrors'][0]['message']}")
        # Nếu lỗi do store không hỗ trợ Gift Card, chúng ta dừng tại đây
        return

    gift_card = create_data.get("giftCard", {})
    gift_card_id = gift_card.get("id")
    print(f"✅ Tạo thành công! ID: {gift_card_id} | Code: {gift_card.get('code')}")

    # --- 2. DISABLE GIFT CARD (ADJUSTMENT) ---
    print(f"🔒 Step 2: Disabling the Gift Card: {gift_card_id}")

    disable_mutation = """
    mutation giftCardDeactivate($id: ID!) {
    giftCardDeactivate(id: $id) {
        giftCard {
        id
        deactivatedAt
        }
        userErrors {
        message
        field
        code
        }
    }
    }
    """

    _client.execute(query=disable_mutation, variables={"id": gift_card_id})
    print("🚫 Gift Card đã được vô hiệu hóa.")

    # --- 3. QUERY GIFT CARDS (VERIFY) ---
    print("🔍 Step 3: Querying Gift Cards...")

    query_str = """
    query {
      giftCards(first: 5) {
        edges {
          node {
            id
            lastCharacters
            enabled
            initialValue {
              amount
              currencyCode
            }
          }
        }
      }
    }
    """

    query_res = _client.execute(query=query_str)
    edges = query_res.get("data", {}).get("giftCards", {}).get("edges", [])

    # --- 4. SAVE TO SQLITE ---
    print("💾 Step 4: Saving Gift Card IDs to SQLite...")

    for edge in edges:
        node = edge["node"]
        g_id = node["id"]
        g_code = node["lastCharacters"]  # Shopify thường ẩn code, chỉ hiện 4 số cuối

        repo.register_entity(
            entity_type="GIFT_CARD",
            shopify_gid=g_id,
            note=f"Code: {g_code}, Status: {'Enabled' if node['enabled'] else 'Disabled'}",
        )
        print(f" 🔹 Đã lưu: {g_code} (ID: {g_id})")

    print("✨ Exercise 08 hoàn tất!")


if __name__ == "__main__":
    main()
