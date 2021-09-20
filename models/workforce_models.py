# -*- coding: utf-8 -*-

from odoo import api, fields, models

from ..utils import vars

statics = vars.Vars

class Workforces(models.Model):
    _name = 'construction.workforce'
    _description = 'Modulo para catalogo de mano de obra'

    name = fields.Char(string='Name' )
    code = fields.Char(string='Código' )
    w_unit = fields.Many2one( 'construction.unit', string='Unidad', domain="[('magnitude','=','tiempo')]", ondelete='set null', index=True, copy=False)
    performance = fields.Float( digits=(6,4), string='Rendimiento' )
    cost = fields.Float( digits=(6,4), string='Costo', compute="_get_total_workers_cost", store=True )
    coin = fields.Selection( statics.coins, string="Moneda", default='0', help="Seleccionar una moneda")

    team_lines = fields.One2many('construction.workforce_team','workforce_id', string='Cuadrilla')
    basic_id = fields.Many2one('construction.basic', string='Concepto/Básico',  ondelete='cascade', index=True, copy=False)


    currency_id = fields.Many2one('res.currency', compute='_compute_currency')
    
    @api.depends('coin')
    def _compute_currency(self):
        self.currency_id = self.env.ref('base.main_company').currency_id

    @api.depends('team_lines')
    def _get_total_workers_cost(self):
        for rec in self:
            total = 0
            for row in rec.team_lines:
                total += row.subtotal
            rec['cost'] = total

class Stage_workforce_lines(models.Model):
    _name = 'construction.stage_workforce_lines'
    _description = 'Partida mano de obra'

    quantity = fields.Float( string='Cantidad', default='1' )
    w_import = fields.Float( digits=(6,4), string='Importe', compute='_get_subtotal', store=True)

    stage_id = fields.Many2one('construction.stage', string='Partida',  ondelete='cascade', index=True, copy=False)
    workforce_id = fields.Many2one('construction.workforce', string='Cuadrilla',  ondelete='cascade', index=True, copy=False)
    workforce_cost = fields.Float( related='workforce_id.cost', string='Costo')
    workforce_unit = fields.Many2one( related='workforce_id.w_unit', string='Unidad')

    @api.depends('quantity','workforce_cost')
    def _get_subtotal(self):
        for rec in self:
            rec['w_import'] = rec.quantity * rec.workforce_cost

class Concept_workforce_lines(models.Model):
    _name = 'construction.concept_workforce_lines'
    _description = 'concepto mano de obra'

    quantity = fields.Float( string='Cantidad', default='1' )
    w_import = fields.Float( digits=(6,4), string='Importe', compute='_get_subtotal', store=True)

    concept_id = fields.Many2one('construction.concept', string='Concepto',  ondelete='cascade', index=True, copy=False)
    workforce_id = fields.Many2one('construction.workforce', string='Cuadrilla',  ondelete='cascade', index=True, copy=False)
    workforce_cost = fields.Float( related='workforce_id.cost', string='Costo')
    workforce_unit = fields.Many2one( related='workforce_id.w_unit', string='Unidad')

    @api.depends('quantity','workforce_cost')
    def _get_subtotal(self):
        for rec in self:
            rec['w_import'] = rec.quantity * rec.workforce_cost

class Basic_workforce_lines(models.Model):
    _name = 'construction.basic_workforce_lines'
    _description = 'básico mano de obra'

    quantity = fields.Float( string='Cantidad', default='1' )
    w_import = fields.Float( digits=(6,4), string='Importe', compute='_get_subtotal', store=True)

    basic_id = fields.Many2one('construction.basic', string='Básico',  ondelete='cascade', index=True, copy=False)
    workforce_id = fields.Many2one('construction.workforce', string='Cuadrilla',  ondelete='cascade', index=True, copy=False)
    workforce_cost = fields.Float( related='workforce_id.cost', string='Costo')
    workforce_unit = fields.Many2one( related='workforce_id.w_unit', string='Unidad')

    @api.depends('quantity','workforce_cost')
    def _get_subtotal(self):
        for rec in self:
            rec['w_import'] = rec.quantity * rec.workforce_cost

class Workforce_team(models.Model):
    _name = 'construction.workforce_team'
    _description = 'Cuadrilla'

    quantity = fields.Integer( string='Cantidad', default='1' )
    subtotal = fields.Float( digits=(6,4), string='Importe', compute='_get_subtotal')
    workforce_id = fields.Many2one('construction.workforce', string='Mano de obra',  ondelete='cascade', index=True, copy=False)
    worker_type_id = fields.Many2one('construction.worker_type', string='Tipo de trabajador',  ondelete='cascade', index=True, copy=False)
    worker_type_cost = fields.Float( related='worker_type_id.cost', string='Costo')
    worker_type_coin = fields.Selection( related='worker_type_id.coin', string='Moneda')

    currency_id = fields.Many2one('res.currency', compute='_compute_currency')
    
    @api.depends('worker_type_coin')
    def _compute_currency(self):
        self.currency_id = self.env.ref('base.main_company').currency_id

    @api.depends('quantity','worker_type_cost')
    def _get_subtotal(self):
        for rec in self:
            rec['subtotal'] = rec.quantity * rec.worker_type_cost

