# -*- coding: utf-8 -*-
from odoo import fields, models


class res_company(models.Model):
    _inherit = "res.company"
    _order = "name"

    code = fields.Char(string="Code")
