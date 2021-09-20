odoo.define('construction.model_select_widget', (require) => {
    "use strict";

    const Widget = require('web.AbstractField');
    const registry = require('web.field_registry');
    const Utils = require('construction.forge_utils');

    var utils = new Utils();

    //ENVIROMENT VARIABLES
    var FORGE_CLIENT_ID = 'O1dIaiH9hP7ye8M2mnqUpO6C8jgLqKmF';
    var CLIENT_SECRET = 'YAGxNUAlTOybNAGD';
    var CURRENT_URN_OBJ = ''
    var ACCOUNT_ID = 'a0431d28-9773-4946-9987-f961281d3f4f';
    var HUB_ID = 'b.a0431d28-9773-4946-9987-f961281d3f4f'

    //CONTROL VARIABLES
    var access_token = '';
    var _super;
    var instance;

    //ELEMENT VARIABLES

    var menu = [{
        // name:'folders',
        // id:'2',
        childs: [{ name: 'folders', id: '3', files: [{ name: 'archivo', urn: '' }] }],
        files: [{ name: 'archivo', urn: '' }]
    }];

    var model_menu = [{
        name: '',
        id: ''
    }]

    var model_elements = [];

    var documentId = '';

    //FORGE VIEWER
    var viewer;

    var project_data;
    var current_data;

    var scopes = 'data:read data:write data:create bucket:create bucket:read account:write account:read';

    const bucketKey = FORGE_CLIENT_ID.toLowerCase() + '_tutorial_bucket'; // Prefix with your ID so the bucket key is unique across all buckets on all other accounts
    const policyKey = 'transient'; // Expires in 24hr

    var formData = new FormData();

    const model_select_widget = Widget.extend({
        xmlDependencies: ['/construction/static/src/xml/model_select_widget.xml'],
        template: 'construction.model_select_view_widget',
        events: {
            'click .cntr-folder': 'show',
            'click .setModel': 'setModel',
            'click .getHubs': 'getHubs',
            'click .getJobStatus': 'getJobStatus',
            'change .onFileUpload': 'onFileUpload',
            'click .model-item': 'selectModelFromItem'
        },
        isSet() {
            return true;
        },
        async willStart() {
            instance = this;
            instance.menu = menu;
            instance.model_menu = model_menu;
            await this.getToken2legged();
            // Dialog.alert(this, 'Now you can share this content', { title: 'Copied!'  });
        },
        start() {
            this.renderElement();
        },
        show(ev) {
            ev.target.parentElement.parentElement.querySelector(".nested").classList.toggle("active");
            ev.target.classList.toggle("caret-down");
        },
        renderElement() {
            _super = this._super;
            return _super.apply(this, arguments);
        },
        renderMenu() {
            instance.menu = menu;
            instance.model_menu = model_menu;
            return _super.apply(this, arguments);
        },
        async setModel(){

            await this._rpc({
                route: '/construction/set/model' ,
                params: {
                    model_id: instance.modelo_id,
                    model_name: instance.model_name,
                    project_id: this.recordData.id
                },
            }).then(function (res) {'robo_id updated',
            'robo_name updated',
                console.log(res)
            });
            // this.value = 'robo';
            // var field_forge_model_name = document.getElementsByName('forge_model_name')
            // var field_forge_model_id = document.getElementsByName('forge_model_id')
            
            // this.record.data.forge_model_name = 'robo name';
            // this.record.data.forge_model_id = 'robo id';
            // console.log(this);

            // console.log(field_forge_model_name);
            // field_forge_model_name[0].value = 'robo name';
            // field_forge_model_id[0].value = 'robo id';
            // console.log(field_forge_model_id);
        },
        getToken2legged() {
            menu = [];
            $.ajax({
                type: "POST",
                url: "https://developer.api.autodesk.com/authentication/v1/authenticate",
                headers: { 'content-type': 'application/x-www-form-urlencoded' },
                data: {
                    client_id: FORGE_CLIENT_ID,
                    client_secret: CLIENT_SECRET,
                    grant_type: 'client_credentials',
                    scope: scopes
                },
                success: function (response) {
                    access_token = response.access_token;
                    console.log(access_token);
                    instance.getHubs();
                },
                error: function (xmlHttpRequest, textStatus, errorThrown) {
                    alert(textStatus, errorThrown);
                }
            });
        },
        showViewer() {
            var options = {
                env: 'AutodeskProduction',
                api: 'derivativeV2',  // for models uploaded to EMEA change this option to 'derivativeV2_EU'
                getAccessToken: function (onTokenReady) {
                    var token = access_token;
                    var timeInSeconds = 3600; // Use value provided by Forge Authentication (OAuth) API
                    onTokenReady(token, timeInSeconds);
                }
            };

            Autodesk.Viewing.Initializer(options, function () {
                var htmlDiv = document.getElementById('forgeViewer');
                viewer = new Autodesk.Viewing.GuiViewer3D(htmlDiv);
                var startedCode = viewer.start();
                if (startedCode > 0) {
                    console.error('Failed to create a Viewer: WebGL not supported.');
                    return;
                }

                console.log('Initialization complete, loading a model next...');

            });
            return _super.apply(this, arguments);
        },
        getHubs() {
            $.ajax({
                type: "GET",
                url: "https://developer.api.autodesk.com/project/v1/hubs/" + HUB_ID + "/projects",
                headers: { 'Authorization': 'Bearer ' + access_token },
                success: function (response) {
                    instance.getFolders(response.data[0].relationships.topFolders.links.related.href);
                },
                error: function (xmlHttpRequest, textStatus, errorThrown) {
                    alert(textStatus, errorThrown);
                }
            });
        },
        getFolders(urlFoldersTop) {
            $.ajax({
                type: "GET",
                url: urlFoldersTop,
                headers: { 'Authorization': 'Bearer ' + access_token },
                success: function (response) {

                    var folders = response.data.filter(item => item.attributes.name == 'Project Files' || item.attributes.name == 'Plans');
                    folders.forEach(item => {
                        var data_item = {
                            name: item.attributes.name,
                            id: item.id,
                            childs: [],
                            files: []
                        };
                        instance.getFoldersChilds(item.relationships.contents.links.related.href, data_item);
                    });
                },
                error: function (xmlHttpRequest, textStatus, errorThrown) {
                    alert(textStatus, errorThrown);
                }
            });
        },
        getFoldersChilds(url_content, data_item) {
            $.ajax({
                type: "GET",
                url: url_content,
                headers: { 'Authorization': 'Bearer ' + access_token },
                success: function (response) {
                    //response for now gett two folders "folders" and "item"
                    if (response.data.length != 0) {
                        response.data.forEach(element => {//element = each folder and items
                            if (element.type == 'folders') {
                                instance.getItem(element.relationships.contents.links.related.href, data_item).done(function (item) {
                                    
                                    instance.getThumbnails(item.included[0].relationships.thumbnails.data.id).done(function(thumbnail){
                                        const url = window.URL || window.webkitURL;
                                        const src = url.createObjectURL(thumbnail);
                                        console.log(src);
                                        data_item.childs.push({
                                            name: element.attributes.name,
                                            id: element.id,
                                            files: [{
                                                name: item.data[0].attributes.displayName,
                                                urn: item.included[0].relationships.derivatives.data.id,
                                                thumbnail: src
                                            }]
                                        });
                                        instance.renderMenu();
                                    }).fail(function(){
                                        console.log('error en thumbnail');
                                    });
                                    
                                }).fail(function () {
                                    console.log('error en item');
                                });
                            }
                            if (element.type == 'items') {
                                instance.getItem(element.links.self.href).done(function (item) {
                                    instance.getThumbnails(item.included[0].relationships.thumbnails.data.id).done(function(thumbnail){
                                        const url = window.URL || window.webkitURL;
                                        const src = url.createObjectURL(thumbnail);
                                        console.log(src);
                                        data_item.files.push({
                                            name: item.data.attributes.displayName,
                                            urn: item.included[0].relationships.derivatives.data.id,
                                            thumbnail: src
                                        })
                                        instance.renderMenu();
                                    }).fail(function(){
                                        console.log('error en thumbnail');
                                    });
                
                                }).fail(function () {
                                    console.log('error en item');
                                });
                            }
                        });

                    }
                },
                error: function (xmlHttpRequest, textStatus, errorThrown) {
                    console.log(textStatus, errorThrown);
                },
                complete: function (data) {
                    menu.push(data_item);
                    instance.renderMenu();
                }
            });

        },
        getItem(url_content) {
            return $.ajax({
                type: "GET",
                url: url_content,
                headers: { 'Authorization': 'Bearer ' + access_token }
            });
        },
        renderFile(ev) {
            // urn = ev.target.attributes[0].value 
            instance.getMetadata(ev.target.attributes[0].value).done(function (metadata) {
                model_menu = [];
                console.log(metadata);
                // guid = metadata.data.metadata[0].guid
                console.log(metadata.data.metadata[0].guid);
                instance.getMetadataGuidProperties(ev.target.attributes[0].value, metadata.data.metadata[1].guid).done(function (guidData) {
                    console.log(guidData);
                    model_elements = guidData.data.collection;

                    utils.setModelItems(guidData.data.collection);

                    // guidData.data.objects[0].objects.forEach( object => {
                    //     model_menu.push({
                    //         name:object.name,
                    //         id:object.objectid
                    //     });
                    // });
                    instance.model_menu = model_menu;
                    // instance.renderMenu();
                }).fail(function () {
                    console.log('error en getMetadataGuid');
                });
            }).fail(function () {
                console.log('error en item');
            });

            Autodesk.Viewing.Document.load('urn:' + ev.target.attributes[0].value, onDocumentLoadSuccess, onDocumentLoadFailure);

            function onDocumentLoadSuccess(viewerDocument) {
                var defaultModel = viewerDocument.getRoot().getDefaultGeometry();
                viewer.loadDocumentNode(viewerDocument, defaultModel);
            }

            function onDocumentLoadFailure() {
                console.error('Failed fetching Forge manifest');
            }
        },
        getMetadata(urnBase64) {
            return $.ajax({
                type: "GET",
                url: "https://developer.api.autodesk.com/modelderivative/v2/designdata/" + urnBase64 + "/metadata",
                headers: { 'Authorization': 'Bearer ' + access_token }
            });
        },
        getMetadataGuid(urnBase64, guid) {
            return $.ajax({
                type: "GET",
                url: "https://developer.api.autodesk.com/modelderivative/v2/designdata/" + urnBase64 + "/metadata/" + guid,
                headers: { 'Authorization': 'Bearer ' + access_token }
            });
        },
        getMetadataGuidProperties(urnBase64, guid) {
            return $.ajax({
                type: "GET",
                url: "https://developer.api.autodesk.com/modelderivative/v2/designdata/" + urnBase64 + "/metadata/" + guid + "/properties",
                headers: { 'Authorization': 'Bearer ' + access_token }
            });
        },
        getThumbnails(urnBase64) {
            return $.ajax({
                type: "GET",
                url: "https://developer.api.autodesk.com/modelderivative/v2/designdata/"+urnBase64+"/thumbnail?width=100&height=100",
                headers: { 
                    'Authorization': 'Bearer ' + access_token ,
                },
                xhrFields: {
                    responseType: 'blob'
                },
            });
        },
        selectModelFromItem(ev){
            document.getElementById('model-display-id').value = ev.currentTarget.attributes[1].value;
            document.getElementById('model-display-name').value = ev.currentTarget.attributes[2].value;
            instance.modelo_id = ev.currentTarget.attributes[1].value;
            instance.model_name = ev.currentTarget.attributes[2].value;
        }
    });

    registry.add('model_select', model_select_widget);
});