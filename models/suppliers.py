from odoo import api, fields, models


class Supplier(models.Model):
    _name = 'construction.supplier'
    _description = 'Proveedores'

    code = fields.Char(string='Código')
    name = fields.Char(string='Nombre')
    description = fields.Char(string='Descripción')
    web_site = fields.Char(string='Sitio web')
    image = fields.Image( string="Imagen", help="Imagen del proveedor")
    phone = fields.Char(string='Telefono')
    email = fields.Char(string='Correo')

    #ADDRESS
    street_1 = fields.Char(string='Calle 1')
    street_2 = fields.Char(string='Calle 2')
    int_number = fields.Char(string='Número interio')
    ext_number = fields.Char(string='Número exterior')
    state = fields.Char(string='Estado')
    city = fields.Char(string='Ciudad')
    country = fields.Char(string='País')
    neighborhood = fields.Char(string='Colonia')
    zip_supplier = fields.Char(string='Código postal')
