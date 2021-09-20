odoo.define('construction.tree_all_concepts', (require) => {
    "use strict";

    const Widget = require('web.AbstractField');
    const registry = require('web.field_registry');

    var project_data
    var current_data
    var FORGE_CLIENT_ID = 'O1dIaiH9hP7ye8M2mnqUpO6C8jgLqKmF';
    var CLIENT_SECRET = 'YAGxNUAlTOybNAGD';
    var CURRENT_URN_OBJ = ''
    var ACCOUNT_ID = 'a0431d28-9773-4946-9987-f961281d3f4f';
    var _super;
    var scopes = 'data:read data:write data:create bucket:create bucket:read account:write account:read';

    const bucketKey = FORGE_CLIENT_ID.toLowerCase() + '_tutorial_bucket'; // Prefix with your ID so the bucket key is unique across all buckets on all other accounts
    const policyKey = 'transient'; // Expires in 24hr

    var access_token = '';

    var formData = new FormData();

    const tree_concepts_widget = Widget.extend({
        xmlDependencies: ['/construction/static/src/xml/construction_tree_widget.xml'],
        template: 'construction.tree_concepts_view_widget',
        events: {
            'click .caret': 'show',
            'click .stage-up': 'stageUP',
            'click .concept-up': 'conceptUP',
            'click .basic-up': 'basicUP',
            'click .showViewer': 'showViewer',
            'click .getHubs': 'getHubs',
            'click .getJobStatus': 'getJobStatus',
            'change .onFileUpload': 'onFileUpload'
        },
        isSet() {
            return true;
        },
        async willStart() {
            await this._rpc({
                route: '/construction/get/project',
                params: {
                    project_id: this.recordData.id,
                },
            }).then(function (res) {
                project_data = res;
                console.log(res)
            });
            // Dialog.alert(this, 'Now you can share this content', { title: 'Copied!'  });
        },
        start() {
            this.renderElement();
        },
        show(ev) {
            ev.target.parentElement.parentElement.parentElement.querySelector(".nested").classList.toggle("active");
            ev.target.classList.toggle("caret-down");
        },
        async stageUP(ev) {
            var a = this;
            await this._rpc({
                route: '/construction/get/stage/by/id',
                params: {
                    stage_id: ev.target.attributes[0].value,
                },
            }).then(function (res) {
                console.log(res);
                current_data = res;
                a.renderStageData();
            });
        },
        async conceptUP(ev) {
            var a = this;
            await this._rpc({
                route: '/construction/get/concept/by/id',
                params: {
                    concept_id: ev.target.attributes[0].value,
                },
            }).then(function (res) {
                console.log(res);
                current_data = res;
                a.renderStageData();
            });
        },
        async basicUP(ev) {
            var a = this;
            await this._rpc({
                route: '/construction/get/basic/by/id',
                params: {
                    basic_id: ev.target.attributes[0].value,
                },
            }).then(function (res) {
                console.log(res);
                current_data = res;
                a.renderStageData();
            });
        },
        renderElement() {
            this.project_data = project_data
            this.current_data = { 'concept': [[]], 'data': [[]] }
            _super = this._super;
            return this._super.apply(this, arguments);
        },
        renderStageData() {
            this.current_data = current_data;
            return _super.apply(this, arguments);
        },
        showViewer() {
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
                },
                error: function (xmlHttpRequest, textStatus, errorThrown) {
                    alert(textStatus, errorThrown);
                }
            });
            // var myViewerDiv = document.getElementById('MyViewerDiv');
            // var viewer = new Autodesk.Viewing.Private.GuiViewer3D(myViewerDiv);
            // var options = {
            //     'env' : 'Local',
            //     'document' : 'http://developer-autodesk.github.io/translated-models/dwfx-sample-house/f0224dd3-8767-45c1-ff99-5c9c881b9fee/0.svf'
            // };
            // Autodesk.Viewing.Initializer(options, function() {
            //     viewer.start(options.document, options);
            // });
        },
        // getHubs() {
        //     $.ajax({
        //         type: "GET",
        //         url: "https://developer.api.autodesk.com/project/v1/hubs",
        //         headers: { 'Authorization': 'Bearer ' + access_token },
        //         success: function (response) {
        //             console.log(response);
        //         },
        //         error: function (xmlHttpRequest, textStatus, errorThrown) {
        //             alert(textStatus, errorThrown);
        //         }
        //     });
        // }
        // getHubs() {
        //     $.ajax({
        //         type: "GET",
        //         url: "https://developer.api.autodesk.com/hq/v1/accounts/" + ACCOUNT_ID + "/projects",
        //         headers: { 'Authorization': 'Bearer ' + access_token },
        //         data: {
        //             scope: scopes
        //         },
        //         success: function (response) {
        //             console.log(response);
        //         },
        //         error: function (xmlHttpRequest, textStatus, errorThrown) {
        //             alert(textStatus, errorThrown);
        //         }
        //     });
        // },
        // getHubs(){
        //     var data_bucket = {
        //         bucketKey: "bucket1-tst",
        //         access: "full",
        //         policyKey: "transient"
        //     }
        //     $.ajax({
        //         type: "POST",
        //         url: "https://developer.api.autodesk.com/oss/v2/buckets",
        //         headers: { 
        //             'Authorization': 'Bearer ' + access_token ,
        //         },
        //         dataType: 'json',
        //         contentType: 'application/json',
        //         data: JSON.stringify(data_bucket),
        //         success: function(response){
        //             console.log(response);
        //         },
        //         error: function (xmlHttpRequest, textStatus, errorThrown) {
        //             alert(textStatus, errorThrown);
        //        }
        //     });
        // }

        // getHubs() {
        //     $.ajax({
        //         type: "GET",
        //         url: "https://developer.api.autodesk.com/hq/v1/accounts/" + ACCOUNT_ID + "/projects",
        //         headers: { 'Authorization': 'Bearer ' + access_token },
        //         data: {
        //             scope: scopes
        //         },
        //         success: function (response) {
        //             console.log(response);
        //         },
        //         error: function (xmlHttpRequest, textStatus, errorThrown) {
        //             alert(textStatus, errorThrown);
        //         }
        //     });
        // },
        // uploadFile() {
        //     $.ajax({
        //         type: "PUT",
        //         url: "https://developer.api.autodesk.com/oss/v2/buckets/bucket1-tst/objects/rvtFile",
        //         headers: { 'Authorization': 'Bearer ' + access_token },
        //         data: {
        //             scope: scopes
        //         },
        //         success: function (response) {
        //             console.log(response);
        //         },
        //         error: function (xmlHttpRequest, textStatus, errorThrown) {
        //             alert(textStatus, errorThrown);
        //         }
        //     });
        // },
        onFileUpload(event){
            console.log(event.target.files[0]);
            formData.append("fileToUpload", event.target.files[0]);
            $.ajax({
                type: "PUT",
                url: "https://developer.api.autodesk.com/oss/v2/buckets/bucket1-tst/objects/file2.rvt",
                headers: { 
                    'Authorization': 'Bearer ' + access_token,
                    'Accept-Encoding': 'gzip, deflate'
                },
                processData: false,  // tell jQuery not to process the data
                contentType: 'application/octet-stream',
                data: formData,
                success: function (response) {
                    console.log(response);
                },
                error: function (xmlHttpRequest, textStatus, errorThrown) {
                    alert(textStatus, errorThrown);
                }
            });
        }, 
        getHubs() {
            var a = this;
            $.ajax({
                type: "GET",
                url: "https://developer.api.autodesk.com/oss/v2/buckets/bucket1-tst/objects",
                headers: { 'Authorization': 'Bearer ' + access_token },
                data: {
                    scope: scopes
                },
                success: function (response) {
                    console.log(response);
                    let encodeString = btoa(response.items[0].objectId);
                    encodeString = encodeString.replace(/\+/g, '-').replace(/\//g, '_').replace(/\=+$/, '');
                    CURRENT_URN_OBJ = encodeString;
                    console.log(encodeString);
                    a.startJob(encodeString);
                },
                error: function (xmlHttpRequest, textStatus, errorThrown) {
                    alert(textStatus, errorThrown);
                }
            });
        },
        startJob(urn){
            var data = {
                "input": {
                    "urn": urn,
                },
                "output": {
                    "force": "true",
                    "destination": {
                        "region": "us"
                    },
                    "formats": [
                        {
                            "type": "svf",
                            "views": [
                                "2d",
                                "3d"
                            ]       
                        }
                    ]
                }
            };
            $.ajax({
                type: "POST",
                url: "https://developer.api.autodesk.com/modelderivative/v2/designdata/job",
                headers: { 
                    'Authorization': 'Bearer ' + access_token,
                    'x-ads-force': 'true'
                },
                contentType: 'application/json',
                data: JSON.stringify(data),
                success: function (response) {
                    console.log(response);
                },
                error: function (xmlHttpRequest, textStatus, errorThrown) {
                    alert(textStatus, errorThrown);
                }
            });
        }, 
        getJobStatus() {
            $.ajax({
                type: "GET",
                url: "https://developer.api.autodesk.com/modelderivative/v2/designdata/"+CURRENT_URN_OBJ+"/manifest",
                headers: { 'Authorization': 'Bearer ' + access_token },
                data: {
                    scope: scopes
                },
                success: function (response) {
                    console.log(response);
                },
                error: function (xmlHttpRequest, textStatus, errorThrown) {
                    alert(textStatus, errorThrown);
                }
            });
        },
        // onFileUpload(event){
        //     console.log(event.target.files);
        //     this.selecetdFile = event.target.files[0];
        //     const reader = new FileReader();
        //     reader.onload = () => {
        //     this.imagePreview = reader.result;
        //     };
        //     reader.readAsDataURL(this.selecetdFile);
        //   }



        // // add assoc key values, this will be posts values
        // formData.append("file", this.file, this.getName());
        // formData.append("upload_file", true);

    });

    registry.add('tree_concepts', tree_concepts_widget);
});

