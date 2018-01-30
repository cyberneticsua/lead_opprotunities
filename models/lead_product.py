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

activity_ids_list=[8, 9,10,11]
sales_order_states = [
    'progress', 'manual', 'shipping_exept', 'invoice_except', 'done']

#######15.01.2018################################
#######Фільтри для категорій#####################
class ProductCategoryInLead(models.Model):
    _inherit = 'crm.lead'
    first_level_category = fields.Many2one(
        'product.category',
        string='Категорія товару',
        domain="[('parent_id', '=', False)]",
        # domain=_getCategoryId,
        help='Категорія товару',
        )
    
    second_level_category=fields.Many2one(
        'product.category',
        string='Підкатегорія товару',
        help='Підкатегорія товару',
    )

    second_level_category_id = fields.Integer(
        string='Child categories for second level',
        compute='_get_second_level_value',
    )
    
    show_second_level_category = fields.Boolean(
        string='Show/hide second category',
        default = False,
        compute='_get_second_level_value',
    )
    
    third_level_category=fields.Many2one(
        'product.category',
        string='Підкатегорія товару',
        help='Підкатегорія товару',
    )

    third_level_category_id = fields.Integer(
        string='Child categories for third level',
        compute='_get_third_level_value',
    )
    
    show_third_level_category = fields.Boolean(
        string='Show/hide third category',
        default = False,
        compute='_get_third_level_value',
    )
    
    # @api.one
    @api.onchange('first_level_category')
    def _get_second_level_value(self):
        if self.first_level_category.name:
            self.show_second_level_category = True
            self.second_level_category_id = self.first_level_category.id
        else:
            self.show_second_level_category = False
            self.show_third_level_category=False

    # @api.one
    @api.onchange('second_level_category')
    def _get_third_level_value(self):
        if self.second_level_category.name:
            self.show_third_level_category = True
            self.third_level_category_id = self.second_level_category.id
        else:
            self.show_third_level_category = False    

    # @api.model
    # def _get_my_name(self):
    #     result = []
    #     for record in self.first_level_category:
    #         name = '[' + str(record.id) + ']' + ' ' + record.name
    #         result.append((record.id, name))
    #     return result

    # def _get_my_name(self):
    #     res = []
    #     for record in self:
    #         res.append((record.id, record.name))
    #     return res

