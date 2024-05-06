from .mirakl_json import MiraklJson


class MiraklOffer(MiraklJson):

    sku: str
    product_id: str
    product_id_type: str
    state: str

    @classmethod
    def map_item(cls, mirakl_channel, product):
        """

        :param mirakl_channel:
        :param product: product to map
        :return: a pydantic object corresponding to the form expected by mirakl
        """
        relation_prod_channel = product.product_tmpl_id.prod_sale_channel_ids.filtered(
            lambda r: r.sale_channel_id == mirakl_channel.channel_id
        )
        return cls(
            sku=relation_prod_channel.mirakl_code,
            product_id=product.barcode if product.barcode else product.default_code,
            product_id_type="EAN" if product.barcode else "SHOP_SKU",
            state="11",
        )

    @classmethod
    def get_offers_file_header(cls):
        return ["sku", "product-id", "product-id-type", "state"]

    @classmethod
    def get_additional_option_for_file(cls):
        return {"import_mode": "NORMAL"}

    def to_json(self):
        return {
            "sku": self.sku,
            "product-id": self.product_id,
            "product-id-type": self.product_id_type,
            "state": self.state,
        }
