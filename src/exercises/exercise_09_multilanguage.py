"""
Exercise 09 — Shopify multi-language

Goal:
- Learn Shopify Translations API concepts
- Add translations for:
  - Product title
  - Collection title
- Query translations to verify
"""

from src.app.config import load_settings
from src.shopify.client import ShopifyGraphQLClient


def main() -> None:
    settings = load_settings()
    _client = ShopifyGraphQLClient(settings)

    # TODO:
    # - Implement translationsRegister mutation (or equivalent)
    # - Query translatable resources
    # - Verify translations were applied

    # --- CẤU HÌNH ---
    target_locale = "vi"  # Ngôn ngữ mục tiêu (Đảm bảo đã add trong Admin)
    product_gid = "gid://shopify/Product/8863763038365"
    collection_gid = "gid://shopify/Collection/439543136573"

    # --- 1. LẤY DIGEST (MÃ XÁC THỰC NỘI DUNG GỐC) ---
    print(f"🔍 Step 1: Fetching translatable resources for Product...")

    get_digest_query = """
    query getTranslatableResource($id: ID!) {
      translatableResource(resourceId: $id) {
        resourceId
        translatableContent {
          key
          value
          digest
        }
      }
    }
    """

    # Lấy digest cho Product
    p_res = _client.execute(query=get_digest_query, variables={"id": product_gid})
    p_content = (
        p_res.get("data", {})
        .get("translatableResource", {})
        .get("translatableContent", [])
    )

    # Tìm digest của trường 'title'
    p_title_digest = next(
        (item["digest"] for item in p_content if item["key"] == "title"), None
    )

    if not p_title_digest:
        print("❌ Không tìm thấy nội dung để dịch. Kiểm tra lại ID sản phẩm.")
        return

    # --- 2. REGISTER TRANSLATIONS (MUTATION) ---
    print(f"✍️ Step 2: Registering translation for Product Title ({target_locale})...")

    register_mutation = """
    mutation translationsRegister($resourceId: ID!, $translations: [TranslationInput!]!) {
      translationsRegister(resourceId: $resourceId, translations: $translations) {
        translations {
          key
          value
          locale
        }
        userErrors { field message }
      }
    }
    """

    translation_input = [
        {
            "locale": target_locale,
            "key": "title",
            "value": "Áo thun cao cấp ",  # Nội dung đã dịch
            "translatableContentDigest": p_title_digest,
        }
    ]

    reg_res = _client.execute(
        query=register_mutation,
        variables={"resourceId": product_gid, "translations": translation_input},
    )

    reg_errors = (
        reg_res.get("data", {}).get("translationsRegister", {}).get("userErrors", [])
    )
    if reg_errors:
        print(f"❌ Lỗi khi dịch: {reg_errors[0]['message']}")
        return

    print(f"✅ Đã dịch thành công sang {target_locale}!")

    # --- 3. QUERY BACK TO VERIFY ---
    print("🧪 Step 3: Verifying translation...")

    verify_query = """
    query verifyTranslation($id: ID!, $locale: String!) {
      product(id: $id) {
        title
        translations(locale: $locale) {
          value
        }
      }
    }
    """

    verify_res = _client.execute(
        query=verify_query, variables={"id": product_gid, "locale": target_locale}
    )
    product_data = verify_res.get("data", {}).get("product", {})

    print(f"   🔹 Bản gốc: {product_data.get('title')}")
    print(
        f"   🔹 Bản dịch ({target_locale}): {product_data.get('translation', {}).get('value')}"
    )

    print("✨ Exercise 09 hoàn tất!")


if __name__ == "__main__":
    main()
