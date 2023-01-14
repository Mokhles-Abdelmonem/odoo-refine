from odoo import models, fields, api



class Test(models.Model):
    _name = "test"
    _description = "Refine Refine test data"
    Country_territoryofasylum_residence = fields.Char(string="Country_territoryofasylum_residence", required=True, tracking=True)
    Year = fields.Char(string="Year", required=True, tracking=True)
    Month = fields.Char(string="Month", required=True, tracking=True)
    Value = fields.Char(string="Value", required=True, tracking=True)
    Date = fields.Char(string="Date", required=True, tracking=True)
