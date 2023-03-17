# -*- coding: utf-8 -*-
# from odoo import http


# class L10nCuBase(http.Controller):
#     @http.route('/l10n_cu_base/l10n_cu_base/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/l10n_cu_base/l10n_cu_base/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('l10n_cu_base.listing', {
#             'root': '/l10n_cu_base/l10n_cu_base',
#             'objects': http.request.env['l10n_cu_base.l10n_cu_base'].search([]),
#         })

#     @http.route('/l10n_cu_base/l10n_cu_base/objects/<model("l10n_cu_base.l10n_cu_base"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('l10n_cu_base.object', {
#             'object': obj
#         })
