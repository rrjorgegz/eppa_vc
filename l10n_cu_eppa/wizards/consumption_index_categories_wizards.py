# -*- coding: utf-8 -*-
import calendar
from datetime import datetime

from odoo import fields, models


class ConsumptionIndexCategoriesWizards(models.TransientModel):
    _name = "l10n_cu_eppa.consumption_index_categories_wizards"
    _description = "Consumption Index for Categories Wizards"

    date = fields.Date("Date", default=datetime.today(), required=True)
    start = fields.Date("Start", default=datetime.today().replace(day=1), required=True)
    end = fields.Date("End", default=datetime.today().replace(day=calendar.monthrange(year=datetime.today().year, month=datetime.today().month)[1]), required=True)

    company_id = fields.Many2one("res.company", string="Company", default=lambda self: self.env.user.company_id, domain=lambda self: [("id", "in", self.env.user.company_ids.ids)], required=True)
    is_todos_prod_unit = fields.Selection(
        [("uno", "A Production Unit"), ("todos", "All the Production Units")], "Select Production Unit", help="To select Production Unit", default="todos", required=True
    )
    prod_unit_id = fields.Many2one("production.unit", string="Production Unit", required=True, default=lambda self: self.env.user.prod_unit_id)

    is_todos = fields.Selection([("uno", "An Ingredient"), ("todos", "All the Ingredients")], "Select Ingredients", help="To select ingredients", default="todos", required=True)
    product_tmpl_id = fields.Many2one(
        "product.template", string="Product", domain=[("purchase_ok", "=", True), ("uom_id", ">", 1), ("active", "=", True), ("type", "=", "product")], help="Product", index=True
    )
    commercialization_id = fields.Many2one("l10n_cu_mrp.commercialization", help="Form of Commercialization", required=True, default=lambda self: self.env.ref("l10n_cu_mrp.MN").id)

    departament_id = fields.Many2one("mrp.department", help="MRP Departament", required=True, default=lambda self: self.env.ref("l10n_cu_mrp.mrp_department_produccion").id)

    is_category = fields.Selection([("uno", "An Category"), ("todos", "All the Category")], "Select Category", help="To select Category", default="todos", required=True)
    category_id = fields.Many2one("product.category", help="Category", index=True)

    def get_report(self):
        data = {
            "ids": self.ids,
            "model": "report.l10n_cu_eppa.consumption_index_categories",
            "form": {
                "date": self.date,
                "start": self.start,
                "end": self.end,
                "company_id": self.company_id.id,
                "is_todos": self.is_todos,
                "product_tmpl_id": self.product_tmpl_id.id,
                "commercialization_id": self.commercialization_id.id,
                "is_category": self.is_category,
                "category_id": self.category_id.id,
                "is_todos_prod_unit": self.is_todos_prod_unit,
                "prod_unit_id": self.prod_unit_id.id,
                "departament_id": self.departament_id.id,
            },
        }
        return self.env.ref("l10n_cu_eppa.action_report_consumption_index_categories").report_action(self, data=data)
