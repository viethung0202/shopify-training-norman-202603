"""
Exercise 06 — Metafields

Goal:
- Set metafields on products (and optionally customers/orders)
- Query metafields back
- Store created metafield identifiers into SQLite registry using raw SQL (if applicable)
"""

from src.app.config import load_settings
from src.shopify.client import ShopifyGraphQLClient
from src.storage import repo


def main() -> None:
    settings = load_settings()
    _client = ShopifyGraphQLClient(settings)

    # TODO:
    # - Implement metafieldsSet mutation
    # - Query metafields for a product
    # - Save any required identifiers into SQLite
    
    product_gid = "gid://shopify/Product/8863763038365" 

    # --- 1. SET METAFIELD (MUTATION) ---
    print(f"🚀 Step 1: Setting Metafield for Product: {product_gid}")
    
    set_mutation = """
    mutation metafieldsSet($metafields: [MetafieldsSetInput!]!) {
      metafieldsSet(metafields: $metafields) {
        metafields {
          id
          namespace
          key
          value
          type
        }
        userErrors {
          field
          message
        }
      }
    }
    """
    
    # Định nghĩa thông tin Metafield
    metafields_input = [
        {
            "ownerId": product_gid,
            "namespace": "manual_info1",
            "key": "material",
            "value": "Coton 100%",
            "type": "single_line_text_field"
        }
    ]

    response = _client.execute(query=set_mutation, variables={"metafields": metafields_input})
    
    set_data = response.get("data", {}).get("metafieldsSet", {})
    errors = set_data.get("userErrors", [])

    if errors:
        print(f"❌ Lỗi khi set Metafield: {errors[0]['message']}")
        return

    # Lấy ID của Metafield (Shopify trả về một mảng)
    metafield_id = set_data.get("metafields", [{}])[0].get("id")
    print(f"✅ Set thành công! Metafield ID: {metafield_id}")

    # --- 2. QUERY METAFIELDS (VERIFY) ---
    print("🔍 Step 2: Querying metafields back from Product...")
    
    query_str = """
    query getProductMetafields($id: ID!) {
      product(id: $id) {
        metafields(first: 10) {
          edges {
            node {
              id
              namespace
              key
              value
            }
          }
        }
      }
    }
    """
    
    query_res = _client.execute(query=query_str, variables={"id": product_gid})
    edges = query_res.get("data", {}).get("product", {}).get("metafields", {}).get("edges", [])

    print(f"📋 Các Metafields hiện có của sản phẩm {product_gid}:")
    for edge in edges:
        m = edge["node"]
        print(f" 🔹 {m['namespace']}.{m['key']} = {m['value']} (ID: {m['id']})")

        repo.register_entity(
        entity_type="METAFIELD",
        shopify_gid=m['id'],
        note=f"Material info for product {product_gid}"
    )
    
    print("✨ Exercise 06 hoàn tất!")


if __name__ == "__main__":
    main()