class LeadProduct(models.Model):
    _inherit = 'crm.lead'
    pdt_line = fields.One2many('crm.product_line', 'pdt_crm', string="Product")
    sales_order_count = fields.Integer(compute='count_sales_order')
    base_opportunity = fields.Boolean(
        string='IsBaseOpportuinty',
        default=False,
    )
        
    # parent_opportunity = fields.One2many(
    #     string='Parent Opportunities',
    #     comodel_name='crm.lead',
    #     inverse_name='inverse_field',
    # )
    
    # child_opportunities = fields.Many2one(
    #     string='Child opprotunities',
    #     comodel_name='crm.lead',
    # )
    ###########################11.01.2018#########################################
    #########Підрахунок кількості деталей для замовлення 
    def count_sales_order(self):
        # if not self.partner_id:
        #     return False
        count=0
        for data in self.pdt_line:
            if data.child_opportunity:
                count=count+1
        # my_pdt_line = self.env['crm.product_line'].search([('child_opportunity', '=', int(self._origin.id))])
        # my_pdt_line.write({'stage_name':self.stage_id.name})
        self.sales_order_count = count
        # self.sales_order_count = self.env['sale.order'].search_count([
        #     ('partner_id', '=', self.partner_id.id),
        #     ('state', 'in', sales_order_states),
        # ])
        
    #############Перехід до списку opportunities
    # @api.multi
    # def get_opportunity_view(self, order_states, view_title):
    @api.model
    def get_opportunity_view(self, view_title):
        partner_ids = self.partner_id.id
        child_ids = []
        for data in self.pdt_line:
            if data.child_opportunity:
                child_ids.append(data.child_opportunity)
        
        opportunities = self.env['crm.lead'].search([
            # ('partner_id', 'in', partner_ids),
            ('id', 'in', child_ids),
        ])
        res = {
            'name': view_title,
            'type': 'ir.actions.act_window',
            'res_model': 'crm.lead',
            'view_type': 'form',
        }
        if len(opportunities) == 1:
            res['res_id'] = opportunities[0].id
            res['view_mode'] = 'form'
        else:
            res['domain'] = [
                # ('state', 'in', order_states),
                # ('partner_id', 'in', partner_ids),
                ('id', 'in', child_ids),
            ]
            res['view_mode'] = 'kanban,tree,form'
        return res

    @api.multi
    def button_opportunities(self):
        return self.get_opportunity_view("Список деталей")
   ###########################11.01.2018#########################################    

    #Створення Quotation з Product Line
    def sale_action_quotations_new(self):
        for data in self.pdt_line:        
            vals = {
            'partner_id': self.partner_id.id,
            'user_id': self.user_id.id,
            'opportunity_id':self.id
               }
            sale_order = self.env['sale.order'].create(vals)
            order_line = self.env['sale.order.line']
            pdt_value = {
                        'order_id': sale_order.id,
                        'product_id': data.product_id.id,
                        'name': data.name,
                        'product_uom_qty': data.product_uom_qty,
                }
            order_line.create(pdt_value)

    # Оновлення етапів в ліді
    def update_parts_stage(self):
        for data in self.pdt_line:
            new_opportunity= self.env['crm.lead'].search([('id', '=', data.child_opportunity)])
            stage_name = self.env['crm.stage'].search([('id', '=', new_opportunity.stage_id.id)])
            data.write ({'stage_name':stage_name.name})         

    def sale_action_opportunities_new(self):
        ####################################################
        self.base_opportunity = True
        countt=1
        for data in self.pdt_line:        
            if (not data.isSplitted):
                # Creating opportunity###############
                # my_tag_ids =[]
                # for my_tag_id in self.tag_ids
                #     my_tag_ids.append(my_tag_id)
                if data.default_code:
                    st_id = 2
                else:
                    st_id = 1
                vals = {
                'partner_id': self.partner_id.id,
                'user_id': self.env.uid,
                'name': data.name,
                'stage_id':st_id,
                'type':'opportunity',
                'priority':self.priority,
                
                #####################################################
                #############Змінити час№№№№№№№
                'date_deadline':date.today().strftime('%Y-%m-%d'),
                # 'tag_ids':my_tag_ids,
                }
                new_opportunity = self.env['crm.lead'].create(vals)
                
                # Creating product line in opportunity##########
                pdt_line = self.env['crm.product_line']
                pdt_value = {
                            'product_id': data.product_id.id,
                            'name': data.name,
                            'product_uom_qty': data.product_uom_qty,
                            'default_code':data.default_code,
                            'pdt_crm':new_opportunity.id,
                            'price_unit':data.price_unit,
                            'market_price':data.market_price,
                            'qty_hand':data.qty_hand,
                            'isSplitted': True,
                            }
                pdt_line.create(pdt_value)
                data1 = self.env['ir.model'].search([('model', '=', 'crm.lead')])
                
                #Creating activity###############
                act_vals={
                    'activity_type_id':activity_ids_list[st_id-1],
                    'date_deadline':date.today().strftime('%Y-%m-%d'),
                    'res_id':new_opportunity.id,
                    'res_model_id':data1.id,
                }
                my_activity = self.env['mail.activity'].create(act_vals)

                #Setting stage stage#################
                stage_name = self.env['crm.stage'].search([('id', '=', new_opportunity.stage_id.id)])
                data.write ({'stage_name':stage_name.name,'product_stage_id':new_opportunity.stage_id,'child_opportunity':int(new_opportunity.id)})
        self.pdt_line.write({'isSplitted':True})
        
        if self.description:
            data1 = self.env['ir.model'].search([('model', '=', 'crm.lead')])
            act_vals={
                    'activity_type_id':activity_ids_list[3],
                    'date_deadline':date.today().strftime('%Y-%m-%d'),
                    'res_id':self.id,
                    'res_model_id':data1.id,
                }
            my_activity = self.env['mail.activity'].create(act_vals)    
        #########################################################
        #self.env.ref('action_your_pipeline').run()
        
        action = self.env['crm.team'].action_your_pipeline()
        return action
        
        # return {
        #      'type': 'ir.actions.act_window',
        #      'res_model': 'crm.lead',
        #      'view_type': 'kanban',
        #      'view_mode': 'kanban',
        #      'target': 'main',
        #      'domain':[['type','=','opportunity']],
        #      'context':{'default_type': 'opportunity','default_user_id': self.env.uid,},
        #      'view_id':False,
        #  }

class LeadProductLine(models.Model):
    _name = 'crm.product_line'

    product_id = fields.Many2one('product.product', string="Товар",
                                 change_default=True, ondelete='restrict', required=True)

    
    name = fields.Text(string='Опис')
    pdt_crm = fields.Many2one('crm.lead')
    product_uom_qty = fields.Float(string='Quantity', default=1.0)
    price_unit = fields.Float(string='Ціна')
    market_price = fields.Float(string='Ціна продажу')
    qty_hand = fields.Integer(string='Наявна кількість')
    uom_id = fields.Many2one('product.uom', 'Од.вимір.')
    child_opportunity=fields.Integer(string='ID of child opportunity')
    stage_name=fields.Char(string='Етап')
    product_stage_id = fields.One2many('crm.lead','stage_id','Стан деталі')
    isSplitted = fields.Boolean(
        string='Splitted',
    )
    #######16.01.2018###########
    
    categ_id = fields.Many2one(
        string='Категорія товару',
        comodel_name='product.category',
        ondelete='set null',
    )

    ######29.01.2018###########
    default_code = fields.Text(string='Код товару')
    

    
    
    @api.onchange('product_id')
    def product_data(self):
        data = self.env['product.template'].search([('name', '=', self.product_id.name)])
        self.name = data.name
        self.price_unit = data.list_price
        self.uom_id = data.uom_id
        self.market_price = data.standard_price
        self.qty_hand = data.qty_available
        self.isSplitted = False
        self.categ_id= data.categ_id
        self.default_code=data.default_code