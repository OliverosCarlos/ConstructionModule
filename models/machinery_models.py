from odoo import api, fields, models
from ..utils import vars

statics = vars.Vars

class Machinery(models.Model):
    _name = 'construction.machinery'
    _description = 'Maquinaria'

    code = fields.Char(string='Código')
    name = fields.Char(string='Nombre')
    description = fields.Char(string='Descripción')
    unit = fields.Many2one( 'construction.unit', string='Unidad', ondelete='set null', index=True, copy=False)

    capacity = fields.Float(digits=(6,2), string='Capacidad (HP)')
    serie = fields.Char(string='Serie')
    fuel_type = fields.Selection(statics.fuels, string='Tipo de combustible')
    anual_interest_rate = fields.Float(digits=(6,4), string='Tasa de interés anual')
    average_annual_insurance_premium = fields.Float(digits=(6,4), string='Prima anual promedio de seguros')
    photo = fields.Image( string="Foto", help="Foto de maquinaria")

    basic_id = fields.Many2one('construction.basic', string='Concepto/Básico',  ondelete='cascade', index=True, copy=False)

    acquisition_price = fields.Float(digits=(6,4), string='Precio de adquisición')
    wheels_price = fields.Float(digits=(6,4), string='Precio juego de llantas')
    additional_equipment = fields.Float(digits=(6,4), string='Equipo adicional')
    wheels_economic_life = fields.Float(digits=(6,4), string='Vida económica de las llantas')
    price_special_pieces = fields.Float(digits=(6,4), string='Precio pzas especiales')
    pieces_economic_life = fields.Float(digits=(6,4), string='Vida económica pzas especiales')
    machine_value = fields.Float(digits=(6,4), string='Valor de la máquina')
    salvage_value = fields.Float(digits=(6,4), string='Valor de rescate', readonly=True, compute='_get_salvage_value')
    operator_real_salary = fields.Float(digits=(6,4), string='Salario real del operador')
    cost_by_operation_salary = fields.Float(digits=(6,4), string='Costo por salario de operación', readonly=True, compute='_get_cost_by_operation_salary')
    effective_working_hours_shift = fields.Float(digits=(6,4), string='Horas efectivas de trabajo por turno')
    lubricant_time = fields.Float(digits=(6,4), string='Tiempo entre cambio de lubricante')

    economic_life_years = fields.Integer(digits=(6,4), string='Vida economica en años')
    economic_life = fields.Integer(digits=(6,4), string='Vida economica', readonly=True, compute='_get_economic_life')
    hours_per_year = fields.Integer(digits=(6,4), string='Horas por año')
    fuel_cost = fields.Float(digits=(6,4), string='Costo combustible')
    lubricant_cost = fields.Float(digits=(6,4), string='Costo lubricante')
    rated_power = fields.Float(digits=(6,4), string='Potencia nominal')
    operating_factor = fields.Float(digits=(6,4), string='Factor de operación')
    operating_power = fields.Float(digits=(6,4), string='Potencia de operación')
    mantenance_factor = fields.Float(digits=(6,4), string='Factor de mantenimiento')
    fuel_coefficient = fields.Float(digits=(6,4), string='Coeficiente de combustible')
    lubricant_coefficient = fields.Float(digits=(6,4), string='Coeficiente de lubricante')
    carter_capacity = fields.Float(digits=(6,4), string='Capacidad del carter')
    performance_factor = fields.Float(digits=(6,4), string='Factor de rendimiento')

    # FIXED COST
    depreciation = fields.Float(digits=(6,4), string='Depreciación', readonly=True, compute='_get_depreciation')
    investment = fields.Float(digits=(6,4), string='Inversión', readonly=True, compute='_get_investment')
    insurance = fields.Float(digits=(6,4), string='Seguros', readonly=True, compute='_get_insurance')
    maintenance = fields.Float(digits=(6,4), string='Mantenimiento', readonly=True, compute='_get_maintenance')
    sum_fixed_cost = fields.Float(digits=(6,4), string='Suma cargos fijos', readonly=True, compute='_get_sum_fixed_cost')

    # CONSUMPTIONS
    fuel = fields.Float(digits=(6,4), string='Combustible', readonly=True, compute='_get_fuel')
    lubrincant = fields.Float(digits=(6,4), string='Lubricante', readonly=True, compute='_get_lubrincant')
    wheels = fields.Float(digits=(6,4), string='Llantas', readonly=True, compute='_get_wheels')
    special_pieces = fields.Float(digits=(6,4), string='Piezas especiales', readonly=True, compute='_get_special_pieces')
    sum_consumptions = fields.Float(digits=(6,4), string='Suma de consumos', readonly=True, compute='_get_sum_consumptions')

    # OPERATION
    operation_sum = fields.Float(digits=(6,4), string='Suma de operación')
    worker_id = fields.Many2one('construction.worker_type',
        ondelete="set null", string="Operador", index=True)
    worker_price = fields.Float( related="worker_id.cost", string="Salario del operador")
    worker_unit = fields.Many2one( related="worker_id.w_unit", string="Unidad")
    worker_import = fields.Float( digits=(4,6), string="Importe", readonly=True, compute='_get_import')

    direct_cost_machinery = fields.Float(digits=(6,4), string='Costo directo hora-maquinaria', readonly=True, compute='_get_direct_cost_machinery', store=True)

    @api.depends('acquisition_price')
    def _get_salvage_value(self):
        for rec in self:
            rec['salvage_value'] = .12*rec.acquisition_price

    @api.depends('economic_life_years','hours_per_year')
    def _get_economic_life(self):
        for rec in self:
            rec['economic_life'] = rec.economic_life_years * rec.hours_per_year

    @api.depends('rated_power', 'operating_factor')
    def _get_cost_by_operation_salary(self):
        for rec in self:
            rec['cost_by_operation_salary'] = rec.rated_power*rec.operating_factor 

    # FIXED COST COMPUTE
    @api.depends('machine_value','salvage_value','economic_life')
    def _get_depreciation(self):
        for rec in self:
            if rec.machine_value>0 and rec.salvage_value>0 and rec.economic_life>0:
                rec['depreciation'] = (rec.machine_value - rec.salvage_value)/rec.economic_life
            else:
                rec['depreciation'] = 0

    @api.depends('machine_value','salvage_value','anual_interest_rate','hours_per_year')
    def _get_investment(self):
        for rec in self:
            if rec.machine_value>0 and rec.salvage_value>0 and rec.anual_interest_rate>0 and rec.hours_per_year>0:
                rec['investment'] = (rec.machine_value + rec.salvage_value) * (rec.anual_interest_rate/100)/(2*rec.hours_per_year)
            else:
                rec['investment'] = 0

    @api.depends('machine_value','salvage_value','average_annual_insurance_premium','hours_per_year')
    def _get_insurance(self):
        for rec in self:
            if rec.machine_value>0 and rec.salvage_value>0 and rec.average_annual_insurance_premium>0 and rec.hours_per_year>0:
                rec['insurance'] = (rec.machine_value + rec.salvage_value) * (rec.average_annual_insurance_premium/100)/(2*rec.hours_per_year)
            else:
                rec['insurance'] = 0

    @api.depends('mantenance_factor', 'depreciation')
    def _get_maintenance(self):
        for rec in self:
            rec['maintenance'] = rec.mantenance_factor * rec.depreciation

    @api.depends( 'depreciation', 'investment', 'insurance', 'maintenance' )
    def _get_sum_fixed_cost(self):
        for rec in self:
            rec['sum_fixed_cost'] = rec.depreciation + rec.investment + rec.insurance + rec.maintenance

    # CONSUMPTIONS COMPUTE
    @api.depends('fuel_cost', 'operating_power', 'fuel_coefficient')
    def _get_fuel(self):
        for rec in self:
            rec['fuel'] = rec.fuel_cost * rec.operating_power * rec.fuel_coefficient
 
    @api.depends('lubricant_time','lubricant_cost','operating_power','lubricant_coefficient','carter_capacity')
    def _get_lubrincant(self):
        for rec in self:
            if rec.lubricant_time>0 and rec.carter_capacity>0:
                rec['lubrincant'] = ( (rec.lubricant_coefficient * rec.operating_power) + (rec.carter_capacity/rec.lubricant_time) ) * rec.lubricant_cost   
            else :
                rec['lubrincant'] = ( (rec.lubricant_coefficient * rec.operating_power) + 0 ) * rec.lubricant_cost

    @api.depends('wheels_price', 'wheels_economic_life')
    def _get_wheels(self):        
        for rec in self:
            if rec.wheels_price > 0 and rec.wheels_economic_life > 0:
                rec['wheels'] = rec.wheels_price/rec.wheels_economic_life
            else:
                rec['wheels'] = 0
    
    @api.depends('price_special_pieces', 'pieces_economic_life')
    def _get_special_pieces(self):
        for rec in self:
            if rec.price_special_pieces>0 and rec.pieces_economic_life>0:
                rec['special_pieces'] = (rec.price_special_pieces*5)/rec.pieces_economic_life
            else:
                rec['special_pieces'] = 0

    @api.depends('fuel', 'lubrincant', 'wheels', 'special_pieces')
    def _get_sum_consumptions(self):
        for rec in self:
            rec['sum_consumptions'] = rec.fuel + rec.lubrincant + rec.wheels + rec.special_pieces

    #OPERATION IMPORT
    @api.depends('operator_real_salary', 'effective_working_hours_shift')
    def _get_import(self):
        for rec in self:
            if rec.operator_real_salary > 0 and rec.effective_working_hours_shift > 0:
                rec['worker_import'] = rec.operator_real_salary/rec.effective_working_hours_shift
            else:
                rec['worker_import'] = 0

    @api.depends('sum_fixed_cost', 'sum_consumptions', 'worker_import')
    def _get_direct_cost_machinery(self):
        for rec in self:
            rec['direct_cost_machinery'] = rec.sum_fixed_cost + rec.sum_consumptions + rec.worker_import

