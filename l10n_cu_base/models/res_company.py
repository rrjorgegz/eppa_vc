# -*- coding: utf-8 -*-
from odoo import models, fields, api

class res_company(models.Model):
    _inherit = 'res.company'
    _order = 'name'

    code = fields.Char(string='Code')

