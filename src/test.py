import requests
import os
from dotenv import load_dotenv

# 1. Tải các biến từ file .env vào hệ thống
load_dotenv()

# 2. Lấy dữ liệu từ env (Nếu không tìm thấy sẽ trả về None)
SHOP_DOMAIN = os.getenv("SHOPIFY_SHOP_DOMAIN")
API_VERSION = os.getenv("SHOPIFY_ADMIN_API_VERSION")
ACCESS_TOKEN = os.getenv("SHOPIFY_ADMIN_ACCESS_TOKEN")

# 3. Tạo URL động từ env
url = f"https://{SHOP_DOMAIN}/admin/api/{API_VERSION}/graphql"

headers = {"Content-Type": "application/json", "X-Shopify-Access-Token": ACCESS_TOKEN}

query = """
query ProductMetafields($ownerId: ID!) {
  product(id: $ownerId) {
    id
    title
    handle
    descriptionHtml
    status
    vendor
    productType
    metafields(first: 3) {
      edges {
        node {
          namespace
          key
          value
        }
      }
    }
  }
}
"""

variables = {"ownerId": "gid://shopify/Product/8863709364381"}

# Gửi request
response = requests.post(
    url, json={"query": query, "variables": variables}, headers=headers
)

# In kết quả
print(response.json())
