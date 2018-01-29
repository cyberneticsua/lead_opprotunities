from odoo import models, fields, api

class DateToDatetimeInMailActivity(models.Model):
    _inherit = 'mail.activity'
    new_date_deadline = fields.Datetime('Due Date', index=True, required=True, default=fields.Datetime.now)


# class DateToDatetimeInMailActivityMixin(models.Model):
    # _inherit = 'mail.activity.mixin'
    # new_activity_date_deadline = fields.Datetime(
    #     'Next Activity Deadline', related='activity_ids.new_date_deadline',
    #     readonly=True, store=True,  # store to enable ordering + search
    #     groups="base.group_user")


