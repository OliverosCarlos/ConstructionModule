odoo.define('construction.extension_viewer_select', (require) => {
  "use strict";

  const Utils = require('construction.forge_utils');
  var utils = new Utils();

  function MyExtension(viewer, options) {
    Autodesk.Viewing.Extension.call(this, viewer, options);
  }

  MyExtension.prototype = Object.create(Autodesk.Viewing.Extension.prototype);
  MyExtension.prototype.constructor = MyExtension;

  MyExtension.prototype.onSelectionEvent = function (event) {
    var currSelection = this.viewer.getSelection();
    console.log(event);
    console.log( utils.getModelItems(event.dbIdArray[0]) );
    var properties = utils.getModelItems(event.dbIdArray[0])[0].properties;

    var nodeVolume = document.createElement("LI");                 // Create a <li> node
    var nodeArea = document.createElement("LI");
    var nodeLength = document.createElement("LI");

    var textNodeVolume = document.createTextNode('Volumen: '+properties.Dimensions.Volume);
    var textNodeArea = document.createTextNode('Area: '+properties.Dimensions.Area);
    var textNodeLength = document.createTextNode('Longitud: '+properties.Dimensions.Length);

    nodeVolume.appendChild(textNodeVolume);
    nodeArea.appendChild(textNodeArea);
    nodeLength.appendChild(textNodeLength);

    document.getElementById("stage-model-object-properties").appendChild(nodeVolume); 
    document.getElementById("stage-model-object-properties").appendChild(nodeArea); 
    document.getElementById("stage-model-object-properties").appendChild(nodeLength); 
  };

  MyExtension.prototype.load = function () {
    // alert('MyExtension is loaded!');

    var viewer = this.viewer;

    this.onSelectionBinded = this.onSelectionEvent.bind(this);
    this.viewer.addEventListener(Autodesk.Viewing.SELECTION_CHANGED_EVENT, this.onSelectionBinded);

    return true;
  };

  MyExtension.prototype.unload = function () {
    alert('MyExtension is now unloaded!');
    this.viewer.removeEventListener(Autodesk.Viewing.SELECTION_CHANGED_EVENT, this.onSelectionBinded);
    this.onSelectionBinded = null;
    return true;
  };

  Autodesk.Viewing.theExtensionManager.registerExtension('MyExtension', MyExtension);
});

