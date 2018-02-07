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

class Vendor(models.Model):
    _inherit = 'res.partner'
    
    # my_delivery_time = fields.Integer(
    #     string='Delivery time',
    # )
    
    brand_ids = fields.Many2many(
        string='Бренди',
        comodel_name='product.brand',
        )
    
    vehicle_brand_ids = fields.Many2many(
        string='Марки авто',
        comodel_name='vehicle.brand',
        )
    
    public_categ_ids = fields.Many2many('product.public.category', 
                                        string='Групи деталей',
                                        help="Категорії автомобілів",
                                        domain="[('parent_id', '=', False)]",)
    
    actual_price = fields.Boolean(
        'Ціна актуальна', default=False,
        help="Встановити якщо ціна для постачальника є актуальною.")

    actual_qty = fields.Boolean(
        'Кількість актуальна', default=False,
        help="Встановити якщо кількість для постачальника є актуальною.")
    
    price_list_parsing=fields.Boolean(
        'Прайс-лист', default=False,
        help="Встановити якщо для постачальника потрібно парсити прайс-листи.")

    phone_parsing=fields.Boolean(
        'Телефон', default=False,
        help="Встановити якщо постачальнику потрібно телефонувати.")

    site_parsing=fields.Boolean(
        'Парсер', default=False,
        help="Встановити якщо для постачальнику потрібно парсити сайт.")

