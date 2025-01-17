import re
from odoo import models, fields, api
from odoo.exceptions import UserError

class BarcodeScanner(models.Model):
    _name = 'barcode.scanner'
    _description = 'Barcode Scanner'

    name = fields.Char('Session Name', required=True)
    location_id = fields.Many2one('stock.location', 'Location', required=True)
    scanned_item_ids = fields.One2many('barcode.scanner.line', 'scanner_id', 'Scanned Items')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('done', 'Done')
    ], string='Status', default='draft')

    def action_scan_item(self, barcode, quantity, operation_type):
        self.ensure_one()
        if self.state != 'draft':
            raise UserError('You can only add or remove items in draft state.')

        product = self.env['product.product'].search([('barcode', '=', barcode)], limit=1)
        if not product:
            raise UserError(f'No product found with barcode {barcode}')

        quantity = abs(quantity) if operation_type == 'add' else -abs(quantity)
        existing_line = self.scanned_item_ids.filtered(lambda l: l.barcode == barcode)
        
        if existing_line:
            new_quantity = existing_line.quantity + quantity
            if new_quantity < 0 and abs(new_quantity) > existing_line.available_quantity:
                raise UserError(f'Cannot remove more than the available quantity ({existing_line.available_quantity}).')
            existing_line.quantity = new_quantity
            if existing_line.quantity == 0:
                existing_line.unlink()
        else:
            quant = self.env['stock.quant'].search([
                ('product_id', '=', product.id),
                ('location_id', '=', self.location_id.id)
            ], limit=1)
            available_quantity = quant.quantity if quant else 0.0
            if quantity < 0 and abs(quantity) > available_quantity:
                raise UserError(f'Cannot remove more than the available quantity ({available_quantity}).')
            self.env['barcode.scanner.line'].create({
                'scanner_id': self.id,
                'barcode': barcode,
                'product_id': product.id,
                'quantity': quantity,
                'available_quantity': available_quantity
            })
        return True

    def action_open_view_item_wizard(self):
        self.ensure_one()
        return {
            'name': 'View Item',
            'type': 'ir.actions.act_window',
            'res_model': 'barcode.scanner.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_operation_type': 'view'},
        }

    def action_view_item(self, barcode):
        self.ensure_one()
        product = self.env['product.product'].search([('barcode', '=', barcode)], limit=1)
        if not product:
            raise UserError(f'No product found with barcode {barcode}')
        return {
            'name': 'Product',
            'type': 'ir.actions.act_window',
            'res_model': 'product.product',
            'res_id': product.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_confirm(self):
        self.ensure_one()
        if not self.scanned_item_ids:
            raise UserError('No items scanned')
        self.state = 'confirmed'
        return True

    def action_update_inventory(self):
        self.ensure_one()
        if self.state != 'confirmed':
            raise UserError('Please confirm the scanned items before updating inventory')

        for line in self.scanned_item_ids:
            products = self.env['product.product'].search([('barcode', '=', line.barcode)])
            if len(products) > 1:
                return self._open_conflict_wizard(line)
            elif not products:
                raise UserError(f'No product found with barcode {line.barcode}')
            
            quant = self.env['stock.quant'].search([
                ('product_id', '=', products.id),
                ('location_id', '=', self.location_id.id)
            ], limit=1)

            if quant:
                quant.inventory_quantity = quant.quantity + line.quantity
            else:
                if line.quantity < 0:
                    raise UserError(f"Cannot remove quantity for non-existent stock of product with barcode {line.barcode}")
                self.env['stock.quant'].create({
                    'product_id': products.id,
                    'location_id': self.location_id.id,
                    'inventory_quantity': line.quantity,
                })

        self.state = 'done'
        return {
            'type': 'ir.actions.act_window',
            'name': 'Inventory Update Summary',
            'res_model': 'barcode.scanner',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def _open_conflict_wizard(self, line):
        products = self.env['product.product'].search([('barcode', '=', line.barcode)])
        return {
            'name': 'Resolve Barcode Conflict',
            'type': 'ir.actions.act_window',
            'res_model': 'barcode.conflict.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_barcode': line.barcode,
                'default_quantity': line.quantity,
                'default_product_ids': [(6, 0, products.ids)],
                'default_scanner_id': self.id,
                'default_location_id': self.location_id.id,
            }
        }

    def action_revert_to_draft(self):
        self.ensure_one()
        if self.state != 'confirmed':
            raise UserError('You can only revert to draft from the confirmed state.')
        self.state = 'draft'
        return True

class BarcodeScannerLine(models.Model):
    _name = 'barcode.scanner.line'
    _description = 'Barcode Scanner Line'

    scanner_id = fields.Many2one('barcode.scanner', 'Scanner')
    barcode = fields.Char('Barcode', required=True)
    quantity = fields.Float('Quantity')  
    product_id = fields.Many2one('product.product', 'Product', required=True)
    available_quantity = fields.Float('Available Quantity', compute='_compute_available_quantity', store=True)
    operation_type = fields.Selection([
        ('add', 'Added'),
        ('remove', 'Removed')
    ], string='Operation', compute='_compute_operation_type', store=True)

    @api.depends('quantity')
    def _compute_operation_type(self):
        for line in self:
            line.operation_type = 'add' if line.quantity > 0 else 'remove'

    @api.depends('product_id', 'scanner_id.location_id')
    def _compute_available_quantity(self):
        for line in self:
            quant = self.env['stock.quant'].search([
                ('product_id', '=', line.product_id.id),
                ('location_id', '=', line.scanner_id.location_id.id)
            ], limit=1)
            line.available_quantity = quant.quantity if quant else 0.0

class BarcodeConflictWizard(models.TransientModel):
    _name = 'barcode.conflict.wizard'
    _description = 'Barcode Conflict Resolution Wizard'

    barcode = fields.Char('Barcode', readonly=True)
    quantity = fields.Float('Quantity', readonly=True)
    product_ids = fields.Many2many('product.product', string='Conflicting Products')
    selected_product_id = fields.Many2one('product.product', string='Select Product')
    scanner_id = fields.Many2one('barcode.scanner', 'Scanner')
    location_id = fields.Many2one('stock.location', 'Location')

    def action_resolve_conflict(self):
        self.ensure_one()
        if not self.selected_product_id:
            raise UserError('Please select a product to resolve the conflict')

        quant = self.env['stock.quant'].search([
            ('product_id', '=', self.selected_product_id.id),
            ('location_id', '=', self.location_id.id)
        ], limit=1)

        if quant:
            quant.inventory_quantity = quant.quantity + self.quantity
        else:
            self.env['stock.quant'].create({
                'product_id': self.selected_product_id.id,
                'location_id': self.location_id.id,
                'inventory_quantity': self.quantity,
            })

        return self.scanner_id.action_update_inventory()

class BarcodeScannerWizard(models.TransientModel):
    _name = 'barcode.scanner.wizard'
    _description = 'Barcode Scanner Wizard'

    barcode = fields.Char('Barcode', required=True)
    quantity = fields.Float('Quantity', default=1.0)
    operation_type = fields.Selection([
        ('add', 'Add'),
        ('remove', 'Remove'),
        ('view', 'View')
    ], string='Operation Type', required=True)

    @api.onchange('operation_type')
    def _onchange_operation_type(self):
        if self.operation_type == 'remove':
            self.quantity = abs(self.quantity)  
        elif self.operation_type == 'add':
            self.quantity = abs(self.quantity)

    def action_process(self):
        self.ensure_one()
        active_id = self.env.context.get('active_id')
        if active_id:
            scanner = self.env['barcode.scanner'].browse(active_id)
            if self.operation_type == 'view':
                return scanner.action_view_item(self.barcode)
            else:
                scanner.action_scan_item(self.barcode, self.quantity, self.operation_type)
        return {'type': 'ir.actions.act_window_close'}

class BarcodeScannerBulkWizard(models.TransientModel):
    _name = 'barcode.scanner.bulk.wizard'
    _description = 'Barcode Scanner Bulk Wizard'

    bulk_barcodes = fields.Text('Bulk Barcodes', required=True, help="Enter barcodes separated by commas or new lines")
    operation_type = fields.Selection([
        ('add', 'Add'),
        ('remove', 'Remove')
    ], string='Operation Type', required=True)

    def action_process_bulk(self):
        self.ensure_one()
        active_id = self.env.context.get('active_id')
        if active_id:
            scanner = self.env['barcode.scanner'].browse(active_id)
            if not scanner or scanner.state != 'draft':
                raise UserError('You can only bulk add or remove items in draft state.')

            # Normalize the input to handle commas and new lines
            barcodes = re.split(r'[\s,]+', self.bulk_barcodes.strip())
            barcodes = [barcode.strip() for barcode in barcodes if barcode.strip()]

            for barcode in barcodes:
                scanner.action_scan_item(barcode, 1, self.operation_type)
                
        return {'type': 'ir.actions.act_window_close'}
