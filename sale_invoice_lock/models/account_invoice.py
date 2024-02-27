from odoo import models, fields, api
from odoo.exceptions import UserError


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    def write(self, vals):
        for rec in self.filtered(lambda i: any(s.state == 'done' for s in i.invoice_line_ids.mapped('sale_line_ids.order_id'))):
            if (not self.env.user.has_group('base.group_erp_manager')
                    and not self.env.user.has_group('base_exception.group_exception_rule_manager')
                    and not self.env.user.has_group('staf_meta.group_account_supp')):
                raise UserError('La commande relative est bloquée')
        return super().write(vals)