class Stage_machinery_lines(models.Model):
    _name = 'construction.stage_machinery_lines'
    _description = 'Partida maquinaria'

    quantity = fields.Float(string='Cantidad', default='1')
    m_import = fields.Float( digits=(6,4), string='Importe', readonly=True, compute='_get_subtotal', store=True)

    stage_id = fields.Many2one('construction.stage', string='Partida',  ondelete='cascade', index=True, copy=False)
    machinery_id = fields.Many2one('construction.machinery', string='Maquinaria',  ondelete='cascade', index=True, copy=False)
    machinery_cost = fields.Float( related='machinery_id.direct_cost_machinery', string='Costo')
    machinery_unit = fields.Many2one( related='machinery_id.unit', string='Unidad')

    @api.depends('quantity','machinery_cost')
    def _get_subtotal(self):
        for rec in self:
            rec['m_import'] = rec.quantity * rec.machinery_cost

class Concept_machinery_lines(models.Model):
    _name = 'construction.concept_machinery_lines'
    _description = 'concepto maquinaria'

    quantity = fields.Float(string='Cantidad', default='1')
    m_import = fields.Float( digits=(6,4), string='Importe', readonly=True, compute='_get_subtotal', store=True)

    concept_id = fields.Many2one('construction.concept', string='Concepto',  ondelete='cascade', index=True, copy=False)
    machinery_id = fields.Many2one('construction.machinery', string='Maquinaria',  ondelete='cascade', index=True, copy=False)
    machinery_cost = fields.Float( related='machinery_id.direct_cost_machinery', string='Costo')
    machinery_unit = fields.Many2one( related='machinery_id.unit', string='Unidad')

    @api.depends('quantity','machinery_cost')
    def _get_subtotal(self):
        for rec in self:
            rec['m_import'] = rec.quantity * rec.machinery_cost

class Basic_machinery_lines(models.Model):
    _name = 'construction.basic_machinery_lines'
    _description = 'concepto/basico maquinaria'

    quantity = fields.Float(string='Cantidad', default='1')
    m_import = fields.Float( digits=(6,4), string='Importe', readonly=True, compute='_get_subtotal', store=True)

    basic_id = fields.Many2one('construction.basic', string='Básico',  ondelete='cascade', index=True, copy=False)
    machinery_id = fields.Many2one('construction.machinery', string='Maquinaria',  ondelete='cascade', index=True, copy=False)
    machinery_cost = fields.Float( related='machinery_id.direct_cost_machinery', string='Costo')
    machinery_unit = fields.Many2one( related='machinery_id.unit', string='Unidad')

    @api.depends('quantity','machinery_cost')
    def _get_subtotal(self):
        for rec in self:
            rec['m_import'] = rec.quantity * rec.machinery_cost