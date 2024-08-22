from odoo import models, fields

class Supplier(models.Model):
    _name = 'product.supplier'
    _description = 'Product Supplier'

    name = fields.Char(string='Name', required=True)
    code = fields.Char(string='Supplier Code')
    contact_person = fields.Char(string='Contact Person')
    email = fields.Char(string='Email')
    phone = fields.Char(string='Phone')
    website = fields.Char(string='Website')
    lead_time = fields.Integer(string='Lead Time (days)')
    min_order_qty = fields.Float(string='Minimum Order Quantity')
    currency_id = fields.Many2one('res.currency', string='Currency')