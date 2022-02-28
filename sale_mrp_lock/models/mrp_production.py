from odoo import models, fields, api
from odoo.exceptions import UserError


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    # .with_context(auth_editing=True)
    def write(self, vals):
        for rec in self.sudo().filtered(lambda i: i.sale_id and i.sale_id.state == 'done'):
            if not self.env.user.has_group('base.group_erp_manager'):
                raise UserError('L\'ordre de fabrication est bloquée par la commande ' + rec.sale_id.name)
        return super().write(vals)
