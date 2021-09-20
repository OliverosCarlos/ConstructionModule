from odoo import api, models, fields


class Budgets(models.TransientModel):
    _name = "construction.budgets_wizard"

    name = fields.Char(string='nombre')
    project_id = fields.Char(string="id del proyecto", compute="_set_project_id")

    def _set_project_id(self):
        self.project_id = self.env.context.get("project_id")
        print('project set')

    def show_data(self):
        stages = []
        for stage in self.env['construction.project'].browse(self.env.context.get("project_id")):
            stages.append(stage.name)
        print(stages)
        return stages
    # def update_student_fees(self):
    #     # print("Yeah successfully click on update_student_fees method........")

    #     self.env['school.student'].browse(self._context.get("active_ids")).update({'total_fees': self.total_fees})
    #     return True