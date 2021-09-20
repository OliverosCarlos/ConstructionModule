from odoo import api, fields, models

class Bim(models.Model):
    _name = 'construction.bim'
    _description = 'bim tools'

    project = fields.Char(string='Proyecto')