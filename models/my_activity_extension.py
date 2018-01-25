from odoo import models, fields, api
from datetime import date

class DateToDatetimeInMailActivity(models.Model):
    _inherit = 'mail.activity
    date_deadline = fields.Datetime('Due Date', index=True, required=True, default=fields.Datetime.now)

class DateToDatetimeInMailActivity(models.Model):
    _inherit = 'mail.activity.mixin'
    activity_date_deadline = fields.Datetime(
        'Next Activity Deadline', related='activity_ids.date_deadline',
        readonly=True, store=True,  # store to enable ordering + search
        groups="base.group_user")


