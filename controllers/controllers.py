#-*- coding: utf-8 -*-
from odoo import http
from functools import reduce

class Construction(http.Controller):

    @http.route('/construction/get/stages/by/project_id', auth='public', type='json')
    def getStagesByID(self, project_id=None):
        query_get_fsr_fsn = ''' 
            SELECT fsr, fsn
            FROM construction_project
            WHERE construction_project.id = {}
        '''.format(project_id)

        http.request.cr.execute(query_get_fsr_fsn)   
        fsr_fsn = http.request.cr.fetchall()
        print('\n \n fsr fsn')
        print(fsr_fsn[0])
        print('fsr fsn \n \n')

        query_stage_data = ''' 
            SELECT *
            FROM construction_stage
            WHERE construction_stage.project_id = {}
        '''.format(project_id)




        http.request.cr.execute(query_stage_data)   
        stages = http.request.cr.fetchall()
        stages_data = []
        for stage in stages:
            item = {}
            concepts = self.get_concepts_by_id(stage[0])
            materials = self.get_materials_by_id(stage[0])
            workforce = self.get_workforce_by_id(stage[0],fsr_fsn[0])
            machineries = self.get_machinery_by_id(stage[0])

            stages_data.append({
                'name': stage[2],
                'cost': stage[10],
                'materials': materials,
                'workforces': workforce,
                'machineries': machineries,
                'concepts': concepts,
                'len_items': len(concepts)+len(materials)+len(workforce)+len(machineries)+1
            })
        return stages_data

    def get_concepts_by_id(self, id):
        query_concept = ''' 
            SELECT
                construction_concept.code,
                construction_concept.name,
                construction_unit.name,
                construction_concept.cost,
                construction_stage_concept_lines.quantity,
                construction_stage_concept_lines.s_import
            FROM construction_concept
            INNER JOIN construction_stage_concept_lines
            ON construction_stage_concept_lines.concept_id = construction_concept.id
            INNER JOIN construction_unit
            ON construction_unit.id = construction_concept.unit
            WHERE construction_stage_concept_lines.stage_id = {}
        '''.format(id)
        http.request.cr.execute(query_concept)   
        concepts = http.request.cr.fetchall()
        return concepts
    
    def get_materials_by_id(self, id):
        query_materials = ''' 
            SELECT
                construction_material.code,
                construction_material.name,
                construction_unit.name as unit,
                construction_material.cost,
                construction_stage_material_lines.quantity,
                construction_stage_material_lines.m_import
            FROM construction_material
            INNER JOIN construction_stage_material_lines
            ON construction_stage_material_lines.material_id = construction_material.id
            INNER JOIN construction_unit
            ON construction_unit.id = construction_material.m_unit
            WHERE construction_stage_material_lines.stage_id = {}
        '''.format(id)
        http.request.cr.execute(query_materials)   
        meterials = http.request.cr.fetchall()
        return meterials

    def get_workforce_by_id(self, id, fsr_fsn):
        query_workforce = ''' 
            SELECT
                construction_workforce.code,
                construction_workforce.name,
                construction_unit.name as unit,
                construction_workforce.cost,
                construction_stage_workforce_lines.quantity,
                construction_stage_workforce_lines.w_import
            FROM construction_workforce
            INNER JOIN construction_stage_workforce_lines
            ON construction_stage_workforce_lines.workforce_id = construction_workforce.id
            INNER JOIN construction_unit
            ON construction_unit.id = construction_workforce.w_unit
            WHERE construction_stage_workforce_lines.stage_id = {}
        '''.format(id)
        http.request.cr.execute(query_workforce)
        workforce = http.request.cr.fetchall()
        workforce = list( map(lambda x: self.set_fasar(x, fsr_fsn[0], fsr_fsn[1]), workforce) )
        return workforce

    def set_fasar(self, worker, fsr, fsn):
        worker = list(worker)
        print('\n \n workforce')
        print(worker)
        sn = worker[3] * fsn
        sr = sn * fsr
        worker[3] = sr
        worker[5] = worker[3]*worker[4]
        print(worker)
        print('workforce \n \n')
        return worker
    # @api.depends('salary', 'fsn')
    # def _get_sn(self):
    #     for rec in self:
    #         rec['sn'] = rec.salary * rec.fsn

    # @api.depends('fsr', 'sn')
    # def _get_sr(self):
    #     for rec in self:
    #         sr = rec.sn * rec.fsr
    #         rec['sr'] = sr
    #         rec['price'] = sr

    def get_machinery_by_id(self, id):
        query_machinery = ''' 
            SELECT
                construction_machinery.code,
                construction_machinery.name,
                construction_unit.name as unit,
                construction_machinery.direct_cost_machinery,
                construction_stage_machinery_lines.quantity,
                construction_stage_machinery_lines.m_import
            FROM construction_machinery
            INNER JOIN construction_stage_machinery_lines
            ON construction_stage_machinery_lines.machinery_id = construction_machinery.id
            INNER JOIN construction_unit
            ON construction_unit.id = construction_machinery.unit
            WHERE construction_stage_machinery_lines.stage_id = {}
        '''.format(id)
        http.request.cr.execute(query_machinery)   
        machinery = http.request.cr.fetchall()
        return machinery

    @http.route('/construction/get/project', auth='public', type='json')
    def getProjectById(self, project_id=None):
        query_stage_data = ''' 
            SELECT
                construction_stage.id,
                construction_stage.name
            FROM construction_stage
            INNER JOIN construction_project_stage_lines
            ON construction_project_stage_lines.stage_id = construction_stage.id
            WHERE construction_project_stage_lines.project_id = {}
        '''.format(project_id)

        query_concept = ''' 
            SELECT
                construction_concept.id,
                construction_concept.name
            FROM construction_concept
            INNER JOIN construction_stage_concept_lines
            ON construction_stage_concept_lines.concept_id = construction_concept.id
            WHERE construction_stage_concept_lines.stage_id = {}
        '''
        http.request.cr.execute(query_stage_data)   
        stages = http.request.cr.fetchall()

        def getConceptMaterial(concept_id):
            query_concept_material = ''' 
                SELECT 
                    construction_material.id,
                    construction_material.name
                FROM construction_concept_material_lines 
                INNER JOIN construction_material
                ON construction_material.id = construction_concept_material_lines.material_id
                WHERE construction_concept_material_lines.concept_id = {}
            '''.format(concept_id)
            http.request.cr.execute(query_concept_material)   
            concept_materials = http.request.cr.fetchall()
            return concept_materials

        def getConceptWorkforce(concept_id):
            query_concept_workforce = ''' 
                SELECT 
                    construction_workforce.id,
                    construction_workforce.name
                FROM construction_concept_workforce_lines 
                INNER JOIN construction_workforce
                ON construction_workforce.id = construction_concept_workforce_lines.workforce_id
                WHERE construction_concept_workforce_lines.concept_id = {}
            '''.format(concept_id)
            http.request.cr.execute(query_concept_workforce)   
            concept_workforce = http.request.cr.fetchall()
            return concept_workforce
            
        def getConceptMachinery(concept_id):
            query_concept_machinery = ''' 
                SELECT 
                    construction_machinery.id,
                    construction_machinery.name
                FROM construction_concept_machinery_lines 
                INNER JOIN construction_machinery
                ON construction_machinery.id = construction_concept_machinery_lines.machinery_id
                WHERE construction_concept_machinery_lines.concept_id = {}
            '''.format(concept_id)
            http.request.cr.execute(query_concept_machinery)   
            concept_machinery = http.request.cr.fetchall()
            return concept_machinery

        def getConceptBasic(concept_id=0):
            query_concept_basic = ''' 
                SELECT 
                    construction_basic.id,
                    construction_basic.name
                FROM construction_concept_basic_lines 
                INNER JOIN construction_basic
                ON construction_basic.id = construction_concept_basic_lines.basic_id
                WHERE construction_concept_basic_lines.concept_id = {}
            '''.format(concept_id)
            http.request.cr.execute(query_concept_basic)   
            concept_basics = http.request.cr.fetchall()
            concept_basic_data = []
            for concept_basic in concept_basics:
                concept_basic_data.append( {
                    'basic_id':concept_basic[0],
                    'basic_name':concept_basic[1],
                    'material':getBasicMaterial(concept_basic[0]),
                    'workforce':getBasicWorkforce(concept_basic[0]),
                    'machinery':getBasicMachinery(concept_basic[0])
                } )
            return  concept_basic_data

        def getBasicMaterial(basic_id):
            query_basic_material = ''' 
                SELECT 
                    construction_material.id,
                    construction_material.name
                FROM construction_basic_material_lines 
                INNER JOIN construction_material
                ON construction_material.id = construction_basic_material_lines.material_id
                WHERE construction_basic_material_lines.basic_id = {}
            '''.format(basic_id)
            http.request.cr.execute(query_basic_material)   
            basic_material = http.request.cr.fetchall()
            return basic_material

        def getBasicWorkforce(basic_id):
            query_basic_workforce = ''' 
                SELECT 
                    construction_workforce.id,
                    construction_workforce.name
                FROM construction_basic_workforce_lines 
                INNER JOIN construction_workforce
                ON construction_workforce.id = construction_basic_workforce_lines.workforce_id
                WHERE construction_basic_workforce_lines.basic_id = {}
            '''.format(basic_id)
            http.request.cr.execute(query_basic_workforce)   
            basic_workforce = http.request.cr.fetchall()
            return basic_workforce

        def getBasicMachinery(basic_id):
            query_basic_machinery = ''' 
                SELECT 
                    construction_machinery.id,
                    construction_machinery.name
                FROM construction_basic_machinery_lines 
                INNER JOIN construction_machinery
                ON construction_machinery.id = construction_basic_machinery_lines.machinery_id
                WHERE construction_basic_machinery_lines.basic_id = {}
            '''.format(basic_id)
            http.request.cr.execute(query_basic_machinery)   
            basic_machinery = http.request.cr.fetchall()
            return basic_machinery

        tree_data = []
        
        for stage in stages:
            query_concept_data = query_concept.format(stage[0])
            http.request.cr.execute(query_concept_data)
            concepts = http.request.cr.fetchall()
            concept_data = []
            for concept in concepts:
                concept_data.append({
                    'concept_id':concept[0],
                    'concept_name':concept[1],
                    'material':getConceptMaterial(concept[0]),
                    'workforce':getConceptWorkforce(concept[0]),
                    'machinery':getConceptMachinery(concept[0]),
                    'basic':getConceptBasic(concept[0])
                })
            tree_data.append({
                'stage_id':stage[0],
                'stage_name':stage[1],
                'concepts':concept_data
            })
        return tree_data

    @http.route('/construction/get/stage/by/id', auth='public', type='json')
    def getStageById(self, stage_id=None):
        query_stage_data=''' 
            SELECT 
                construction_stage.code,
                construction_stage.name,
                construction_unit.name as unit_name,
                construction_stage.cost,
                construction_stage.description
            FROM construction_stage
            INNER JOIN construction_unit
            ON construction_unit.id = construction_stage.unit  
            WHERE construction_stage.id = {}
        '''.format(stage_id)
        http.request.cr.execute(query_stage_data)   
        data_stage = http.request.cr.fetchall()

        query_stage_concepts_data =''' 
            SELECT 
            	construction_concept.code,
            	construction_concept.name,
            	construction_unit.name as unit_name,
                construction_stage_concept_lines.quantity,
            	construction_concept.cost,
            	construction_stage_concept_lines.s_import
            FROM construction_stage_concept_lines
            INNER JOIN construction_concept
            ON construction_stage_concept_lines.concept_id = construction_concept.id
            INNER JOIN construction_unit
            ON construction_unit.id = construction_concept.unit
            WHERE construction_stage_concept_lines.stage_id = {}
        '''.format(stage_id)
        http.request.cr.execute(query_stage_concepts_data)   
        data_stage_concepts = http.request.cr.fetchall()

        data = {
            'concept': data_stage,
            'data': data_stage_concepts
        } 
        print(data)
        return data

    @http.route('/construction/get/concept/by/id', auth='public', type='json')
    def getConceptById(self, concept_id=None):
        query_concept_data=''' 
            SELECT 
                construction_concept.code,
                construction_concept.name,
                construction_unit.name as unit_name,
                construction_concept.cost,
                construction_concept.description
            FROM construction_concept
            INNER JOIN construction_unit
            ON construction_unit.id = construction_concept.unit  
            WHERE construction_concept.id = {}
        '''.format(concept_id)
        http.request.cr.execute(query_concept_data)   
        data_concept = http.request.cr.fetchall()

        query_concepts_data =''' 
            SELECT 
            	construction_material.code,
            	construction_material.name,
            	construction_unit.name as unit,
            	construction_concept_material_lines.quantity,
            	construction_material.cost as cost,
            	construction_concept_material_lines.m_import as import
            FROM construction_concept
            INNER JOIN construction_concept_material_lines
            ON construction_concept_material_lines.concept_id = construction_concept.id
            INNER JOIN construction_material
            ON construction_material.id = construction_concept_material_lines.material_id
            INNER JOIN construction_unit
            ON construction_unit.id = construction_material.m_unit
            WHERE construction_concept.id = {id}

            UNION

            SELECT 
            	construction_machinery.code,
            	construction_machinery.name,
            	construction_unit.name as unit,
            	construction_concept_machinery_lines.quantity,
            	construction_machinery.direct_cost_machinery as cost,
            	construction_concept_machinery_lines.m_import as import
            FROM construction_concept
            INNER JOIN construction_concept_machinery_lines
            ON construction_concept_machinery_lines.concept_id = construction_concept.id
            INNER JOIN construction_machinery
            ON construction_machinery.id = construction_concept_machinery_lines.machinery_id
            INNER JOIN construction_unit
            ON construction_unit.id = construction_machinery.unit
            WHERE construction_concept.id = {id}

            UNION

            SELECT 
            	construction_workforce.code,
            	construction_workforce.name,
            	construction_unit.name as unit,
            	construction_concept_workforce_lines.quantity,
            	construction_workforce.cost,
            	construction_concept_workforce_lines.w_import as import
            FROM construction_concept
            INNER JOIN construction_concept_workforce_lines
            ON construction_concept_workforce_lines.concept_id = construction_concept.id
            INNER JOIN construction_workforce
            ON construction_workforce.id = construction_concept_workforce_lines.workforce_id
            INNER JOIN construction_unit
            ON construction_unit.id = construction_workforce.w_unit
            WHERE construction_concept.id = {id}

            UNION

            SELECT 
            	construction_basic.code,
            	construction_basic.name,
            	construction_unit.name as unit,
            	construction_concept_basic_lines.quantity,
            	construction_basic.cost,
            	construction_concept_basic_lines.b_import as import
            FROM construction_concept
            INNER JOIN construction_concept_basic_lines
            ON construction_concept_basic_lines.concept_id = construction_concept.id
            INNER JOIN construction_basic
            ON construction_basic.id = construction_concept_basic_lines.basic_id
            INNER JOIN construction_unit
            ON construction_unit.id = construction_basic.unit
            WHERE construction_concept.id = {id}
        '''.format(id = concept_id)
        http.request.cr.execute(query_concepts_data)   
        data_concepts = http.request.cr.fetchall()

        data = {
            'concept': data_concept,
            'data': data_concepts
        } 
        print(data)
        return data

    @http.route('/construction/get/basic/by/id', auth='public', type='json')
    def getBasicById(self, basic_id=None):
        query_basic_data=''' 
            SELECT 
                construction_basic.code,
                construction_basic.name,
                construction_unit.name as unit_name,
                construction_basic.cost,
                construction_basic.description
            FROM construction_basic
            INNER JOIN construction_unit
            ON construction_unit.id = construction_basic.unit  
            WHERE construction_basic.id = {}
        '''.format(basic_id)
        http.request.cr.execute(query_basic_data)   
        data_basic = http.request.cr.fetchall()

        query_basics_data =''' 
            SELECT 
            	construction_material.code,
            	construction_material.name,
            	construction_unit.name as unit,
            	construction_basic_material_lines.quantity,
            	construction_material.cost as cost,
            	construction_basic_material_lines.m_import as import
            FROM construction_basic
            INNER JOIN construction_basic_material_lines
            ON construction_basic_material_lines.basic_id = construction_basic.id
            INNER JOIN construction_material
            ON construction_material.id = construction_basic_material_lines.material_id
            INNER JOIN construction_unit
            ON construction_unit.id = construction_material.m_unit
            WHERE construction_basic.id = {id}

            UNION

            SELECT 
            	construction_machinery.code,
            	construction_machinery.name,
            	construction_unit.name as unit,
            	construction_basic_machinery_lines.quantity,
            	construction_machinery.direct_cost_machinery as cost,
            	construction_basic_machinery_lines.m_import as import
            FROM construction_basic
            INNER JOIN construction_basic_machinery_lines
            ON construction_basic_machinery_lines.basic_id = construction_basic.id
            INNER JOIN construction_machinery
            ON construction_machinery.id = construction_basic_machinery_lines.machinery_id
            INNER JOIN construction_unit
            ON construction_unit.id = construction_machinery.unit
            WHERE construction_basic.id = {id}

            UNION

            SELECT 
            	construction_workforce.code,
            	construction_workforce.name,
            	construction_unit.name as unit,
            	construction_basic_workforce_lines.quantity,
            	construction_workforce.cost,
            	construction_basic_workforce_lines.w_import as import
            FROM construction_basic
            INNER JOIN construction_basic_workforce_lines
            ON construction_basic_workforce_lines.basic_id = construction_basic.id
            INNER JOIN construction_workforce
            ON construction_workforce.id = construction_basic_workforce_lines.workforce_id
            INNER JOIN construction_unit
            ON construction_unit.id = construction_workforce.w_unit
            WHERE construction_basic.id = {id}
        '''.format(id = basic_id)
        http.request.cr.execute(query_basics_data)   
        data_basics = http.request.cr.fetchall()

        data = {
            'concept': data_basic,
            'data': data_basics
        } 
        print(data)
        return data

    @http.route('/construction/set/model', auth='public', type='json')
    def getBasicById(self, model_id=None, model_name=None, project_id=None):
        print('aqui ------------------------------------>')
        print(model_id, model_name)

        project = http.request.env['construction.project'].browse(int(project_id))
        print(project.name)
        project.name

        project.forge_model_name = model_name
        project.update({'forge_model_id' : model_id, 'forge_model_name': model_name})
        # product.share_count = product.share_count + 1