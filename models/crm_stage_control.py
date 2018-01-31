# -*- coding: utf-8 -*-
##############################################################################
#    Exa.cv.ua.
#    Copyright (C) 2017-TODAY Exa.cv.ua(<http://www.exa.cv.ua>).
#    Author: Igor Vinnychuk (<http://www.exa.cv.ua>)
#    Author: Andrii Verstiak (<http://www.exa.cv.ua>)
#
##############################################################################

from odoo import models, fields, api
from datetime import date

class ActivityControl (models.Model):
    _inherit='crm.lead'
    
    @api.onchange('stage_id')
    def _onchange_stage_id(self):
        values = self._onchange_stage_id_values(self.stage_id.id)
        self.update(values)
        #код для оновлення pdt_line
        my_pdt_line = self.env['crm.product_line'].search([('child_opportunity', '=', int(self._origin.id))])
        my_pdt_line.write({'stage_name':self.stage_id.name})