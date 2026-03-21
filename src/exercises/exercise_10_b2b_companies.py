"""
Exercise 10 — Shopify B2B companies

Goal:
- Create a company
- Add a company contact
- Query company data
- Store created IDs into SQLite registry using raw SQL
"""

from src.app.config import load_settings
from src.shopify.client import ShopifyGraphQLClient
from src.storage import repo


def main() -> None:
    settings = load_settings()
    _client = ShopifyGraphQLClient(settings)

    # TODO:
    # - Implement companyCreate mutation (if available)
    # - Implement locationCreate mutation (if available)
    # - Implement companyContactCreate or equivalent
    # - Query companies
    # - Save IDs to SQLite registry

    # --- 1. CONFIGURATION (DỮ LIỆU MẪU) ---
    print("🏗️ Step 0: Preparing B2B Sample Data...")

    # Tạo tên công ty duy nhất để tránh trùng lặp khi chạy lại
    company_name = f" Global Trading - 01"

    # --- 2. CREATE COMPANY (MUTATION) ---
    print(f" Step 1: Creating B2B Company: {company_name}")

    company_create_mutation = """
    mutation companyCreate($input: CompanyCreateInput!) {
      companyCreate(input: $input) {
        company {
          id
          name
        }
        userErrors { field message }
      }
    }
    """

    # Input cơ bản để tạo Company
    company_input = {
        "company": {"name": company_name, "note": "B2B Training Exercise 10"}
    }

    c_res = _client.execute(
        query=company_create_mutation, variables={"input": company_input}
    )
    c_data = c_res.get("data", {}).get("companyCreate", {})

    if c_data.get("userErrors"):
        print(f"❌ Lỗi Create Company: {c_data['userErrors'][0]['message']}")
        return

    company_id = c_data.get("company", {}).get("id")
    print(f"✅ Tạo Company thành công! ID: {company_id}")

    # --- 3. CREATE COMPANY LOCATION (MUTATION) ---
    print(f"📍 Step 2: Creating Main Location for {company_id}")

    location_create_mutation = """
    mutation companyLocationCreate($companyId: ID!, $input: CompanyLocationInput!) {
    companyLocationCreate(companyId: $companyId, input: $input) {
        companyLocation {
        id
        name
        }
        userErrors {
        field
        message
        }
    }
    }
    """

    # Input bắt buộc phải có địa chỉ đầy đủ (Shopify B2B yêu cầu rất chặt)
    location_input = {
        "name": "Main Warehouse",
        "shippingAddress": {
            "address1": "1 Trieu Quoc Dat",
            "city": "Hanoi",
            "countryCode": "VN",
            "zip": "100000",
        },
    }

    l_res = _client.execute(
        query=location_create_mutation,
        variables={"companyId": company_id, "input": location_input},
    )

    l_data = l_res.get("data", {}).get("companyLocationCreate", {})
    if l_data.get("userErrors"):
        print(f"❌ Lỗi Create Location: {l_data['userErrors'][0]['message']}")
        # B2B không thể đặt hàng nếu thiếu Location, nên chúng ta dừng tại đây
        return

    location_id = l_data.get("companyLocation", {}).get("id")
    print(f"✅ Tạo Location thành công! ID: {location_id}")

    # --- 4. CREATE COMPANY CONTACT (MUTATION) ---
    print(f"👤 Step 3: Assigning Contact to Company")

    contact_create_mutation = """
    mutation companyContactCreate($companyId: ID!, $input: CompanyContactInput!) {
      companyContactCreate(companyId: $companyId, input: $input) {
        companyContact {
          id
          customer { email }
        }
        userErrors { field message }
      }
    }
    """

    # Input để kết nối Customer đã có vào Company
    contact_input = {
        "firstName": "Viet",
        "lastName": "Hung",
        "email": f"hung2@example.com",
    }
    co_res = _client.execute(
        query=contact_create_mutation,
        variables={"companyId": company_id, "input": contact_input},
    )
    co_data = co_res.get("data", {}).get("companyContactCreate", {})

    if co_data.get("userErrors"):
        print(f"❌ Lỗi Create Contact: {co_data['userErrors'][0]['message']}")
        return

    contact_id = co_data.get("companyContact", {}).get("id")
    contact_email = co_data.get("companyContact", {}).get("customer", {}).get("email")
    print(f"✅ Đã gán {contact_email} làm người đại diện! Contact ID: {contact_id}")

    # --- 5. QUERY ALL COMPANIES & SAVE TO SQLITE ---
    print("🔍 Step 4: Querying B2B Data & Saving to SQLite...")

    get_all_companies_query = """
    query {
    companies(first: 5) {
        edges {
        node {
            id
            name
            # Thay mainLocation bằng cách query vào mảng locations
            locations(first: 1) {
            edges {
                node {
                id
                name
                }
            }
            }
            contacts(first: 1) {
            edges {
                node {
                id
                customer {
                    email
                }
                }
            }
            }
        }
        }
    }
    }
    """

    q_res = _client.execute(query=get_all_companies_query)
    edges = q_res.get("data", {}).get("companies", {}).get("edges", [])

    if not edges:
        print("⚠️ Không tìm thấy Company nào phù hợp để lưu.")
    else:
        for edge in edges:
            node = edge["node"]
            c_id = node["id"]
            c_name = node["name"]

            # Lấy thông tin Location chính
            loc_id = node.get("mainLocation", {}).get("id", "N/A")

            # Lấy thông tin Contact đầu tiên (nếu có)
            contacts_edges = node.get("contacts", {}).get("edges", [])
            contact_email = "No Contact"
            if contacts_edges:
                contact_email = contacts_edges[0]["node"]["customer"]["email"]

            # Lưu vào SQLite bảng training_entities
            repo.register_entity(
                entity_type="B2B_COMPANY",
                shopify_gid=c_id,
                note=f"Name: {c_name}, MainLoc: {loc_id}, Contact: {contact_email}",
            )
            print(f" 🔹 Đã lưu: {c_name} (ID: {c_id})")

    print("✨ Exercise 10 hoàn tất!")


if __name__ == "__main__":
    main()
