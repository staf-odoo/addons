import datetime

from odoo import models, fields, api, _, SUPERUSER_ID


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    mrp_production_batch_id = fields.Many2one('mrp.production.batch')

    @api.model
    def create(self, vals):
        production = super().create(vals)
        if not production.mrp_production_batch_id:
            batch = self.env['mrp.production.batch'].search(
                [('state', '=', 'confirmed'), ('picking_type_id', '=', production.picking_type_id.id),
                 ('routing_id', '=', production.routing_id.id), ('origin', '=', production.origin)], limit=1)
            attribute_values = production.product_id.product_template_attribute_value_ids.filtered(lambda v: not v.attribute_id.group_in_mrp_batch)
            if batch and (attribute_values in batch.attribute_value_ids or attribute_values == batch.attribute_value_ids):
                production.write({'mrp_production_batch_id': batch.id})
                # if production.origin:
                #     batch.write({'origin': batch.origin + ',' + production.origin if batch.origin else production.origin})
            else:
                batch = self.env['mrp.production.batch'].create({
                    'origin': production.origin,
                    'routing_id': production.routing_id and production.routing_id.id or False,
                    'date_planned_start': production.date_planned_start,
                    'date_planned_finished': production.date_planned_finished,
                    'state': 'confirmed',
                    'user_id': production.user_id.id if production.user_id and production.user_id.id != SUPERUSER_ID else False,
                    'company_id': production.company_id.id,
                    'picking_type_id': production.picking_type_id.id,
                    'location_src_id': production.location_src_id.id,
                    'location_dest_id': production.location_dest_id.id,
                    'production_ids': [(6, 0, production.ids)]
                })
            batch.action_update_move_data()
        else:
            production.mrp_production_batch_id.action_update_move_data()
            production.mrp_production_batch_id.request_validation()
        return production

class MrpWorkorder(models.Model):
    _inherit = 'mrp.workorder'

    mrp_workorder_batch_id = fields.Many2one('mrp.workorder.batch', string='Lot de travail')

class MrpWorkcenter(models.Model):
    _inherit = 'mrp.workcenter'

    batch_order_ids = fields.One2many('mrp.workorder.batch', 'workcenter_id', "Batch Orders")

    # todo: fix me
    # @api.depends('batch_order_ids.duration_expected', 'batch_order_ids.workcenter_id', 'batch_order_ids.state', 'batch_order_ids.date_planned_start')
    # def _compute_workorder_count(self):
    #     MrpWorkorderBatch = self.env['mrp.workorder.batch']
    #     result = {wid: {} for wid in self.ids}
    #     result_duration_expected = {wid: 0 for wid in self.ids}
    #     #Count Late Workorder
    #     data = MrpWorkorderBatch.read_group([('workcenter_id', 'in', self.ids), ('state', 'in', ('pending', 'ready')), ('date_planned_start', '<', datetime.datetime.now().strftime('%Y-%m-%d'))], ['workcenter_id'], ['workcenter_id'])
    #     count_data = dict((item['workcenter_id'][0], item['workcenter_id_count']) for item in data)
    #     #Count All, Pending, Ready, Progress Workorder
    #     res = MrpWorkorderBatch.read_group(
    #         [('workcenter_id', 'in', self.ids)],
    #         ['workcenter_id', 'state', 'duration_expected'], ['workcenter_id', 'state'],
    #         lazy=False)
    #     for res_group in res:
    #         result[res_group['workcenter_id'][0]][res_group['state']] = res_group['__count']
    #         if res_group['state'] in ('pending', 'ready', 'progress'):
    #             result_duration_expected[res_group['workcenter_id'][0]] += res_group['duration_expected']
    #     for workcenter in self:
    #         workcenter.workorder_count = sum(count for state, count in result[workcenter.id].items() if state not in ('done', 'cancel'))
    #         workcenter.workorder_pending_count = result[workcenter.id].get('pending', 0)
    #         workcenter.workorder_ready_count = result[workcenter.id].get('ready', 0)
    #         workcenter.workorder_progress_count = result[workcenter.id].get('progress', 0)
    #         workcenter.workorder_late_count = count_data.get(workcenter.id, 0)
