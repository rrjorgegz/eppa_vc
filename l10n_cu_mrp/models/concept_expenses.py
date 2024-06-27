# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ConceptExpenses(models.Model):
    _name = "l10n_cu_mrp.concept_expenses"
    _description = "Concept of Expenses"

    name = fields.Char("Reference", store=True, compute="get_name", help="Name of the Worker s Wage")
    company_id = fields.Many2one("res.company", string="Companies", default=lambda self: self.env.company, required=True)
    mrp_bom_id = fields.Many2one("mrp.bom", string="Bill of Material", domain="[('company_id', '=', company_id)]", required=True)
    product_tmpl_id = fields.Many2one("product.template", store=True, string="Product Template", related="mrp_bom_id.product_tmpl_id")
    salario = fields.Many2one("l10n_cu_mrp.wage_worker", string="Wage of the Worker", domain="[('product_tmpl_id', '=', product_tmpl_id)]", required=True)
    currency_id = fields.Many2one("res.currency", string="Currency", store=True, related="mrp_bom_id.forma_c.currency_id", groups="base.group_multi_currency")
    materias_p = fields.Float(string="Matter Prevails and Materials", help="Matter Prevails and Materials (MP)", related="mrp_bom_id.total", digits="Concept of Expenses", default=0, store=True)
    materias_pf = fields.Float(
        store=True, compute="get_materias_pf", string="Matter Prevails and Fundamintal Materials", help="Matter Prevails and Fundamintal Materials (MP)", default=0, digits="Concept of Expenses"
    )
    lubicante_mp = fields.Float(string="Fuels and Lubricant", help="Fuels and Lubricant (MP)", digits="Concept of Expenses", store=True, compute="get_lubicante_mp", default=0)
    energia_mp = fields.Float(string="Electric Power", default=0, help="Electric Power (MP)", digits="Concept of Expenses", store=True, compute="get_energia_mp")
    agua_mp = fields.Float(string="Water", help="Water (MP)", default=0, digits="Concept of Expenses", store=True, compute="get_agua_mp")
    subtotal_ge = fields.Float(string="Subtotal (Expenses of Elaboration)", store=True, compute="get_subtotal_ge", help="Subtotal (Expenses of Elaboration)", digits="Concept of Expenses", default=0)
    otros_gd = fields.Float(string="Other Direct Expenses", store=True, compute="get_otros_gd", help="Other Direct Expenses (GD)", default=0, digits="Concept of Expenses")
    dep_gd = fields.Float(string="Depreciation (GD)", help="Depreciation (GD)", store=True, compute="get_dep_gd", default=0, digits="Concept of Expenses")
    arr_equi_gd = fields.Float(string="Lease of Teams (GD)", help="Lease of Teams (GD)", store=True, compute="get_arr_equi_gd", digits="Concept of Expenses", default=0)
    rop_cal_gd = fields.Float(
        string="Clothes and Footwear (Direct workers) (GD)", store=True, compute="get_rop_cal_gd", help="Clothes and Footwear (Direct workers) (GD)", default=0, digits="Concept of Expenses"
    )
    otro_gd = fields.Float(string="Others (GD)", help="Others (GD)", default=0, store=True, compute="get_otro_gd", digits="Concept of Expenses")
    gasto_ft = fields.Float(string="Expenses of Force of Work (GD)", store=True, compute="get_gasto_ft", help="Expenses of Force of Work (FT)", digits="Concept of Expenses", default=0)
    sal_ft = fields.Float(string="Wages (FT)", help="Wages (FT)", store=True, compute="get_sal_ft", default=0, digits="Concept of Expenses")
    vac_ft = fields.Float(string="Vacations (FT)", help="Vacations (FT)", store=True, compute="get_vac_ft", default=0, digits="Concept of Expenses")
    est_pc = fields.Float(string="Stimulation in Convertible Pesos", help="Stimulation in Convertible Pesos", default=0, digits="Concept of Expenses")
    gastos_ip = fields.Float(string="Indirect Expenses of Production (IP)", store=True, compute="get_gastos_ip", help="Indirect Expenses of Production (IP)", default=0, digits="Concept of Expenses")
    depre_ip = fields.Float(string="Depreciation (IP)", store=True, compute="get_depre_ip", help="Depreciation (IP)", default=0, digits="Concept of Expenses")
    mant_rep_ip = fields.Float(string="Maintinance and Repair (IP)", store=True, compute="get_mant_rep_ip", help="Maintinance and Repair (IP)", digits="Concept of Expenses", default=0)
    otros_ip = fields.Float(string="Others (IP)", help="Others (IP)", default=0, store=True, compute="get_otros_ip", digits="Concept of Expenses")
    gastos_ga = fields.Float(
        string="General Expenses and of Administration (GA)",
        digits="Concept of Expenses",
        help="General Expenses and of Administration (GA)",
        default=0,
        required=True,
        store=True,
        compute="get_gastos_ga",
    )
    com_lubi_ga = fields.Float(string="Fuels and Lubricant (GA)", digits="Concept of Expenses", store=True, compute="get_com_lubi_ga", help="Fuels and Lubricant (GA)", default=0)
    ene_ele_ga = fields.Float(string="Electric Power (GA)", digits="Concept of Expenses", help="Electric Power (GA)", default=0, store=True, compute="get_ene_ele_ga")
    dep_ga = fields.Float(string="Depreciation (GA)", digits="Concept of Expenses", store=True, compute="get_dep_ga", help="Depreciation (GA)", default=0)
    rop_cal_ga = fields.Float(string="Clothes and Footwear (GA)", digits="Concept of Expenses", store=True, compute="get_rop_cal_ga", help="Clothes and Footwear (GA)", default=0)
    alimentos_ga = fields.Float(string="Foods (GA)", digits="Concept of Expenses", store=True, compute="get_alimentos_ga", help="Foods (GA)", default=0)
    otros_ga = fields.Float(string="Others (GA)", digits="Concept of Expenses", store=True, compute="get_otros_ga", help="Others (GA)", default=0)
    gastos_dv = fields.Float(
        string="Expenses of Distribution and Sales (GA)", digits="Concept of Expenses", store=True, compute="get_gastos_dv", help="Expenses of Distribution and Sales (DV)", default=0
    )
    com_lub_dv = fields.Float(string="Fuels and Lubricant (DV)", digits="Concept of Expenses", store=True, compute="get_com_lub_dv", help="Fuels and Lubricant (DV)", default=0)
    ene_ele_dv = fields.Float(string="Electric Power (DV)", digits="Concept of Expenses", store=True, compute="get_ene_ele_dv", help="Electric Power (DV)", default=0)
    dep_dv = fields.Float(string="Depreciation (DV)", digits="Concept of Expenses", store=True, compute="get_dep_dv", help="Depreciation (DV)", default=0)
    rop_cal_dv = fields.Float(string="Clothes and Footwear (DV)", digits="Concept of Expenses", store=True, compute="get_rop_cal_dv", help="Clothes and Footwear (DV)", default=0)
    otro_dv = fields.Float(string="Others (DV)", help="Others (DV)", store=True, compute="get_otro_dv", digits="Concept of Expenses", default=0)
    gastos_ba = fields.Float(string="Expenses Bancarios", help="Expenses Bancarios", digits="Concept of Expenses", default=0)
    gastos_tc = fields.Float(string="Expenses Totals o Cost of Production", digits="Concept of Expenses", store=True, compute="get_gastos_tc", help="Expenses Totals o Cost of Production", default=0)
    margen_ub = fields.Float(
        string="Margin Utility s/ it Bases Authorized %", store=True, compute="get_margen_ub", help="Margin Utility s/ it Bases Authorized % (UB)", digits="Concept of Expenses", default=0
    )
    impuesto_ub = fields.Float(string="Imposed Use of the Force of Work", digits="Concept of Expenses", store=True, compute="get_impuesto_ub", help="Imposed Use of the Force of Work (UB)", default=0)
    con_ub = fields.Float(string="Contribution to the Social Security", digits="Concept of Expenses", store=True, compute="get_con_ub", help="Contribution to the Social Security (UB)", default=0)
    precio = fields.Float(string="Price: ", help="Price: ", default=0, store=True, compute="get_precio", digits="Concept of Expenses")
    precio1 = fields.Float(string="Price / 100", help="Price / 100", default=0, store=True, compute="get_precio1", digits="Concept of Expenses", required=True)
    coef_dep_gd = fields.Float(string="Coef D GD", digits="Concept of Expenses", help="Coefficient of Depreciation of Direct Expenses", default=0)
    coef_arr_equi_gd = fields.Float(string="Coef A GD", digits="Concept of Expenses", help="Coefficient of Lease of Teams (GD) of Direct Expenses", default=0)
    coef_rop_cal_gd = fields.Float(string="Coef R&C GD", digits="Concept of Expenses", help="Coefficient of Clothes and Footwear of Direct Expenses", default=0.3)
    coef_otro_gd = fields.Float(string="Coef O GD", digits="Concept of Expenses", help="Coefficient of Others of Direct Expenses", default=0.4)
    coef_depre_ip = fields.Float(string="Coef D GI", help="Coefficient of Depreciation of Expenses Indirectos", digits="Concept of Expenses", default=0)
    coef_mant_rep_ip = fields.Float(string="Coef M&R GI", help="Coefficient of Maintinance and Repair of Expenses Indirectos", digits="Concept of Expenses", default=0)
    coef_otros_ip = fields.Float(string="Coef O GI ", help="Coefficient of Others of Expenses Indirectos", digits="Concept of Expenses", default=0)
    coef_rop_cal_ga = fields.Float(string="Coef R&C GA", digits="Concept of Expenses", help="Coefficient of Clothes and Footwear of General Expenses and of Administration", default=0)
    coef_alimentos_ga = fields.Float(string="Coef A GA", help="Coefficient of Foods of General Expenses and of Administration", digits="Concept of Expenses", default=0)
    coef_com_lubi_ga = fields.Float(string="Coef CL D&A", digits="Concept of Expenses", help="Coefficient of Fuels and Lubricant in General Expenses and of Administration", default=0)
    coef_ene_ele_ga = fields.Float(string="Coef EE D&A", digits="Concept of Expenses", help="Coefficient of Electric Power in General Expenses and of Administration", default=0)
    coef_dep_ga = fields.Float(string="Coef D D&A", default=0, digits="Concept of Expenses", help="Coefficient of depreciation in General Expenses and of Administration")
    coef_otros_ga = fields.Float(string="Coef O D&A", digits="Concept of Expenses", help="Coefficient of Others in General Expenses and of Administration", default=0)
    coef_com_lub_dv = fields.Float(string="Coef CL D&V", default=0, digits="Concept of Expenses", help="Coefficient of Fuels and Lubricant in Expenses of Distribution and Sales")
    coef_ene_ele_dv = fields.Float(string="Coef EE D&V", digits="Concept of Expenses", help="Coefficient of Electric Power  in Expenses of Distribution and Sales", default=0)
    coef_rop_cal_dv = fields.Float(string="Coef R&C D&V", digits="Concept of Expenses", help="Coefficient of Clothes and Footwear of Depreciation  in Expenses of Distribution and Sales", default=0)
    coef_dep_dv = fields.Float(string="Coef D D&V", digits="Concept of Expenses", help="Coefficient of Depreciation  in Expenses of Distribution and Sales", default=0)
    coef_otro_dv = fields.Float(string="Coef O D&V", digits="Concept of Expenses", help="Coefficient of Others  in Expenses of Distribution and Sales", default=0)
    coef = fields.Float(string="Coef Total", digits="Concept of Expenses", help="add of those Coefficient ", store=True, compute="add_Coefficients", default=0)

    confeccionado_por = fields.Many2one("hr.employee", string="Made for")
    aprobado_por = fields.Many2one("hr.employee", string="Approved for")
    revisado_por = fields.Many2one("hr.employee", string="Revised for")

    # _sql_constraints = [
    #     ('check_coef', 'CHECK(coef >= 0.0 and coef <= 2.5)',
    #      'The Total Coefficient  of an Concept of Expenses should be between 0.0 and 2.5')
    # ]

    @api.depends("product_tmpl_id")
    def get_name(self):
        self.name = "CG/"
        if self.id:
            self.name = "CG/" + str(self.id)
        return

    @api.depends("mrp_bom_id")
    def get_lubicante_mp(self):
        aux = 0
        for materiales in self.mrp_bom_id.bom_line_ids:
            if materiales.product_tmpl_id.categ_id.name == "Combustibles y Lubricantes" or materiales.product_tmpl_id.categ_id.name == "Fuels and Lubricant":
                a = 0
                b = 0
                a = self.cantidad_productos(qty=materiales.product_qty, uom=materiales.product_uom_id, prd=1)
                b = self.convert_cantidad_productos(qty=a, uom=materiales.product_tmpl_id.uom_id)
                aux = b * materiales.product_id.standard_price
        self.lubicante_mp = aux
        return

    @api.depends("mrp_bom_id")
    def get_energia_mp(self):
        aux = 0
        for materiales in self.mrp_bom_id.bom_line_ids:
            if materiales.product_tmpl_id.categ_id.name == "Energía Eléctrica" or materiales.product_tmpl_id.categ_id.name == "Electric Power":
                # aux = materiales.product_qty * materiales.product_id.standard_price
                a = 0
                b = 0
                a = self.cantidad_productos(qty=materiales.product_qty, uom=materiales.product_uom_id, prd=1)
                b = self.convert_cantidad_productos(qty=a, uom=materiales.product_tmpl_id.uom_id)
                aux = b * materiales.product_id.standard_price
        self.energia_mp = aux
        return

    @api.depends("mrp_bom_id")
    def get_agua_mp(self):
        aux = 0
        for materiales in self.mrp_bom_id.bom_line_ids:
            if materiales.product_tmpl_id.categ_id.name == "Agua" or materiales.product_tmpl_id.categ_id.name == "Water":
                a = 0
                b = 0
                a = self.cantidad_productos(qty=materiales.product_qty, uom=materiales.product_uom_id, prd=1)
                b = self.convert_cantidad_productos(qty=a, uom=materiales.product_tmpl_id.uom_id)
                aux = b * materiales.product_id.standard_price
                # aux = materiales.product_qty * materiales.product_id.standard_price
        self.agua_mp = aux
        return

    @api.depends("materias_p", "lubicante_mp", "energia_mp", "agua_mp")
    def get_materias_pf(self):
        aux = 0
        aux = self.materias_p - self.lubicante_mp - self.energia_mp - self.agua_mp
        self.materias_pf = aux
        return

    @api.depends("dep_gd", "arr_equi_gd", "rop_cal_gd", "otro_gd")
    def get_otros_gd(self):
        aux = 0
        aux = self.dep_gd + self.arr_equi_gd + self.rop_cal_gd + self.otro_gd
        self.otros_gd = aux
        return

    @api.depends("sal_ft", "coef_dep_gd")
    def get_dep_gd(self):
        aux = 0
        aux = self.sal_ft * self.coef_dep_gd
        self.dep_gd = aux
        return

    @api.depends("sal_ft", "coef_arr_equi_gd")
    def get_arr_equi_gd(self):
        aux = 0
        aux = self.sal_ft * self.coef_arr_equi_gd
        self.arr_equi_gd = aux
        return

    @api.depends("sal_ft", "coef_rop_cal_gd")
    def get_rop_cal_gd(self):
        aux = 0
        aux = self.sal_ft * self.coef_rop_cal_gd
        self.rop_cal_gd = aux
        return

    @api.depends("sal_ft", "coef_otro_gd")
    def get_otro_gd(self):
        aux = 0
        aux = self.sal_ft * self.coef_otro_gd
        self.otro_gd = aux
        return

    @api.depends("sal_ft", "vac_ft")
    def get_gasto_ft(self):
        aux = 0
        aux = self.sal_ft + self.vac_ft
        self.gasto_ft = aux
        return

    @api.depends("salario")
    def get_sal_ft(self):
        aux = 0
        aux = self.salario.salario_basico
        self.sal_ft = aux
        return

    @api.depends("sal_ft")
    def get_vac_ft(self):
        aux = 0
        aux = self.sal_ft * 0.0909
        self.vac_ft = aux
        return

    @api.depends("otros_gd", "gasto_ft", "gastos_ip", "gastos_ga", "gastos_dv", "gastos_ba")
    def get_subtotal_ge(self):
        aux = 0
        aux = self.otros_gd + self.gasto_ft + self.gastos_ip + self.gastos_ga + self.gastos_dv + self.gastos_ba
        self.subtotal_ge = aux
        return

    @api.depends("depre_ip", "mant_rep_ip", "otros_ip")
    def get_gastos_ip(self):
        aux = 0
        aux = self.depre_ip + self.mant_rep_ip + self.otros_ip
        self.gastos_ip = aux
        return

    @api.depends("sal_ft", "coef_depre_ip")
    def get_depre_ip(self):
        aux = 0
        if self.coef_depre_ip > 0:
            aux = self.sal_ft * self.coef_depre_ip
        self.depre_ip = aux
        return

    @api.depends("com_lubi_ga", "ene_ele_ga", "dep_ga", "rop_cal_ga", "alimentos_ga", "otros_ga")
    def get_gastos_ga(self):
        aux = 0
        aux = self.com_lubi_ga + self.ene_ele_ga + self.dep_ga + self.rop_cal_ga + self.alimentos_ga + self.otros_ga
        self.gastos_ga = aux
        return

    @api.depends("sal_ft", "coef_mant_rep_ip")
    def get_mant_rep_ip(self):
        aux = 0
        if self.coef_mant_rep_ip > 0:
            aux = self.sal_ft * self.coef_mant_rep_ip
        self.mant_rep_ip = aux
        return

    @api.depends("otros_ip", "coef_otros_ip")
    def get_otros_ip(self):
        aux = 0
        if self.coef_otros_ip > 0:
            aux = self.sal_ft * self.coef_otros_ip
        self.otros_ip = aux
        return

    @api.depends("sal_ft", "coef_alimentos_ga")
    def get_alimentos_ga(self):
        aux = 0
        if self.coef_alimentos_ga > 0:
            aux = self.sal_ft * self.coef_alimentos_ga
        self.alimentos_ga = aux
        return

    @api.depends("sal_ft", "coef_rop_cal_ga")
    def get_rop_cal_ga(self):
        aux = 0
        if self.coef_rop_cal_ga > 0:
            aux = self.sal_ft * self.coef_rop_cal_ga
        self.rop_cal_ga = aux
        return

    @api.depends("sal_ft", "coef_ene_ele_dv")
    def get_ene_ele_dv(self):
        aux = 0
        if self.coef_ene_ele_dv > 0:
            aux = self.sal_ft * self.coef_ene_ele_dv
        self.ene_ele_dv = aux
        return

    @api.depends("sal_ft", "coef_rop_cal_dv")
    def get_rop_cal_dv(self):
        aux = 0
        if self.coef_rop_cal_dv > 0:
            aux = self.sal_ft * self.coef_rop_cal_dv
        self.rop_cal_dv = aux
        return

    @api.depends("sal_ft", "coef_com_lubi_ga")
    def get_com_lubi_ga(self):
        aux = 0
        if self.coef_com_lubi_ga > 0:
            aux = self.sal_ft * self.coef_com_lubi_ga
        self.com_lubi_ga = aux
        return

    @api.depends("sal_ft", "coef_ene_ele_ga")
    def get_ene_ele_ga(self):
        aux = 0
        if self.coef_ene_ele_ga > 0:
            aux = self.sal_ft * self.coef_ene_ele_ga
        self.ene_ele_ga = aux
        return

    @api.depends("sal_ft", "coef_dep_ga")
    def get_dep_ga(self):
        aux = 0
        if self.coef_dep_ga:
            aux = self.sal_ft * self.coef_dep_ga
        self.dep_ga = aux
        return

    @api.depends("sal_ft", "coef_otros_ga")
    def get_otros_ga(self):
        aux = 0
        if self.coef_otros_ga > 0:
            aux = self.sal_ft * self.coef_otros_ga
        self.otros_ga = aux
        return

    @api.depends("com_lub_dv", "ene_ele_dv", "dep_dv", "rop_cal_dv", "otro_dv")
    def get_gastos_dv(self):
        aux = 0
        aux = self.com_lub_dv + self.ene_ele_dv + self.dep_dv + self.rop_cal_dv + self.otro_dv
        self.gastos_dv = aux
        return

    @api.depends("sal_ft", "coef_com_lub_dv")
    def get_com_lub_dv(self):
        aux = 0
        if self.coef_com_lub_dv > 0:
            aux = self.sal_ft * self.coef_com_lub_dv
        self.com_lub_dv = aux
        return

    @api.depends("sal_ft", "coef_dep_dv")
    def get_dep_dv(self):
        aux = 0
        if self.coef_dep_dv > 0:
            aux = self.sal_ft * self.coef_dep_dv
        self.dep_dv = aux
        return

    @api.depends("sal_ft", "coef_otro_dv")
    def get_otro_dv(self):
        aux = 0
        if self.coef_otro_dv > 0:
            aux = self.sal_ft * self.coef_otro_dv
        self.otro_dv = aux
        return

    @api.depends("materias_p", "subtotal_ge")
    def get_gastos_tc(self):
        aux = 0
        if self.materias_p and self.subtotal_ge:
            aux = self.materias_p + self.subtotal_ge
        self.gastos_tc = aux
        return

    @api.depends("subtotal_ge")
    def get_margen_ub(self):
        aux = 0
        aux = self.subtotal_ge * 0.2
        self.margen_ub = aux
        return

    @api.depends("gasto_ft")
    def get_impuesto_ub(self):
        aux = 0
        aux = self.gasto_ft * 0.05
        self.impuesto_ub = aux
        return

    @api.depends("gasto_ft")
    def get_con_ub(self):
        aux = 0
        aux = self.gasto_ft * 0.125
        self.con_ub = aux
        return

    @api.depends("gastos_ba", "gastos_tc", "margen_ub", "impuesto_ub", "con_ub")
    def get_precio(self):
        aux = 0
        aux = self.gastos_ba + self.gastos_tc + self.margen_ub + self.impuesto_ub + self.con_ub
        self.precio = aux
        return

    @api.depends("precio")
    def get_precio1(self):
        aux = 0
        aux = self.precio / 100
        self.precio1 = aux
        return

    @api.depends(
        "coef_mant_rep_ip",
        "coef_otros_ip",
        "coef_depre_ip",
        "coef_alimentos_ga",
        "coef_dep_ga",
        "coef_com_lubi_ga",
        "coef_rop_cal_ga",
        "coef_otros_ga",
        "ene_ele_ga",
        "coef_otro_dv",
        "coef_ene_ele_dv",
        "coef_rop_cal_dv",
        "coef_dep_dv",
        "coef_com_lub_dv",
    )
    def add_Coefficients(self):
        self.coef = (
            self.coef_depre_ip
            + self.coef_otros_ip
            + self.coef_mant_rep_ip
            + self.coef_com_lubi_ga
            + self.coef_ene_ele_ga
            + self.coef_dep_ga
            + self.coef_alimentos_ga
            + self.coef_rop_cal_ga
            + self.coef_otros_ga
            + self.coef_com_lub_dv
            + self.coef_ene_ele_dv
            + self.coef_dep_dv
            + self.coef_rop_cal_dv
            + self.coef_otro_dv
        )
        return

    def cantidad_productos(self, qty, uom, prd):
        aux = 0
        if uom.uom_type == "bigger":
            aux = qty * uom.factor_inv
        else:
            if qty > 0 and uom.factor > 0:
                aux = qty / uom.factor
        if prd > 0:
            aux = aux * prd
        return aux

    def convert_cantidad_productos(self, qty, uom):
        aux = 0
        if uom.uom_type == "bigger" and qty > 0 and uom.factor > 0:
            aux = qty / uom.factor_inv
        else:
            aux = qty * uom.factor
        return aux
