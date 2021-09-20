from odoo import api, fields, models


class Project(models.Model):
    _name = 'construction.project'
    _description = 'Proyectos de obras'

    project_type_list = [
        ('1', 'Casa habitación'),
        ('2', 'Desarrollo de proyecto'),
        ('3', 'Proyecto estructural'),
        ('4', 'Proyecto arquitectonico'),
        ('5', 'proyecto de instalaciones'),
        ('6', 'construccion de arquitectura'),
        ('7', 'construccion de acabados' ),
        ('8', 'Construcción de ing electrica'),
        ('9',  'Construcción Mécanica'),
        ('10', 'Construcción Hidrosanitaria'),
        ('11', 'Supervisión' ),
        ('12', 'Gerencia')
        ]

    contract_type_list = [
        ('1', 'Precios unitarios'),
        ('2', 'Precio alzado'),
        ('3', 'Prestación de servicios')
    ]

    code = fields.Char(string='Código')
    name = fields.Char(string='Nombre')
    description = fields.Char(string='Descripción')

    cost = fields.Float(digits=(6,4), string='Costos directos', compute='_get_cost_stage', store=True)
    unit = fields.Many2one( 'construction.unit', string='Unidad', ondelete='set null', index=True, copy=False)

    stages = fields.One2many('construction.stage','project_id', string='Partida')

    forge_model_name = fields.Char(string='Nombre del modelo')
    forge_model_id = fields.Char(string='Id del modelo' )
    forge_model_select = fields.Char(string='Seleccionar modelo')
    project_type = fields.Selection(project_type_list, string='Tipo de proyecto')
    contract_type = fields.Selection(contract_type_list, string='Tipo de contrato')
    image = fields.Image( string="Imagen", help="Imagen del proyecto")
    indirect_costs = fields.Many2many('construction.indirect_cost', string="Costos indirectos")
    total_indirect_cost = fields.Float(digits=(6,4), string="Costos indirectos", compute='_get_total_indirect_cost')
    total_cost = fields.Float( digits=(6,4), string="Total", compute='_get_total_cost')

    client_id = fields.Many2one('res.partner', string="Cliente", index="True")
    client_name = fields.Char( related="client_id.name", string="Nombre")
    client_phone = fields.Char( related="client_id.phone", string="Telefono")
    client_email = fields.Char( related="client_id.email", string="Correo")
    client_function = fields.Char( related="client_id.function", string="Puesto")
    client_website = fields.Char( related="client_id.website", string="Sitio web")

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

    @api.depends('stages')
    def _get_cost_stage(self):
        for rec in self:
            total = 0
            for row in rec.stages:
                total += row.cost
            rec['cost'] = total

    @api.depends('indirect_costs')
    def _get_total_indirect_cost(self):
        for rec in self:
            total = 0
            for item in rec.indirect_costs:
                if item.cost_type == '0':
                    total += item.cost
                else :
                    total += self.cost*(item.percentage)
            rec['total_indirect_cost'] = total
            

    @api.depends('total_indirect_cost', 'cost')
    def _get_total_cost(self):
        for rec in self:
            total = rec.total_indirect_cost+rec.cost
            rec['total_cost'] = total


    def open_budget_wizard(self):
        return {
            'name': 'Presupuestos',
            'view_mode': 'form',
            'res_model': 'construction.budgets_wizard',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'context': {
                'project_id':self.id,
                'fsn': self.fsn,
                'fsr': self.fsr
                }
        }

    #****************************************** FASAR *************************************************
    tp = fields.Float( digits=(6,7), string='TP', help="Salario", readonly=True, compute="_get_tp" )
    ti = fields.Float( digits=(6,7), string='TI', help="falta definir", readonly=True, compute="_get_ti" )
    fsr = fields.Float( digits=(6,7), string='FSR', help="falta definir", readonly=True, compute="_get_fsr", store=True )
    fsn = fields.Float( digits=(6,7), string='FSN', help="falta definir", readonly=True, compute="_get_fsn", store=True )
    sn = fields.Float( digits=(6,7), string='SN', help="falta definir", readonly=True, compute="_get_sn" )
    sr = fields.Float( digits=(6,7), string='SR', help="falta definir", readonly=True, compute="_get_sr" )

    #CALENDAR
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

    @api.depends('tp', 'ti')
    def _get_fsr(self):
        for rec in self:
            if rec.tp > 0 and rec.ti > 0:
                rec['fsr'] = 1.29*(rec.tp/rec.ti)
            else:
                rec['fsr'] = 0

    @api.depends('calendar', 'tp')
    def _get_fsn(self):
        for rec in self:
            if rec.calendar > 0 and rec.tp >0:
                rec['fsn'] = rec.tp/rec.calendar
            else:
                rec['fsn'] = 0

