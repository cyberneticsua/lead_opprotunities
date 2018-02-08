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
from odoo.exceptions import UserError
from odoo.exceptions import Warning

class ActivityControl (models.Model):
    _inherit='crm.lead'
    
    

    @api.onchange('stage_id')
    def _onchange_stage_id(self):
        ####Помилка при перенесенні деталі без коду
        my_crm=self.env['crm.lead'].search([('id','=',self._origin.id)])
        qty_sales = 0
        for data in my_crm.pdt_line:
            if (data.default_code):
                qty_sales += 1
                # raise Warning (data.default_code)

        # raise Warning (qty_sales)        
        if (not qty_sales):
            raise Warning(('Ви намагаєтесь перенести деталь без коду')) 
        values = self._onchange_stage_id_values(self.stage_id.id)
        self.update(values)
        
        #код для оновлення pdt_line
        my_pdt_line = self.env['crm.product_line'].search([('child_opportunity', '=', int(self._origin.id))])
        my_pdt_line.write({'stage_name':self.stage_id.name})

    @api.multi
    def write(self, vals):
        if ((self.stage_id.id==1)and (self.type == 'opportunity')):
            qty_sales = 0
            for data in self.pdt_line:
                if (data.default_code):
                    qty_sales += 1
            if (qty_sales>0):
                vals['stage_id'] = 2

        if (self.name=="Діалог"):
            if (self.partner_id.id):
                vals['name']=self.partner_id.name
        res = super(ActivityControl, self).write(vals)
        
        
        