# -*- coding: utf-8 -*-
# Carlos Oliveros

from odoo import api, fields, models


class MachineryReport(models.AbstractModel):
    _name = 'report.construction.machinery_report'
    _description = 'Get machinery for report.'

    @api.model
    def _get_report_values(self, docids, data=None):
        
        machineries = []

        query_stage_data = ''' 
            SELECT *
            FROM construction_stage
            WHERE construction_stage.project_id = {}
        '''.format(docids[0])

        self.env.cr.execute(query_stage_data)   
        stages = self.env.cr.fetchall()

        for stage in stages:
            #GET SUPPLIES BY STAGE
            machineries_stage = self.get_machinery_by_id(stage[0])
            if len(machineries_stage) > 0:
                for machineries_item in machineries_stage:
                    machineries = self.add_input(machineries, machineries_item)

            #GET SUPPLIES BASICS LEVEL 1
            basics_level_1 = self.get_concepts_by_id(stage[0])
            if len(basics_level_1) > 0:
                for basic_level_1 in basics_level_1:
                    machineries_concepts = self.get_machinery_by_basic_level_1_id(basic_level_1[0])
                    for machineries_concept in machineries_concepts:
                        machineries = self.add_input(machineries, machineries_concept)

                    #GET SUPPLIES BASICS LEVEL 2
                    concepts_level_2 = self.get_basics_level_2_by_basic_livel_1_id(basic_level_1[0])
                    for concept_level_2 in concepts_level_2:

                        machineries_basics = self.get_machinery_by_basic_level_2_id(concept_level_2[0])
                        for machineries_basic in machineries_basics:
                            machineries = self.add_input(machineries, machineries_basic)
        print('maquinariaas ------------------->')
        print(machineries)
        return {
            'machineries' : machineries
            # 'docs' : self.env['construction.project'].browse(self.env.project.id)
            }

    def get_concepts_by_id(self, id):
        query_concept = ''' 
            SELECT
                construction_concept.id,
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
        self.env.cr.execute(query_concept)   
        concepts = self.env.cr.fetchall()
        return concepts
    
    def get_basics_level_2_by_basic_livel_1_id(self, id):
        query_concept = ''' 
            SELECT
                construction_basic.id,
                construction_basic.code,
                construction_basic.name,
                construction_unit.name,
                construction_basic.cost,
                construction_concept_basic_lines.quantity,
                construction_concept_basic_lines.b_import
            FROM construction_basic
            INNER JOIN construction_concept_basic_lines
            ON construction_concept_basic_lines.basic_id = construction_basic.id
            INNER JOIN construction_unit
            ON construction_unit.id = construction_basic.unit
            WHERE construction_concept_basic_lines.concept_id = {}
        '''.format(id)
        self.env.cr.execute(query_concept)   
        res = self.env.cr.fetchall()
        return res

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
        self.env.cr.execute(query_machinery)   
        machinery = self.env.cr.fetchall()
        return machinery

    def get_machinery_by_basic_level_1_id(self, id):
        query_machinery = ''' 
            SELECT
                construction_machinery.code,
                construction_machinery.name,
                construction_unit.name as unit,
                construction_machinery.direct_cost_machinery,
                construction_concept_machinery_lines.quantity,
                construction_concept_machinery_lines.m_import
            FROM construction_machinery
            INNER JOIN construction_concept_machinery_lines
            ON construction_concept_machinery_lines.machinery_id = construction_machinery.id
            INNER JOIN construction_unit
            ON construction_unit.id = construction_machinery.unit
            WHERE construction_concept_machinery_lines.concept_id = {}
        '''.format(id)
        self.env.cr.execute(query_machinery)   
        machinery = self.env.cr.fetchall()
        return machinery

    def get_machinery_by_basic_level_2_id(self, id):
        query_machinery = ''' 
            SELECT
                construction_machinery.code,
                construction_machinery.name,
                construction_unit.name as unit,
                construction_machinery.direct_cost_machinery,
                construction_basic_machinery_lines.quantity,
                construction_basic_machinery_lines.m_import
            FROM construction_machinery
            INNER JOIN construction_basic_machinery_lines
            ON construction_basic_machinery_lines.machinery_id = construction_machinery.id
            INNER JOIN construction_unit
            ON construction_unit.id = construction_machinery.unit
            WHERE construction_basic_machinery_lines.basic_id = {}
        '''.format(id)
        self.env.cr.execute(query_machinery)   
        machinery = self.env.cr.fetchall()
        return machinery

    def add_input(self, l, obj):
        item = self.to_json_supplies(obj)
        if self.input_exist(l, item):
            return list( map(lambda x : self.update_input(x, item), l) )
        else :
            l.append(item)
            print('sending')
            print(l)
            return l

    def to_json_supplies(self, item):
        return {
            'code' : item[0],
            'name' : item[1],
            'unit' : item[2],
            'cost' : item[3],
            'quantity' : item[4],
            'import' : item[5]
        }

    def input_exist(self, l, item):
        result = list(filter( lambda x : x['code'] == item['code'], l))
        if len(result) > 0:
            return True
        else:
            return False

    def update_input(self, a, b):
        if a['code'] == b['code']:
            a['quantity'] = a['quantity']+b['quantity']
            a['import'] = a['import']+b['import']
        return a

