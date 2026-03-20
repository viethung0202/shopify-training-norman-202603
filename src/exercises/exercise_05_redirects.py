"""
Exercise 05 — Redirects

Goal:
- Create URL redirects in the Shopify store
- Query redirects and verify results
- Store created redirect IDs into SQLite registry using raw SQL
"""

from src.app.config import load_settings
from src.shopify.client import ShopifyGraphQLClient
from src.storage import repo


def main() -> None:
    settings = load_settings()
    _client = ShopifyGraphQLClient(settings)

    # TODO:
    # - Implement redirectCreate mutation (or equivalent)
    # - Implement redirects query
    # - Save redirect IDs into SQLite registry
    # --- CẤU HÌNH DỮ LIỆU TEST ---
    old_path = "/san-pham-cu-20251"
    new_target = "/collections/all1"

    # --- 1. TẠO REDIRECT (MUTATION) ---
    print(f"📡 Đang tạo Redirect: {old_path} -> {new_target}...")

    create_mutation = """
    mutation urlRedirectCreate($urlRedirect: UrlRedirectInput!) {
      urlRedirectCreate(urlRedirect: $urlRedirect) {
        urlRedirect { id path target }
        userErrors { field message }
      }
    }
    """
    create_variables = {"urlRedirect": {"path": old_path, "target": new_target}}

    response = _client.execute(query=create_mutation, variables=create_variables)

    # Bóc tách dữ liệu an toàn
    create_result = response.get("data", {}).get("urlRedirectCreate", {})
    errors = create_result.get("userErrors", [])
    redirect_node = create_result.get("urlRedirect")

    if errors:
        print(f"❌ Lỗi Shopify: {errors[0]['message']}")
        return

    redirect_id = redirect_node.get("id")
    print(f"✅ Tạo thành công! GID: {redirect_id}")

    # --- 2. KIỂM TRA LẠI (QUERY) ---
    print("🔍 Danh sách 10 Redirects mới nhất trên Shopify:")

    list_query = """
    query {
      urlRedirects(first: 10, reverse: true) {
        edges {
          node {
            id
            path
            target
          }
        }
      }
    }
    """
    query_response = _client.execute(query=list_query)
    edges = query_response.get("data", {}).get("urlRedirects", {}).get("edges", [])

    for edge in edges:
        node = edge.get("node", {})
        print(f"📍 ID: {node.get('id')}")
        print(f"   Path: {node.get('path')}  -->  Target: {node.get('target')}")
        print("-" * 30)

    # --- 3. LƯU VÀO REGISTRY (SQLITE) ---
    print(" Đang lưu vào SQLite registry...")
    repo.register_entity(
        entity_type="REDIRECT",
        shopify_gid=redirect_id,
        note=f"Test redirect: {old_path} -> {new_target}",
    )
    print(" Hoàn thành Exercise 05!")


if __name__ == "__main__":
    main()
