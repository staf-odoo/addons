# -*- coding: utf-8 -*-

from odoo import models, fields, api, tools

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    amount_undelivered = fields.Monetary(string=u'Total Pending', store=True, readonly=True, compute='_amount_delivered_invoiced', track_visibility='always')
    amount_delivered = fields.Monetary(string=u'Total Delivered', store=True, readonly=True, compute='_amount_delivered_invoiced', track_visibility='always')
    amount_invoiced = fields.Monetary(string=u'Total Invoiced', store=True, readonly=True, compute='_amount_delivered_invoiced', track_visibility='always')
    total_invoiced = fields.Monetary(string=u'Total Invoiced', store=True, readonly=True, compute='_total_invoiced', track_visibility='always')

    @api.depends('order_line.price_delivered', 'order_line.price_undelivered', 'order_line.price_invoiced')
    def _amount_delivered_invoiced(self):
        for order in self:
            order.update({
                'amount_undelivered': sum(order.order_line.mapped('price_undelivered')),
                'amount_delivered': sum(order.order_line.mapped('price_delivered')),
                'amount_invoiced': sum(order.order_line.mapped('price_invoiced')),
            })

    @api.depends('state', 'invoice_ids.amount_total_signed', 'invoice_ids.state')
    def _total_invoiced(self):
        for order in self:
            order.update({
                'total_invoiced': sum(order.invoice_ids.mapped('amount_total_signed')),
            })

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    price_undelivered = fields.Monetary(compute='_compute_amount_delivered_invoiced', string='Amount Pending', readonly=True, store=True)
    price_delivered = fields.Monetary(compute='_compute_amount_delivered_invoiced', string='Amount Delivered', readonly=True, store=True)
    price_invoiced = fields.Monetary(compute='_compute_amount_delivered_invoiced', string='Amount Invoiced', readonly=True, store=True)
    qty_undelivered = fields.Float(compute='_compute_amount_delivered_invoiced', string='Qty Pending', readonly=True,
                                      store=True)

    @api.depends('price_total', 'qty_delivered', 'qty_invoiced')
    def _compute_amount_delivered_invoiced(self):
        for line in self:
            line.update({

                'price_undelivered': line.price_total * ((line.product_uom_qty - line.qty_delivered) / line.product_uom_qty) if line.product_uom_qty else 0,
                'price_delivered': line.price_total * (line.qty_delivered / line.product_uom_qty) if line.product_uom_qty else 0,
                'price_invoiced': line.price_total * (line.qty_invoiced / line.product_uom_qty) if line.product_uom_qty else 0,
                'qty_undelivered': (line.product_uom_qty - line.qty_delivered) if line.product_uom_qty else 0,
            })

class SaleReport(models.Model):
    _inherit = 'sale.report'

    price_undelivered = fields.Float('Total en cours', readonly=True)
    price_delivered = fields.Float('Total livré', readonly=True)
    price_invoiced = fields.Float('Total facturé', readonly=True)

    warehouse_id = fields.Many2one('stock.warehouse', 'Warehouse', readonly=True)

    def _query(self, with_clause='', fields={}, groupby='', from_clause=''):
        fields['price_undelivered'] = ", sum(l.price_undelivered / CASE COALESCE(s.currency_rate, 0) WHEN 0 THEN 1.0 ELSE s.currency_rate END) as price_undelivered"
        fields['price_delivered'] = ", sum(l.price_delivered / CASE COALESCE(s.currency_rate, 0) WHEN 0 THEN 1.0 ELSE s.currency_rate END) as price_delivered"
        fields['price_invoiced'] = ", sum(l.price_invoiced / CASE COALESCE(s.currency_rate, 0) WHEN 0 THEN 1.0 ELSE s.currency_rate END) as price_invoiced"
        return super(SaleReport, self)._query(with_clause, fields, groupby, from_clause)
