odoo.define('construction.model_viewer_widget', (require) => {
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
    var entity;

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

    const model_viewer_widget = Widget.extend({
        xmlDependencies: ['/construction/static/src/xml/model_viewer_widget.xml'],
        template: 'construction.model_viewer_view_widget',
        events: {
            'click .caret': 'show',
            'click .connect': 'connect',
            'click .showViewer': 'showViewer',
            'click .getHubs': 'getHubs',
            'click .getJobStatus': 'getJobStatus',
            'change .onFileUpload': 'onFileUpload',
            'click .renderFile': 'renderFile'
        },
        isSet() {
            return true;
        },
        async willStart() {
            entity = this;
            entity.menu = menu;
            entity.model_menu = model_menu;
            await this.getToken2legged();
            // Dialog.alert(this, 'Now you can share this content', { title: 'Copied!'  });
        },
        start() {
            return Promise.all([
                this.renderElement(),
            ]);
        },
        show(ev) {
            ev.target.parentElement.parentElement.parentElement.querySelector(".nested").classList.toggle("active");
            ev.target.classList.toggle("caret-down");
        },
        renderElement() {
            _super = this._super;
            return _super.apply(this, arguments);
        },
        renderMenu() {
            entity.menu = menu;
            entity.model_menu = model_menu;
            return _super.apply(this, arguments);
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
                    entity.showViewer();
                },
                error: function (xmlHttpRequest, textStatus, errorThrown) {
                    alert(textStatus, errorThrown);
                }
            });
        },
        showViewer() {
            console.log(entity);
            if (entity.recordData.project_id) {
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

                    var config3d = {
                        extensions: ['MyExtension']
                    };

                    var htmlDiv = document.getElementById('forgeViewer');
                    viewer = new Autodesk.Viewing.GuiViewer3D(htmlDiv);
                    var startedCode = viewer.start();
                    if (startedCode > 0) {
                        console.error('Failed to create a Viewer: WebGL not supported.');
                        return;
                    }

                    console.log('Initialization complete, loading a model next...');

                });

                Autodesk.Viewing.Document.load('urn:' + entity.recordData.project_forge_model_id, onDocumentLoadSuccess, onDocumentLoadFailure);

                function onDocumentLoadSuccess(viewerDocument) {
                    var defaultModel = viewerDocument.getRoot().getDefaultGeometry();
                    viewer.loadDocumentNode(viewerDocument, defaultModel);
                }

                function onDocumentLoadFailure() {
                    console.error('Failed fetching Forge manifest');
                }

                entity.getMetadata(entity.recordData.project_forge_model_id).done(function (metadata) {
                    console.log(metadata);
                    // guid = metadata.data.metadata[0].guid
                    // console.log(metadata.data.metadata[0].guid);
                    entity.getMetadataGuidProperties(entity.recordData.project_forge_model_id, metadata.data.metadata[1].guid).done(function (guidData) {
                        console.log(guidData);
                        // model_elements = guidData.data.collection;

                        // utils.setModelItems(guidData.data.collection);

                    }).fail(function () {
                        console.log('error en getMetadataGuid');
                    });

                }).fail(function () {
                    console.log('error en item');
                });

                return _super.apply(this, arguments);
            }

        },
        getHubs() {
            $.ajax({
                type: "GET",
                url: "https://developer.api.autodesk.com/project/v1/hubs/" + HUB_ID + "/projects",
                headers: { 'Authorization': 'Bearer ' + access_token },
                success: function (response) {
                    entity.getFolders(response.data[0].relationships.topFolders.links.related.href);
                },
                error: function (xmlHttpRequest, textStatus, errorThrown) {
                    alert(textStatus, errorThrown);
                }
            });
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
        }


    });

    registry.add('model_viewer', model_viewer_widget);
});