from odoo import models, fields, api

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    base_sku = fields.Char(string='Base SKU')
    color = fields.Char(string='Colour')
    size = fields.Char(string='Size')
    brand_id = fields.Many2one('product.brand', string='Brand')
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('unisex', 'Unisex')
    ], string='Gender')
    package_length = fields.Float(string='Package Length (cm)')
    package_width = fields.Float(string='Package Width (cm)')
    package_height = fields.Float(string='Package Height (cm)')
    supplier_product_code = fields.Char(string='Supplier Product Code')
    published = fields.Boolean(string='Published', default=False)
    supplier_ids = fields.Many2many('product.supplier', string='Suppliers')
    primary_supplier_id = fields.Many2one('product.supplier', string='Primary Supplier')
    wholesale_price = fields.Float(string='Wholesale Price', digits='Product Price')
    consignment_price = fields.Float(string='Consignment Price', digits='Product Price')

    @api.onchange('package_length', 'package_width', 'package_height')
    def _onchange_package_dimensions(self):
        if self.package_length and self.package_width and self.package_height:
            self.volume = (self.package_length * self.package_width * self.package_height) / 1000000  # Convert to m³