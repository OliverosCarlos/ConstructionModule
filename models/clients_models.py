# -*- coding: utf-8 -*-
from odoo import models,fields,api

from ..utils import vars

statics = vars.Vars

class Construction_client(models.Model):
    _name = 'construction.construction_client'
    _description = 'Cliente especifico para construcción'

    name = fields.Char(string='Nombre')

class Address(models.Model):
    _name = 'construction.address'
    _description = 'Dirección'

    name = fields.Char(string='Colonia')
    street = fields.Char(string='Calle')
    int_number = fields.Integer(string='No. Interior')
    ext_number = fields.Integer(string='No. Exterior')
    between1 = fields.Char(string='Entre calle 1')
    between2 = fields.Char(string='Entre calle 2')
    references = fields.Char(string='Referencias')
    zipcode = fields.Char(string='Código postal')
    state = fields.Many2one('res.country.state', string='Estado', required=True)
    municipality = fields.Char(string='Municipio')
    locality = fields.Char(string='Localidad')
    country = fields.Many2one('res.country', string='País', required=True)