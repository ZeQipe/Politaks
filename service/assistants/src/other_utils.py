from .links_bases import *

async def get_related_products(domain: str, product_name: str):
    if domain == "main":
        return main_relation_base.get(product_name, {})

    return {}

async def get_product_link(domain: str, product_name: str):
    if domain == "main":
        if product_name == "_all":
            return main_link_base
        return main_link_base.get(product_name, "")

    return {}
