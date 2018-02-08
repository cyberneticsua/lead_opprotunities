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
from odoo.exceptions import Warning

class LeadAlternativeProduct(models.Model):
    _inherit = 'crm.lead'
    alt_pdt_line = fields.One2many('crm.alt_pdt_line', 'pdt_crm', string="Альтернат.товари")

    # @api.one
    def _check_all_alternative_products (self):
        for data in self.alt_pdt_line:
            data.write ({'checked_for_parsing':True})

    @api.multi
    def find_alternative_products(self, vals):
        data = self.env['product.template'].search([('id', '=', vals.get('prod_id'))])
        # raise Warning (data.alternative_product_ids)
        for alt_prod in data.alternative_product_ids:
            alt_pdt_value = {
                            'product_id': alt_prod.id,
                            'name': alt_prod.name,
                            'default_code':alt_prod.default_code,
                            'checked_for_Parsing':True,
                            'pdt_crm':vals.get('new_oppor_id'),
                            'price_unit':alt_prod.list_price,
                            'market_price':alt_prod.standard_price,
                            'qty_hand':alt_prod.qty_available,
                            'product_brand':alt_prod.product_brand_id.name,
                            }
            
            alt_pdt_line=self.env['crm.alt_pdt_line'].create(alt_pdt_value)
            # raise Warning (alt_pdt_line['pdt_crm'])
            
            

class AlternativeProduct(models.Model):
    _name = 'crm.alt_pdt_line'
    product_id = fields.Many2one('product.template', string="Товар",
                                 change_default=False, ondelete='restrict', required=True,) 
                                # domain= lambda self: self._get_product_domain())
    name = fields.Text(string='Опис')
    default_code = fields.Text(string='Код товару')
    
    pdt_crm = fields.Many2one('crm.lead', string='Деталь')
    product_uom_qty = fields.Float(string='Кількість', default=1.0)
    price_unit = fields.Float(string='Ціна')
    market_price = fields.Float(string='Ціна продажу')
    qty_hand = fields.Integer(string='Наявна кількість')
    sequence = fields.Integer(string='Sequence', default=10)

    checked_for_parsing= fields.Selection(
        [('yes', 'Yes'), ('no', 'No')], string='Yes/No'
    )
    

    product_brand = fields.Char(
        string='Бренд',
        help='Бренд товару'
    )
    
    product_categ=fields.Char(
        string='Категорія',
        help='Категорія товару'
    )

    

    # Можна використати для попереднього фільтрування
    # @api.onchange('product_id')
    # def _get_product_domain(self):
    #     res = {}
    #     my_domain=[]
    #     if (self.pdt_crm.third_level_category.id):
    #         my_domain.append(('public_categ_ids','child_of',self.pdt_crm.third_level_category.id))
    #     elif (self.pdt_crm.second_level_category.id):
    #         my_domain.append(('public_categ_ids','child_of',self.pdt_crm.second_level_category.id))
    #     elif (self.pdt_crm.first_level_category.id):
    #         my_domain.append(('public_categ_ids','child_of',self.pdt_crm.first_level_category.id))
    #     res['domain']={'product_id':my_domain}
    #     return res

    # def product_data(self):
    #     data = self.env['product.template'].search([('name', '=', self.product_id.name)])
    #     # if (not(self.pdt_crm.second_level_category.id)):
    #     #     raise Warning(self.pdt_crm.second_level_category.id) 
    #     # else:
    #     self.name = data.name
    #     self.price_unit = data.list_price
    #     self.uom_id = data.uom_id
    #     self.market_price = data.standard_price
    #     self.qty_hand = data.qty_available
    #     self.isSplitted = False
    #     # self.categ_id= data.public_categ_ids
    #     self.default_code=data.default_code
    #     self.product_brand=data.product_brand_id.name
    #     if (self.pdt_crm.third_level_category.id):
    #         self.product_categ=self.pdt_crm.third_level_category.name
    #     elif (self.pdt_crm.second_level_category.id):
    #         self.product_categ=self.pdt_crm.second_level_category.name
    #     elif (self.pdt_crm.first_level_category.id):
    #         self.product_categ=self.pdt_crm.first_level_category.name