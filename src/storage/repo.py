from __future__ import annotations
from typing import Any

# execute/query_all are provided. Trainees must write raw SQL.
from src.storage.db import execute, execute_many, query_all


def create_tables() -> None:
    """
    TODO:
    Create tables using raw SQL.

    Suggested tables:

    1) training_products
       - product_gid TEXT PRIMARY KEY
       - title TEXT
       - handle TEXT
       - status TEXT

    2) training_variants
       - variant_gid TEXT PRIMARY KEY
       - product_gid TEXT
       - title TEXT
       - sku TEXT
       - price TEXT
       - inventory_item_gid TEXT

    3) training_locations
       - location_gid TEXT PRIMARY KEY
       - name TEXT

    4) training_entities (registry for cleanup)
       - entity_type TEXT
       - shopify_gid TEXT PRIMARY KEY
       - note TEXT
    """
    # 1. Bảng Products
    execute(
        """
        CREATE TABLE IF NOT EXISTS training_products (
            product_gid TEXT PRIMARY KEY,
            title TEXT,
            handle TEXT,
            status TEXT
        )
    """
    )
    # 2. Bảng Variants
    execute(
        """
        CREATE TABLE IF NOT EXISTS training_variants (
            variant_gid TEXT PRIMARY KEY,
            product_gid TEXT,
            title TEXT,
            sku TEXT,
            price TEXT,
            inventory_item_gid TEXT
        )
    """
    )
    # 4. Bang Registry
    execute(
        """
        CREATE TABLE IF NOT EXISTS training_entities (
            entity_type TEXT,
            shopify_gid TEXT PRIMARY KEY,
            note TEXT
        )
    """
    )


def register_entity(
    entity_type: str, shopify_gid: str, note: str | None = None
) -> None:
    """
    TODO:
    Insert an entity into training_entities registry table using raw SQL.
    """

    sql = """
        INSERT INTO training_entities (shopify_gid, entity_type, note)
        VALUES (?, ?, ?)
        ON CONFLICT(shopify_gid) DO UPDATE SET
            entity_type = excluded.entity_type,
            note = excluded.note
    """

    execute(sql, (shopify_gid, entity_type, note))


def list_entities(entity_type: str | None = None) -> list[dict[str, Any]]:
    """
    TODO:
    Select entities from training_entities using raw SQL.
    """
    raise NotImplementedError


def delete_entity_record(shopify_gid: str) -> None:
    """
    TODO:
    Delete one entity row by shopify_gid.
    """
    raise NotImplementedError


def upsert_location(location_gid: str, name: str) -> None:
    """
    TODO:
    Insert or replace a location row.
    """
    raise NotImplementedError


def get_any_location_gid() -> str:
    """
    TODO:
    Return one location_gid from training_locations.
    Raise if none exists.
    """
    raise NotImplementedError


def upsert_product(
    product_gid: str, title: str, handle: str | None, status: str | None
) -> None:
    """
    TODO:
    Insert or replace a product row.
    """
    sql = """
        INSERT INTO training_products (product_gid, title, handle, status)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(product_gid) DO UPDATE SET
            title = excluded.title,
            handle = excluded.handle,
            status = excluded.status
    """
    execute(sql, (product_gid, title, handle, status))


def upsert_variant(
    variant_gid: str,
    product_gid: str,
    title: str | None,
    sku: str | None,
    price: str | None,
    inventory_item_gid: str | None,
) -> None:
    """
    TODO:
    Insert or replace a variant row.
    """
    sql = """
        INSERT INTO training_variants (variant_gid, product_gid, title, sku, price, inventory_item_gid)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(variant_gid) DO UPDATE SET
            product_gid = excluded.product_gid,
            title = excluded.title,
            sku = excluded.sku,
            price = excluded.price,
            inventory_item_gid = excluded.inventory_item_gid
    """
    execute(sql, (variant_gid, product_gid, title, sku, price, inventory_item_gid))


def list_products_with_variants() -> list[dict[str, Any]]:
    """
    TODO:
    Return a joined view:
    - product_gid, product_title
    - variant_gid, inventory_item_gid
    This is used for quantity update and cleanup.
    """
    sql = """
        SELECT 
            p.product_gid, 
            p.title AS product_title, 
            v.variant_gid, 
            v.inventory_item_gid
        FROM training_products p
        JOIN training_variants v ON p.product_gid = v.product_gid
    """
    return query_all(sql)
