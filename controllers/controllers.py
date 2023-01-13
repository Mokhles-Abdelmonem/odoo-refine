# -*- coding: utf-8 -*-
# from odoo import http


# class OdooRefine(http.Controller):
#     @http.route('/odoo_refine/odoo_refine', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/odoo_refine/odoo_refine/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('odoo_refine.listing', {
#             'root': '/odoo_refine/odoo_refine',
#             'objects': http.request.env['odoo_refine.odoo_refine'].search([]),
#         })

#     @http.route('/odoo_refine/odoo_refine/objects/<model("odoo_refine.odoo_refine"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('odoo_refine.object', {
#             'object': obj
#         })
