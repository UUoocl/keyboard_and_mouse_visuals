//after connecting to OBS get the Scenes and Sources
let collection = new Object
let displayItems = new Object;

//Get OBS Collection
async function getOBScollection() {
    //create collection object
    collection.scenes = [];
    //get scenes from OBS
    collection = await obs.call("GetSceneList");

    //get scene and sources
    for (let scene = 0; scene < collection.scenes.length; scene++) {
        const sources = await obs.call("GetSceneItemList", { sceneName: collection.scenes[scene].sceneName })

        //get the source settings
        for (let source = 0; source < sources.sceneItems.length; source++) {
            //if source is group, get group items
            if (sources.sceneItems[source].isGroup === true) {
                const groupSources = await obs.call("GetGroupSceneItemList", { sceneName: sources.sceneItems[source].sourceName })
                for (let groupSource = 0; groupSource < groupSources.sceneItems.length; groupSource++) {
                    if (groupSources.sceneItems[groupSource].sourceType === 'OBS_SOURCE_TYPE_INPUT') {
                    const groupSourceSettings = await obs.call("GetInputSettings", { inputName: groupSources.sceneItems[groupSource].sourceName })
                    //if input kind  == "screen_capture" get special settings
                    if (groupSourceSettings.inputKind === "screen_capture") {
                        groupSourceSettings.inputSettings.displayName = displayItems[groupSourceSettings.inputSettings.display_uuid]?.itemName || "Unknown Display @ -0,-0";
                        groupSourceSettings.inputSettings.monitorPositionX = groupSourceSettings.inputSettings.displayName.split(" @ ")[1].split(",")[0];
                        groupSourceSettings.inputSettings.monitorPositionY = groupSourceSettings.inputSettings.displayName.split(" @ ")[1].split(",")[1];
                        groupSourceSettings.inputSettings.monitorWidth = groupSourceSettings.inputSettings.displayName.split(": ")[1].split(" @ ")[0].split("x")[0];
                        groupSourceSettings.inputSettings.monitorHeight = groupSourceSettings.inputSettings.displayName.split(": ")[1].split(" @ ")[0].split("x")[1];
                    }
                    groupSources.sceneItems[groupSource] = Object.assign(groupSources.sceneItems[groupSource], groupSourceSettings)
                    }
                }
                //add group sources to the source object
                sources.sceneItems[source] = Object.assign(sources.sceneItems[source], arrayToObject(groupSources.sceneItems, 'sourceName'))
                //sources.sceneItems[source] = Object.assign(sources.sceneItems[source], groupSources)
            }
            if (sources.sceneItems[source].sourceType === 'OBS_SOURCE_TYPE_INPUT') {
                const sourceSettings = await obs.call("GetInputSettings", { inputName: sources.sceneItems[source].sourceName })
                //if input kind  == "screen_capture" get special settings
                if (sourceSettings.inputKind === "screen_capture") {
                    sourceSettings.inputSettings.displayName = displayItems[sourceSettings.inputSettings.display_uuid]?.itemName || "Unknown Display @ -0,-0";
                    sourceSettings.inputSettings.monitorPositionX = Number(sourceSettings.inputSettings.displayName.split(" @ ")[1].split(",")[0]);
                    sourceSettings.inputSettings.monitorPositionY = Number(sourceSettings.inputSettings.displayName.split(" @ ")[1].split(",")[1]);
                    sourceSettings.inputSettings.monitorWidth = Number(sourceSettings.inputSettings.displayName.split(": ")[1].split(" @ ")[0].split("x")[0]);
                    sourceSettings.inputSettings.monitorHeight = Number(sourceSettings.inputSettings.displayName.split(": ")[1].split(" @ ")[0].split("x")[1]);
                }
                sources.sceneItems[source] = Object.assign(sources.sceneItems[source], sourceSettings)
            }
        }
        //add the sources and settings to the scene object
        // collection.scenes[scene] = Object.assign(collection.scenes[scene], reducedSources)
        collection.scenes[scene] = Object.assign(collection.scenes[scene], arrayToObject(sources.sceneItems, 'sourceName'))
    }
    //add scenes to collection object with scene name as key
    collection.scenes = arrayToObject(collection.scenes, 'sceneName')
    return "collection complete";
}

//Array of objects to object of objects with source name as key
function arrayToObject(array, keyField) {
    return array.reduce((obj, item) => {
        obj[item[keyField]] = item;
        //console.log(obj);
        return obj;
    }, {});
}  

//get display items
async function getDisplayItems() {
    const displays = await obs.call("GetInputList", {inputKind: "screen_capture"})
    console.log(displays.inputs)
    if(displays.inputs.length>0){
        displayItems =  await obs.call("GetInputPropertiesListPropertyItems",{ inputName: displays.inputs[0].inputName, propertyName: "display_uuid"})
        displayItems = arrayToObject(displayItems.propertyItems, 'itemValue')
    }
}