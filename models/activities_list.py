# -*- coding: utf-8 -*-

from odoo import api, fields, models

class ActivityTypeList(models.Model):
    _inherit = ['mail.activity']

    
    def return_values(self):
        
        return {
             'type': 'ir.actions.act_window',
             'res_model': self.res_model,
             'res_id':self.res_id,
             'view_type': 'form',
             'view_mode': 'form',
             'target': 'main',
             'view_id':False,
         }

    
