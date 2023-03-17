# -*- coding: utf-8 -*-
from odoo import models, api, fields


class PartnerMunicipality(models.Model):
    _inherit = 'res.partner'

    municipality = fields.Many2one('l10n_cu_base.res_municipality', 'Municipality',
                                   help='You can associate the municipality')
    rating_id = fields.Many2one('res.partner.rating', 'Partner Rating',
                                help='You can define a rating for legal persons')
    rnccr = fields.Char(string='NIRCC', help="Registration number in the Central Commercial Registry.")
    code_one = fields.Char(string='ONE Code', help="Registration in National Estadistic Office.")
    code_one_full = fields.Char(string='Full ONE Code', help="Full Registration in National Estadistic Office.",
                                compute='_compute_code_one_full',store=True)
    vat = fields.Char(string='TIN', help="Tax Identification Number. "
                                         "Fill it if the company is subjected to taxes. "
                                         "Used by the some of the legal statements.")
    ni = fields.Char('NI', help="Number of Identification")
    npc = fields.Char(string='NPC', help="Permits of Conduction Number")
    organism_id = fields.Many2one('res.organism', 'Organism')
    patner_matriz_id = fields.Many2one('res.partner','Partner Matriz')
    child_ids = fields.One2many('res.partner','patner_matriz_id','Child Partner')

    def _compute_code_one_full(self):
        for c in self:
            code_one_full = ""
            code_one = ""
            organism = ""
            rating = ""
            if c.organism_id:
                organism = str(c.organism_id.code)
            if c.rating_id:
                rating = str(c.rating_id.code)
            if c.code_one:
                code_one = c.code_one
            code_one_full = str(organism) + '.' + str(rating) + '.' + code_one
            c.code_one_full = code_one_full

class PartnerRating(models.Model):
            _description = 'Partner Rating'
            _name = 'res.partner.rating'
            _order = 'name'

            code = fields.Char(string='Rating Code', required=True)
            name = fields.Char(string='Rating Name', required=True, translate=True)
            active = fields.Boolean(default=True,
                                    help="The active field allows you to hide the rating without removing it.")
            dependency = fields.Boolean('Is dependency?', default=False)