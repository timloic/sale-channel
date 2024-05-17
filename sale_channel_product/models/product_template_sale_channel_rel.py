from odoo import fields, models


class ProductTemplateSaleChannelRel(models.Model):
    _name = "product.template.sale.channel.rel"
    _table = "product_template_sale_channel_rel"
    _description = "Product template sale channel Relation"
    _inherit = "sale.channel.relation"

    product_template_id = fields.Many2one(
        "product.template", string="Product Template", required=True
    )