class Worker_type(models.Model):
    _name = 'construction.worker_type'
    _description = 'Tipo de trabajador'

    name = fields.Char( string='Descripción', required=True)
    code = fields.Char( string="Código", required=True)
    w_unit = fields.Many2one( 'construction.unit', string='Unidad', domain="[('magnitude','=','tiempo')]", ondelete='set null', index=True, copy=False)
    cost = fields.Float( digits=(6,2), help="Costo", string='Costo')
    coin = fields.Selection( statics.coins, string='Moneda', default='0')

    currency_id = fields.Many2one('res.currency', compute='_compute_currency')
    
    @api.depends('coin')
    def _compute_currency(self):
        self.currency_id = self.env.ref('base.main_company').currency_id

class Workers(models.Model):
    _name = 'construction.worker'
    _description = "Trabajadores, peones, "

    code = fields.Char( string="Código", required=True)
    name = fields.Char( string="Nombre trabajador", required=True)
    photo = fields.Image( string="Foto", help="Foto del trabajador")
    unit = fields.Selection(statics.units, string="unidad")
    performance = fields.Float( digits=(6,7), help="Rendimiento", string='Rendimiento')
    price = fields.Float( digits=(6,7), help="Precio", string='precio')
    coin = fields.Selection( statics.coins, string='Moneda', default='0')
    worker_type = fields.Selection([('0','Operador'),('1','Peón')], string="Tipo de trabajador", required=True)

    #****************************************** FASAR *************************************************
    salary = fields.Float( digits=(6,7), string='Salario', help="Salario", required=True )
    tp = fields.Float( digits=(6,7), string='TP', help="Salario", readonly=True, compute="_get_tp" )
    ti = fields.Float( digits=(6,7), string='TI', help="falta definir", readonly=True, compute="_get_ti" )
    fsr = fields.Float( digits=(6,7), string='FSR', help="falta definir", readonly=True, compute="_get_fsr" )
    fsn = fields.Float( digits=(6,7), string='FSN', help="falta definir", readonly=True, compute="_get_fsn" )
    sn = fields.Float( digits=(6,7), string='SN', help="falta definir", readonly=True, compute="_get_sn" )
    sr = fields.Float( digits=(6,7), string='SR', help="falta definir", readonly=True, compute="_get_sr" )

    calendar_id = fields.Many2one('construction.calendar', ondelete="set null", string="Calendario", index=True)
    calendar = fields.Integer( related="calendar_id.calendar", string="Días calendario")
    sundays = fields.Float( related="calendar_id.sundays", string="Domingos")
    bonus = fields.Integer( related="calendar_id.bonus", string="Aguinaldo")
    holidays = fields.Integer( related="calendar_id.holidays", string="Vacaciones")
    oficial_days_rest_count = fields.Float( related="calendar_id.oficial_days_rest_count", string="Días oficiales de descanso" )
    days_habit_count = fields.Float( related="calendar_id.days_habit_count", string="Días por costumbre")

    @api.depends('calendar', 'bonus', 'holidays')
    def _get_tp(self):
        for rec in self:
            rec['tp'] = rec.calendar + rec.bonus + (0.2*rec.holidays)

    @api.depends('calendar', 'sundays', 'oficial_days_rest_count', 'days_habit_count', 'holidays')
    def _get_ti(self):
        for rec in self:
            rec['ti'] = rec.calendar - rec.sundays - rec.oficial_days_rest_count - rec.days_habit_count - rec.holidays

    @api.depends('tp', 'ti', 'worker_type')
    def _get_fsr(self):
        for rec in self:
            if rec.tp > 0 and rec.ti > 0:
                if rec.worker_type == '0':
                    rec['fsr'] = 1.27*(rec.tp/rec.ti)
                elif rec.worker_type == '1':
                    rec['fsr'] = 1.29*(rec.tp/rec.ti)
                else:
                    rec['fsr'] = 0
            else:
                rec['fsr'] = 0

    @api.depends('calendar', 'tp')
    def _get_fsn(self):
        for rec in self:
            if rec.calendar > 0 and rec.tp >0:
                rec['fsn'] = rec.tp/rec.calendar
            else:
                rec['fsn'] = 0

    @api.depends('salary', 'fsn')
    def _get_sn(self):
        for rec in self:
            rec['sn'] = rec.salary * rec.fsn

    @api.depends('fsr', 'sn')
    def _get_sr(self):
        for rec in self:
            sr = rec.sn * rec.fsr
            rec['sr'] = sr
            rec['price'] = sr