class Stage(models.Model):
    _name = 'construction.stage'
    _description = 'Partidas de un proyecto'

    code = fields.Char(string='Código')
    name = fields.Char(string='Nombre')
    description = fields.Char(string='Descripción')
    cost = fields.Float(digits=(6,4), string='Costo', compute='_get_cost_stage', store=True)
    unit = fields.Many2one( 'construction.unit', string='Unidad', ondelete='set null', index=True, copy=False)

    project_id = fields.Many2one('construction.project', string='Obra/Proyecto',  ondelete='cascade', index=True, copy=False)
    project_forge_model_name = fields.Char( related="project_id.forge_model_name", string="Nombre del modelo")
    project_forge_model_id = fields.Char( related="project_id.forge_model_id", string="Id del modelo")

    bim_model_viewer = fields.Char(string="Visualizar modelo BIM")

    material_import = fields.Float(digits=(6,2), string='importe de materiales', compute='_get_material_import', store=True)
    workforce_import = fields.Float(digits=(6,2), string='importe de mano de obra', compute='_get_workforce_import', store=True)
    machinery_import = fields.Float(digits=(6,2), string='importe de maquinaria', compute='_get_machinery_import', store=True)
    concept_import = fields.Float(digits=(6,2), string='importe de conceptos', compute='_get_concept_import', store=True)

    concepts = fields.One2many('construction.stage_concept_lines','stage_id', string='Concepto')
    stage_material_lines = fields.One2many('construction.stage_material_lines','stage_id', string='Partida')
    stage_workforce_lines = fields.One2many('construction.stage_workforce_lines','stage_id', string='Partida')
    stage_machinery_lines = fields.One2many('construction.stage_machinery_lines','stage_id', string='Partida')

    @api.depends('material_import','workforce_import','machinery_import','concept_import')
    def _get_cost_stage(self):
        for rec in self:
            rec['cost'] = rec.material_import + rec.workforce_import + rec.machinery_import + rec.concept_import

    @api.depends('stage_material_lines')
    def _get_material_import(self):
        for rec in self:
            total = 0
            for row in rec.stage_material_lines:
                total += row.m_import
            rec['material_import'] = total

    @api.depends('stage_workforce_lines')
    def _get_workforce_import(self):
        for rec in self:
            total = 0
            for row in rec.stage_workforce_lines:
                total += row.w_import
            rec['workforce_import'] = total

    @api.depends('stage_machinery_lines')
    def _get_machinery_import(self):
        for rec in self:
            total = 0
            for row in rec.stage_machinery_lines:
                total += row.m_import
            rec['machinery_import'] = total

    @api.depends('concepts')
    def _get_concept_import(self):
        for rec in self:
            total = 0
            for row in rec.concepts:
                total += row.s_import
            rec['concept_import'] = total

class Stage_concept_lines(models.Model):
    _name = 'construction.stage_concept_lines'
    _description = 'partida concepto'

    quantity = fields.Float( string='Cantidad', default='1' )
    s_import = fields.Float( digits=(6,4), string='Importe', compute='_get_subtotal', store=True)

    stage_id = fields.Many2one('construction.stage', string='Partida',  ondelete='cascade', index=True, copy=False)
    concept_id = fields.Many2one('construction.concept', string='Concepto',  ondelete='cascade', index=True, copy=False)
    concept_cost = fields.Float( related='concept_id.cost', string='Costo')
    concept_unit = fields.Many2one( related='concept_id.unit', string='Unidad')

    @api.depends('quantity','concept_cost')
    def _get_subtotal(self):
        for rec in self:
            rec['s_import'] = rec.quantity * rec.concept_cost

