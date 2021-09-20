odoo.define('construction.budgets_widget_js', (require) => {
    "use strict";

    const Widget = require('web.AbstractField');
    const registry = require('web.field_registry');

    var _super;
    var entity;
    var project_id;

    var desc = 'carlos';
    var stages = [];
    var subtotal = 0;

    const budget_widget = Widget.extend({
        xmlDependencies: ['/construction/static/src/xml/budget_view_template.xml'],
        template: 'construction.budget_view_widget',
        events: {
            'click .getStages': 'get_stages',
        },
        async willStart(){
            project_id = this.value;

            entity = this;
            entity.desc = desc;
            entity.stages = stages;
            entity.iva = 16;
            await this._rpc({
                route: '/construction/get/stages/by/project_id',
                params: {
                    project_id: project_id,
                },
            }).then(function (res) {
                entity.stages = res;
                entity.stages.forEach(element => {
                    subtotal += element.cost;
                });
                entity.subtotal = subtotal;
                console.log('subtotal')
                console.log(subtotal)
                entity.importe_iva = (16*subtotal)/100;
                entity.total = subtotal+entity.importe_iva;
                //a.renderElement();
            });
        },
        start() {
            project_id = this.value;
            this.renderElement();
        },
        renderElement() {
            _super = this._super;
            return _super.apply(this, arguments);
        },
        async get_stages(){
            var a = this;
            await this._rpc({
                route: '/construction/get/stages/by/project_id',
                params: {
                    project_id: project_id,
                },
            }).then(function (res) {
                console.log('data');
                console.log(res);
                //entity.stages = res;
                //a.renderElement();
            });
        }
    });

    registry.add('budget', budget_widget);
});