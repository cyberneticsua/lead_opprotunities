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
from odoo.tools.safe_eval import safe_eval

activity_ids_list=[8, 9,10,11]
sales_order_states = [
    'progress', 'manual', 'shipping_exept', 'invoice_except', 'done']

#######15.01.2018################################
#######Фільтри для категорій#####################
class ProductCategoryInLead(models.Model):
    _inherit = 'crm.lead'
    first_level_category = fields.Many2one(
        'product.public.category',
        string='Категорія товару',
        domain="[('parent_id', '=', False)]",
        help='Категорія товару',
        )
    
    second_level_category=fields.Many2one(
        'product.public.category',
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
        'product.public.category',
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
        if (self.first_level_category.name) and (self.env['product.public.category'].search_count([('parent_id','=',self.first_level_category.id)])):
            self.show_second_level_category = True
            self.second_level_category=False
            self.third_level_category=False
            self.second_level_category_id = self.first_level_category.id
        else:
            self.show_second_level_category = False
            self.show_third_level_category=False
            self.second_level_category=False
            self.third_level_category=False

    # @api.one
    @api.onchange('second_level_category')
    def _get_third_level_value(self):
        if (self.second_level_category.name)  and (self.env['product.public.category'].search_count([('parent_id','=',self.second_level_category.id)])):
            self.show_third_level_category = True
            self.third_level_category=False
            self.third_level_category_id = self.second_level_category.id
        else:
            self.show_third_level_category = False
            self.third_level_category=False    

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
    @api.model
    def get_opportunity_view(self, view_title):
        action = self.env.ref('crm.crm_lead_opportunities_tree_view').read()[0]
        user_team_id = self.env.user.sale_team_id.id
        if not user_team_id:
            user_team_id = self.search([], limit=1).id
            action['help'] = """<p class='oe_view_nocontent_create'>Click here to add new opportunities</p><p>
    Looks like you are not a member of a sales team. You should add yourself
    as a member of one of the sales team.
</p>"""
            if user_team_id:
                action['help'] += "<p>As you don't belong to any sales team, Odoo opens the first one by default.</p>"

        action_context = safe_eval(action['context'], {'uid': self.env.uid})
        if user_team_id:
            action_context['default_team_id'] = user_team_id
        
        child_ids = []
        for data in self.pdt_line:
            if data.child_opportunity:
                child_ids.append(data.child_opportunity)
        action['domain'] = [
        #         # ('state', 'in', order_states),
        #         # ('partner_id', 'in', partner_ids),
                ('id', 'in', child_ids),
            ]
        action['name']=view_title
        tree_view_id = self.env.ref('crm.crm_case_tree_view_oppor').id
        form_view_id = self.env.ref('crm.crm_case_form_view_oppor').id
        kanb_view_id = self.env.ref('crm.crm_case_kanban_view_leads').id
        action['views'] = [
                [kanb_view_id, 'kanban'],
                [tree_view_id, 'tree'],
                [form_view_id, 'form'],
                [False, 'graph'],
                [False, 'calendar'],
                [False, 'pivot']
            ]
        action['context'] = action_context
        return action
    
    
    ###########################################################################################
        # partner_ids = self.partner_id.id
        # child_ids = []
        # for data in self.pdt_line:
        #     if data.child_opportunity:
        #         child_ids.append(data.child_opportunity)
        
        # opportunities = self.env['crm.lead'].search([
        #     # ('partner_id', 'in', partner_ids),
        #     ('id', 'in', child_ids),
        # ])
        # res = {
        #     'name': view_title,
        #     'type': 'ir.actions.act_window',
        #     'res_model': 'crm.lead',
        #     'view_type': 'form',
        # }
        # if len(opportunities) == 1:
        #     res['res_id'] = opportunities[0].id
        #     res['view_mode'] = 'form'
        # else:
        #     res['domain'] = [
        #         # ('state', 'in', order_states),
        #         # ('partner_id', 'in', partner_ids),
        #         ('id', 'in', child_ids),
        #     ]
        #     res['view_mode'] = 'kanban,tree,form'
        # return res
    ####################################################################

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
                if data.default_code:
                    st_id = 2
                    my_activity = self.env['mail.activity.type'].search([('name', '=', 'Запланувати пошук, парсити')])
                else:
                    st_id = 1
                    my_activity = self.env['mail.activity.type'].search([('name', '=', 'Ідентифікувати')])
                vals = {
                'partner_id': self.partner_id.id,
                'user_id': self.env.uid,
                'name': data.name,
                'stage_id':st_id,
                'type':'opportunity',
                'priority':self.priority,
                'vehicle_type_id':self.vehicle_type_id.id,
                'vehicle_model_id':self.vehicle_model_id.id,
                'vehicle_brand_id':self.vehicle_brand_id.id,
                #####################################################
                #############Змінити час№№№№№№№
                'date_deadline':date.today().strftime('%Y-%m-%d'),
                }
                new_opportunity = self.env['crm.lead'].create(vals)
                new_opportunity.tag_ids=[(6,0,self.tag_ids.ids)]
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
                            'product_brand':data.product_brand,
                            'product_categ':data.product_categ,
                            'isSplitted': True,
                            }
                pdt_line.create(pdt_value)

                if (st_id==2):
                    data_ww = self.env['product.product'].search([('id', '=', data.product_id.id)])
                    self.find_alternative_products({'prod_id':data_ww.product_tmpl_id.id,'new_oppor_id':new_opportunity.id})

                ###############Creating activity###############
                data1 = self.env['ir.model'].search([('model', '=', 'crm.lead')])
                
                act_vals={
                    'activity_type_id': my_activity.id,
                    'date_deadline':date.today().strftime('%Y-%m-%d'),
                    'res_id':new_opportunity.id,
                    'res_model_id':data1.id,
                }
                my_activity = self.env['mail.activity'].create(act_vals)

                #Setting stage stage#################
                stage_name = self.env['crm.stage'].search([('id', '=', new_opportunity.stage_id.id)])
                # raise Warning (int(new_opportunity.id))
                data.write ({'stage_name':stage_name.name,'product_stage_id':new_opportunity.stage_id,'child_opportunity':int(new_opportunity.id)})
        self.pdt_line.write({'isSplitted':True})
        
        if self.description:
            data1 = self.env['ir.model'].search([('model', '=', 'crm.lead')])
            my_activity = self.env['mail.activity.type'].search([('name', '=', 'Уточнити параметри авто')])
            act_vals={
                    'activity_type_id':my_activity.id,
                    'date_deadline':date.today().strftime('%Y-%m-%d'),
                    'res_id':self.id,
                    'res_model_id':data1.id,
                }
            my_activity = self.env['mail.activity'].create(act_vals)    
        #########################################################
        #self.env.ref('action_your_pipeline').run()
        return self.get_opportunity_view("Список деталей")
        # action = self.env['crm.team'].action_your_pipeline()
        # return action
        
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
                                 change_default=True, ondelete='restrict', required=True,) 
                                #  domain= lambda self: self._get_product_domain())
    name = fields.Text(string='Опис')
    pdt_crm = fields.Many2one('crm.lead', string='Діалог')
    product_uom_qty = fields.Float(string='Кількість', default=1.0)
    price_unit = fields.Float(string='Ціна')
    market_price = fields.Float(string='Ціна продажу')
    qty_hand = fields.Integer(string='Наявна кількість')
    child_opportunity=fields.Integer(string='ID of child opportunity')
    stage_name=fields.Char(string='Етап')
    product_stage_id = fields.One2many('crm.lead','stage_id','Стан деталі')
    isSplitted = fields.Boolean(
        string='Splitted',
    )
    #######16.01.2018###########
    # categ_id = fields.Many2one(
    #     string='Категорія товару',
    #     comodel_name='product.public.category',
    #     ondelete='set null',
    # )
    ######29.01.2018###########
    default_code = fields.Text(string='Код товару')

    product_brand = fields.Char(
        string='Бренд',
        help='Бренд товару'
    )
    
    product_categ=fields.Char(
        string='Категорія',
        help='Категорія товару'
    )
    # @api.model
    @api.onchange('product_id')
    def _get_product_domain(self):
        res = {}
        my_domain=[]
        if (self.pdt_crm.third_level_category.id):
            my_domain.append(('public_categ_ids','child_of',self.pdt_crm.third_level_category.id))
        elif (self.pdt_crm.second_level_category.id):
            my_domain.append(('public_categ_ids','child_of',self.pdt_crm.second_level_category.id))
        elif (self.pdt_crm.first_level_category.id):
            my_domain.append(('public_categ_ids','child_of',self.pdt_crm.first_level_category.id))
        
        res['domain']={'product_id':my_domain}
        # raise Warning(self.pdt_crm.third_level_category)
        return res

    @api.onchange('product_id')
    def product_data(self):
        data = self.env['product.template'].search([('name', '=', self.product_id.name)])
        # if (not(self.pdt_crm.second_level_category.id)):
        #     raise Warning(self.pdt_crm.second_level_category.id) 
        # else:
        self.name = data.name
        self.price_unit = data.list_price
        self.uom_id = data.uom_id
        self.market_price = data.standard_price
        self.qty_hand = data.qty_available
        self.isSplitted = False
        # self.categ_id= data.public_categ_ids
        self.default_code=self.product_id.default_code
        self.product_brand=data.product_brand_id.name
        if (self.pdt_crm.third_level_category.id):
            self.product_categ=self.pdt_crm.third_level_category.name
        elif (self.pdt_crm.second_level_category.id):
            self.product_categ=self.pdt_crm.second_level_category.name
        elif (self.pdt_crm.first_level_category.id):
            self.product_categ=self.pdt_crm.first_level_category.name
        
    
        