class Concept(models.Model):
    _name = 'construction.concept'
    _description = 'Conceptos'

    code = fields.Char(string='Código')
    name = fields.Char(string='Nombre')
    description = fields.Html(string='Descripción')
    unit = fields.Many2one( 'construction.unit', string='Unidad', ondelete='set null', index=True, copy=False)

    cost = fields.Float(digits=(6,4), string='Costo', compute='_get_cost_concept', store=True)
    material_import = fields.Float(digits=(6,2), string='importe de materiales', compute='_get_material_import', store=True)
    workforce_import = fields.Float(digits=(6,2), string='importe de mano de obra', compute='_get_workforce_import', store=True)
    machinery_import = fields.Float(digits=(6,2), string='importe de maquinaria', compute='_get_machinery_import', store=True)
    basic_import = fields.Float(digits=(6,2), string='importe de básicos', compute='_get_basic_import', store=True)

    stage_id = fields.Many2one('construction.stage', string='Partida',  ondelete='cascade', index=True, copy=False)
    concept_material_lines = fields.One2many('construction.concept_material_lines','concept_id', string='Concepto')
    concept_workforce_lines = fields.One2many('construction.concept_workforce_lines','concept_id', string='Concepto')
    concept_machinery_lines = fields.One2many('construction.concept_machinery_lines','concept_id', string='Concepto')
    concept_basic_lines = fields.One2many('construction.concept_basic_lines','concept_id', string='Concepto')

    @api.depends('material_import','workforce_import','machinery_import','basic_import')
    def _get_cost_concept(self):
        for rec in self:
            rec['cost'] = rec.material_import + rec.workforce_import + rec.machinery_import + rec.basic_import

    @api.depends('concept_material_lines')
    def _get_material_import(self):
        for rec in self:
            total = 0
            for row in rec.concept_material_lines:
                total += row.m_import
            rec['material_import'] = total

    @api.depends('concept_workforce_lines')
    def _get_workforce_import(self):
        for rec in self:
            total = 0
            for row in rec.concept_workforce_lines:
                total += row.w_import
            rec['workforce_import'] = total

    @api.depends('concept_machinery_lines')
    def _get_machinery_import(self):
        for rec in self:
            total = 0
            for row in rec.concept_machinery_lines:
                total += row.m_import
            rec['machinery_import'] = total

    @api.depends('concept_basic_lines')
    def _get_basic_import(self):
        for rec in self:
            total = 0
            for row in rec.concept_basic_lines:
                total += row.b_import
            rec['basic_import'] = total


class Concept_basic_lines(models.Model):
    _name = 'construction.concept_basic_lines'
    _description = 'concepto básicos'

    quantity = fields.Float( string='Cantidad', default='1' )
    b_import = fields.Float( digits=(6,4), string='Importe', compute='_get_subtotal', store=True)

    concept_id = fields.Many2one('construction.concept', string='Concepto',  ondelete='cascade', index=True, copy=False)
    basic_id = fields.Many2one('construction.basic', string='Básico',  ondelete='cascade', index=True, copy=False)
    basic_cost = fields.Float( related='basic_id.cost', string='Costo', store=True)
    basic_unit = fields.Many2one( related='basic_id.unit', string='Unidad')

    @api.depends('quantity','basic_cost')
    def _get_subtotal(self):
        for rec in self:
            rec['b_import'] = rec.quantity * rec.basic_cost

class Basic(models.Model):
    _name = 'construction.basic'
    _description = 'Básicos'

    code = fields.Char(string='Código')
    name = fields.Char(string='Nombre')
    description = fields.Html(string='Descripción')
    unit = fields.Many2one( 'construction.unit', string='Unidad', ondelete='set null', index=True, copy=False)

    cost = fields.Float(digits=(6,4), string='Costo', compute='_get_cost_concept', store=True)
    material_import = fields.Float(digits=(6,2), string='importe de materiales', compute='_get_material_import', store=True)
    workforce_import = fields.Float(digits=(6,2), string='importe de mano de obra', compute='_get_workforce_import', store=True)
    machinery_import = fields.Float(digits=(6,2), string='importe de maquinaria', compute='_get_machinery_import', store=True)

    basic_material_lines = fields.One2many('construction.basic_material_lines','basic_id', string='básico')
    basic_workforce_lines = fields.One2many('construction.basic_workforce_lines','basic_id', string='básico')
    basic_machinery_lines = fields.One2many('construction.basic_machinery_lines','basic_id', string='básico')

    @api.depends('material_import','workforce_import','machinery_import')
    def _get_cost_concept(self):
        for rec in self:
            rec['cost'] = rec.material_import + rec.workforce_import + rec.machinery_import

    @api.depends('basic_material_lines')
    def _get_material_import(self):
        for rec in self:
            total = 0
            for row in rec.basic_material_lines:
                total += row.m_import
            rec['material_import'] = total

    @api.depends('basic_workforce_lines')
    def _get_workforce_import(self):
        for rec in self:
            total = 0
            for row in rec.basic_workforce_lines:
                total += row.w_import
            rec['workforce_import'] = total

    @api.depends('basic_machinery_lines')
    def _get_machinery_import(self):
        for rec in self:
            total = 0
            for row in rec.basic_machinery_lines:
                total += row.m_import
            rec['machinery_import'] = total

class Budget(models.Model):
    _name = 'construction.budget'
    _description = 'Presupuestos'

    name = fields.Char(string='nombre')
