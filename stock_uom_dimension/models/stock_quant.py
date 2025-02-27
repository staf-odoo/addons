from odoo import models, api, fields


class StockQuant(models.Model):
    _inherit = ['stock.quant', 'uom.line']
    _name = 'stock.quant'

    _uom_field = 'product_uom_id'
    _qty_field = 'quantity'

    dimension_ids = fields.One2many('stock.quant.dimension', 'line_id', string='Dimensions', copy=True)

    @api.depends(_qty_field)
    def _get_product_dimension_qty(self):
        super()._get_product_dimension_qty()

    @api.model
    def create(self, vals):
        if self.env.context.get('dimension_ids', False):
            vals.update({
                'dimension_ids': [(0, 0, {'dimension_id': k, 'quantity': v}) for k, v in self.env.context.get('dimension_ids').items()]
            })
        return super().create(vals)

    def _gather(self, product_id, location_id, lot_id=None, package_id=None, owner_id=None, strict=False):
        quants = super(StockQuant, self)._gather(product_id, location_id, lot_id, package_id, owner_id, strict)
        if self.env.context.get('dimension_ids') and product_id.stock_dimensions_strict:
            return quants.filtered(lambda q:
                                   all(d in self.env.context.get('dimension_ids').keys() for d in q.dimension_ids.mapped('dimension_id').ids) and
                                   all(d.quantity == self.env.context['dimension_ids'].get(d.dimension_id.id, 0) for d in q.dimension_ids))
        return quants


class StockMoveDimension(models.Model):
    _inherit = 'uom.line.dimension'
    _name = 'stock.quant.dimension'

    line_id = fields.Many2one('stock.quant', required=True, ondelete='cascade')
