# -*- coding: utf-8 -*-
from odoo import models,fields,api

from ..utils import vars

statics = vars.Vars

class Calendar(models.Model):
    _name = 'construction.calendar'
    _description = 'Calendarios'

    name = fields.Char(string='Nombre calendario', required=True)
    code = fields.Char( string="Código", required=True)
    calendar = fields.Integer(string="Calendario", help="días del año", required=True)
    sundays = fields.Float( digits=(6,7), string="Domingos", compute="_get_sundays", readonly=True )
    bonus = fields.Integer( string="Aguinaldo", required=True )
    holidays = fields.Integer( string="Días vacaciones", required=True )
    official_holidays = fields.Integer( string='Vacaciones', readonly=True, compute='_get_official_holidays')

    oficial_days_rest_count = fields.Float( digits=(6,2), string='Días oficiales de descanso', readonly=True, compute='_sum_oficial_days_rest_count')
    days_habit_count = fields.Float( digits=(6,2), string='Días por costumbre', readonly=True, compute='_sum_days_habit_count') 

    oficial_days_rest_id = fields.Many2many('construction.oficial_days_rest', string="Dias oficiales de descanso")
    days_habit_id = fields.Many2many('construction.days_habit', string="Días por costumbre")

    @api.depends('calendar')
    def _get_sundays(self):
        for rec in self:
            rec['sundays'] = rec.calendar/7
    
    @api.depends('oficial_days_rest_id')
    def _sum_oficial_days_rest_count(self):
        for rec in self:
            total = 0
            for row in rec.oficial_days_rest_id:
                total += float(row.quantity)
            rec['oficial_days_rest_count'] = total
        rec['oficial_days_rest_count'] = total
    
    @api.depends('days_habit_id')
    def _sum_days_habit_count(self):
        for rec in self:
            total = 0
            for row in rec.days_habit_id:
                total += float(row.quantity)
            rec['days_habit_count'] = total
        rec['days_habit_count'] = total
            

    @api.depends('holidays')
    def _get_official_holidays(self):
        for rec in self:
            rec['official_holidays'] = rec.holidays*0.25
            
class Oficial_days_rest(models.Model):
    _name = 'construction.oficial_days_rest'
    _description = 'Días oficiales de descanso'

    name = fields.Char(string='Nombre del día', required=True)
    code = fields.Char(string='Código', required=True)
    description = fields.Char(string='Descripción')
    day = fields.Date(string='Seleccionar día')
    quantity = fields.Selection( statics.days, string="Cantidad", default='1', help="Seleccionar días")

class Days_habit(models.Model):
    _name = 'construction.days_habit'
    _description = 'Días por costumbre'

    name = fields.Char(string='Nombre del día', required=True)
    code = fields.Char(string='Código', required=True)
    description = fields.Char(string='Descripción')
    day = fields.Date(string='Seleccionar día')
    quantity = fields.Selection( statics.days, string="Cantidad", default='1', help="Seleccionar días")