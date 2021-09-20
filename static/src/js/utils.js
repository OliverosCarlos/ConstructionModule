odoo.define('construction.forge_utils', (require) => {
    "use strict";

    var Class = require('web.Class');

    var Utils = {
        value: null,
        get Utils() {
            return this.value;
        },
        set Utils(value) {
            this.value = value;
        }
    }

    var Utils = Class.extend({
        init: function () {
            this.a = 'robo'
        },
        setModelItems: function (data) {
            console.log(data);
            window.model_elements = data;
            console.log(window.model_elements);
        },
        getModelItems: function (objectid) {
            return window.model_elements.filter(element => {
                if(objectid){
                    return element.objectid == objectid
                }else{
                    return element.objectid
                }
            });
        }
    });

    return Utils;
});