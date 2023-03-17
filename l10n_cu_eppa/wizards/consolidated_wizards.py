# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from odoo import api, fields, models
import calendar


class ConsolidatedWizards(models.TransientModel):
    _name = 'l10n_cu_eppa.consolidated_wizards'
    _description = 'Consolidated Wizards'

    date = fields.Date('Date', default=datetime.today(),
                       required=True)
    start = fields.Date('Start', default=datetime.today().replace(day=1),
                        required=True)
    end = fields.Date('End',
                      default=datetime.today().replace(
                          day=calendar.monthrange(year=datetime.today().year, month=datetime.today().month)[1]),
                      required=True)

    is_todos_company = fields.Selection([('uno', 'A Company'), ('todos', 'All the Companies')],
                                        'Select Companies',
                                        help='To select Companies', default="todos",
                                        required=True)
    company_id = fields.Many2one('res.company', string='Company',
                                 default=lambda self: self.env.user.company_id,
                                 required=True)

    currency_id = fields.Many2one('res.currency', string='Currency',
                             default=70,
                             required=True)

    def get_report(self):
        data = {
            'ids': self.ids,
            'model': 'report.l10n_cu_eppa.consolidated',
            'form': {
                'date': self.date,
                'start': self.start,
                'end': self.end,
                'is_todos_company': self.is_todos_company,
                'company_id': self.company_id.id,
                'currency_id': self.currency_id.id,
            },
        }
        return self.env.ref('l10n_cu_eppa.action_report_consolidated').report_action(self, data=data)
