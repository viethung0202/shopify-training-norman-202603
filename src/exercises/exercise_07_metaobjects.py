"""
Exercise 07 — Metaobjects

Goal:
- Create a metaobject definition (if needed)
- Create metaobject entries
- Query metaobjects
- Store created IDs into SQLite registry using raw SQL
"""

from src.app.config import load_settings
from src.shopify.client import ShopifyGraphQLClient
from src.storage import repo


def main() -> None:
    settings = load_settings()
    _client = ShopifyGraphQLClient(settings)

    # TODO:
    # - Implement metaobjectDefinitionCreate (if needed)
    # - Implement metaobjectCreate
    # - Implement metaobject query
    # - Save IDs to SQLite registry

    # --- CONFIGURATION ---
    OBJECT_TYPE = "designer_info"

    # --- 1. IMPLEMENT metaobjectDefinitionCreate (IF NEEDED) ---
    print(f"🏗️ Step 1: Checking/Creating Metaobject Definition: {OBJECT_TYPE}")

    def_mutation = """
    mutation CreateMetaobjectDefinition($definition: MetaobjectDefinitionCreateInput!) {
      metaobjectDefinitionCreate(definition: $definition) {
        metaobjectDefinition { id type }
        userErrors { field message code }
      }
    }
    """

    def_input = {
        "name": "Designer Info",
        "type": OBJECT_TYPE,
        "capabilities": {"publishable": {"enabled": True}},
        "fieldDefinitions": [
            {"name": "Full Name", "key": "name", "type": "single_line_text_field"},
            {"name": "Bio", "key": "bio", "type": "multi_line_text_field"},
        ],
    }

    def_res = _client.execute(query=def_mutation, variables={"definition": def_input})
    def_errors = (
        def_res.get("data", {})
        .get("metaobjectDefinitionCreate", {})
        .get("userErrors", [])
    )

    # Kiểm tra xem lỗi có phải do đã tồn tại (TAKEN) hay không
    is_already_exists = any(err["code"] == "TAKEN" for err in def_errors)

    if def_errors and not is_already_exists:
        print(f"❌ Lỗi Definition: {def_errors[0]['message']}")
        return
    elif is_already_exists:
        print(f"ℹ️ Definition '{OBJECT_TYPE}' đã tồn tại, bỏ qua bước tạo.")
    else:
        print(f"✅ Tạo Definition thành công!")

    # --- 2. IMPLEMENT metaobjectCreate ---
    print(f"📝 Step 2: Creating Metaobject Entry for {OBJECT_TYPE}...")

    create_mutation = """
    mutation CreateMetaobject($metaobject: MetaobjectCreateInput!) {
      metaobjectCreate(metaobject: $metaobject) {
        metaobject { id handle }
        userErrors { field message }
      }
    }
    """

    entry_input = {
        "type": OBJECT_TYPE,
        "fields": [
            {"key": "name", "value": "Viet Hung Backend"},
            {"key": "bio", "value": " Shopify API và Python Automation."},
        ],
    }

    create_res = _client.execute(
        query=create_mutation, variables={"metaobject": entry_input}
    )
    create_data = create_res.get("data", {}).get("metaobjectCreate", {})

    if create_data.get("userErrors"):
        print(f"❌ Lỗi Create Entry: {create_data['userErrors'][0]['message']}")
        return

    new_entry_id = create_data.get("metaobject", {}).get("id")
    print(f"✅ Tạo Entry thành công! ID: {new_entry_id}")

    # --- 3. IMPLEMENT metaobject query ---
    print(f"🔍 Step 3: Querying Metaobjects of type {OBJECT_TYPE}...")

    query_str = """
    query GetMetaobjects($type: String!) {
      metaobjects(type: $type, first: 10) {
        edges {
          node {
            id
            handle
            type
            updatedAt
          }
        }
      }
    }
    """

    query_res = _client.execute(query=query_str, variables={"type": OBJECT_TYPE})
    edges = query_res.get("data", {}).get("metaobjects", {}).get("edges", [])

    # --- 4. SAVE IDs TO SQLite REGISTRY ---
    print("💾 Step 4: Saving Metaobject IDs to SQLite...")

    if not edges:
        print("⚠️ Không tìm thấy Metaobject nào để lưu.")
    else:
        for edge in edges:
            node = edge["node"]
            m_id = node["id"]
            m_handle = node["handle"]

            # Sử dụng repo để lưu vào bảng training_entities
            repo.register_entity(
                entity_type="METAOBJECT",
                shopify_gid=m_id,
                note=f"Type: {OBJECT_TYPE}, Handle: {m_handle}",
            )
            print(f" 🔹 Đã lưu: {m_handle} (ID: {m_id})")

    print("Exercise 07 hoàn tất!")


if __name__ == "__main__":
    main()
