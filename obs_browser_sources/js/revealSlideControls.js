var currentSlideAttributes, 
  currentfragment, 
  currentEvent, 
  comparisonOp,
  targetValue;
  
  //create an array of all the Custom Event Functions
  const customEventFunctions = getCustomFunctionNames("Event");
  const customSlideAttributeFunctions = getCustomFunctionNames("SlideAttribute");

  function getCustomFunctionNames(type){
    const functionNames = [];
    for (const property in window) {
      if (typeof window[property] === 'function' && property.startsWith(`custom${type}`)) {
        functionNames.push(property);
      }
    }
    return functionNames;
  }
    
  console.log(customEventFunctions); 
  console.log(customSlideAttributeFunctions); 
  
  //If the CustomEvent is in the customEvent array, then run the matching function
  obs.on("CustomEvent", async function (event) {
    console.log("CustomEvent Received",event)
    if (customEventFunctions.includes(`customEvent_${event.event_name}`)) {
      //console.log("CustomEvent found")
      window[`customEvent_${event.event_name}`]();
    }
  });

function customEvent_nextSlide(){
  Reveal.next();
}

function customEvent_previousSlide(){
  Reveal.prev();
}

//Reveal Slide events Slide change started or Ended, Fragment shown or hidden

//Reveal Slide transition started https://revealjs.com/events/#slide-changed
Reveal.on('slidechanged', async (event) => {
  //get on exit attributes
    console.log(event)
    slideAttributeFunctions(event, "Exit")
    sendNotes()
    
})

  //Reveal Slide Transition ended https://revealjs.com/events/#slide-transition-end
Reveal.on('slidetransitionend', async (event) => {
  //get on exit attributes
    console.log(event)
    slideAttributeFunctions(event, "Entrance")
})

//!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
//create fragment attribute actions
Reveal.on('fragmentshown', (event) => {
  console.log(event)
  // const dataAttr = JSON.parse(JSON.stringify(event.previousSlide.dataset));
  event.fragment.dataset.fun = "coding"
  const dataAttr = {...event.fragment.dataset};
  console.log(dataAttr)
  
  for (let [key, value] of Object.entries(dataAttr)) {
      if(key){
          console.log(`Key found ${key}, with value ${value}`);
      }
  }
})

//Loop through each slide attribute and run any matches
function slideAttributeFunctions(slideEvent, eventType){
    currentSlideAttributes = {...slideEvent.previousSlide.dataset};
    //console.log(currentSlideAttributes, typeof currentSlideAttributes)
    for (const [attribute, value] of Object.entries(currentSlideAttributes)){
      //console.log("attribute",attribute, value)
      const attr = attribute.replace(eventType,"")
      if(customSlideAttributeFunctions.includes(`customSlideAttribute_${attr}`)){
        window[`customSlideAttribute_${attr}`](value);
      }
    }
  }

  //Switch to Scene
  function customSlideAttribute_scene(scene){
    console.log(`scene found ${scene}`)
    obs.call('SetCurrentProgramScene', {sceneName: `scene|||${scene}`})
  }
  
  //Enable Source in Camera Scene 
  async function customSlideAttribute_camera(cameraView){
    console.log(`camera found ${cameraView}`)
    let cameraSources = await obs.call("GetSceneItemList", { sceneName: "Camera" });
    cameraSources.sceneItems.forEach(async (source) => {
    if (source.sourceName === cameraView ) {
      await obs.call("SetSceneItemEnabled", {
          sceneName: "Camera",
          sceneItemId: source.sceneItemId,
          sceneItemEnabled: true
        });
      } 
    if (source.sourceName !== cameraView){
      await obs.call("SetSceneItemEnabled", {
          sceneName: "Camera",
          sceneItemId: source.sceneItemId,
          sceneItemEnabled: false
        });
      }
    });
  }

    //Call Apple ShortCut
   function customSlideAttribute_shortcutExit(shortCut){
      console.log("exit shortcut found", shortCut)
      const shortcutName = JSON.stringify(shortCut)
      console.log(shortcutName)
      obs.call("BroadcastCustomEvent", {
        eventData: {
          event_name: `run-shortcut`,
          shortcut_name: shortcutName,
        },
      });
  }

  //use PTZ value to change slide
  async function customSlideAttribute_ptzListen(){
    console.log("starting PTZ value")
    listenForPTZ = true;
    comparisonOp = currentSlideAttributes.ptzListen.substr(0,1)
    targetValue = currentSlideAttributes.ptzListen.substr(1)
    window.addEventListener('ptz-message', ptzTrigger);
      
    async function ptzTrigger(event) {
      console.log("ptz event!",event) 
      ptzObj = JSON.parse(event.detail.ptzMessage)
      if(comparisonOp === "<" && ptzObj.pan < targetValue){
        Reveal.next();
        window.removeEventListener('ptz-message', ptzTrigger);
      }
      console.log(`if ${ptzObj.pan} ${comparisonOp} ${targetValue}`)
      if(comparisonOp === ">" && ptzObj.pan > targetValue){
        Reveal.next();
        window.removeEventListener('ptz-message', ptzTrigger);
    }
  }
  }

    //setCurrentSlideAttribute(event,"key","value")
    //console.log(currentSlideAttributes)
    
    //for (let [key, value] of Object.entries(currentSlideAttributes)) {
      //  if(key){
       //     console.log(`Key found ${key}, with value ${value}`);
        //}
   // }

   async function sendNotes(){
    let slideNotes = await Reveal.getSlideNotes()
    //let slideNotes = "Reveal.getSlideNotes()"
    console.log("New Notes function",slideNotes)
    console.log(typeof slideNotes)
    console.log(slideNotes)
    console.log(slideNotes.length)

    //send notes to text source teleprompter
    await obs.call("SetInputSettings", {
      inputName: "Slide Notes Text",
      inputSettings: {
        text: slideNotes.replace(/<[^>]*>/g, '')
      }
    });

    //send notes to browser teleprompter
    obs.call("CallVendorRequest", {
        vendorName: "obs-browser",
        requestType: "emit_event",
        requestData: {
            event_name: "slideChangeResult",
            event_data: { 
              app: "reveal",
              slideNotes: `${JSON.stringify(slideNotes)}`
            },
        },
    });

    //get scroll speed 
    
    const teleprompterSpeed = await getTeleprompterSpeed()
    
    console.log("speed", teleprompterSpeed)
    //Reset the text source teleprompter
    await obs.call("SetSourceFilterSettings", {
      sourceName: "Slide Notes Text",
      filterName: "Scroll",
      filterSettings: {
        speed_y: 0
      }
    })
    .then(
      setTimeout(async () => {
        await obs.call("SetSourceFilterSettings", {
          sourceName: "Slide Notes Text",
          filterName: "Scroll",
          filterSettings: {
            speed_y: teleprompterSpeed
          }
        });
      }, 1000)
    );
  }

  async function getTeleprompterSpeed() {
    let speed = await obs.call("GetSourceFilter", {
        sourceName: "Slide Notes Text",
        filterName: "Scroll"
    });
    console.log("speed",speed)
    return speed.filterSettings.speed_y;
    //document.getElementById("speedValue").value = teleprompterSpeed;
}

  //midi input
  window.addEventListener("midi-message", function (event) {
    console.log("midi event",event)
    let midiData = JSON.stringify(JSON.parse(event.detail.midiEvent).data);
    console.log("midi data", typeof midiData, midiData)
    console.log(`midiData ${midiData}===[144,107,127]`,midiData ==="[144,107,127]")
    switch (midiData) {
      //Get Slide details
      // case "[144,105,127]":
      //   setCommandText(`shortcuts run "Keynote_currentSlide_GUM" &`)
      //   break;
      //Next Slide
      case "[176,23,127]":
      case "[144,107,127]":
        Reveal.next();
        break;
      //Previous Slide
      case "[176,22,127]":
      case "[144,106,127]":
        Reveal.prev();
        break;

      //Camera Pan
      case midiData.startsWith("[176,48,") ? midiData : '':
        console.log("volume fader moved")
        //get fader value 0 - 127
        let panFader = JSON.parse(midiData)[2]
        console.log("fader value: ", panFader)
        //if fader is divisible by 8 then send the camera command 
        if (panFader % 1 === 0) {
          //scale fader to camera pan -468000 to +468000. 
          ptzPan = Math.round(((7370.07874 * panFader) - 468000))
          //send pan command to camera 0
          if (!ptzWaiting){
            ptzWaiting = true
            setTimeout(() => {
////////////send the command to the obsidian whimsy script
              setCommandText(`Applications/Utilities/uvc-util -I 0 -s pan-tilt-abs="{${ptzPan},${ptzTilt}}"`);
              ptzWaiting = false
            }, 300); 
          }
        }
        break;
      //Camera Tilt
      case midiData.startsWith("[176,49,") ? midiData : '':
        let tiltFader = JSON.parse(midiData)[2]
        console.log("fader value: ", tiltFader)
        if (tiltFader % 1 === 0) {
          //scale fader to camera tilt -324000 to +324000. 
          ptzTilt = Math.round(((5102.362205 * tiltFader) - 324000))
          if (!ptzWaiting){
            ptzWaiting = true
            setTimeout(() => {
              setCommandText(`Applications/Utilities/uvc-util -I 0 -s pan-tilt-abs="{${ptzPan},${ptzTilt}}"`);
              ptzWaiting = false
            }, 300); 
          }
        }
        break;
      //Camera Zoom 
      case midiData.startsWith("[176,50,") ? midiData : '':
        let zoomFader = JSON.parse(midiData)[2]
        console.log("fader value: ", zoomFader)
        if (zoomFader % 4 === 0) {
          //scale fader to camera zoom 0 - 100. 
          ptzZoom = Math.round(((zoomFader + 1) / 128) * 100)
          console.log("zoom value: ", ptzZoom)
          //send pan command to camera 0
          setCommandText(`Applications/Utilities/uvc-util -I 0 -s zoom-abs="${ptzZoom}"`)
        }
        break;
      //Camera Focus 
      case midiData.startsWith("[176,51,") ? midiData : '':
        let focusFader = JSON.parse(midiData)[2]
        console.log("fader value: ", focusFader)
        if (focusFader % 4 === 0) {
          //scale fader to camera zoom 0 - 100. 
          ptzFocus = Math.round(((focusFader + 1) / 128) * 100)
          console.log("focus value: ", ptzFocus)
          //send pan command to camera 0
          setCommandText(`Applications/Utilities/uvc-util -I 0 -s auto-focus="false"`)
          setCommandText(`Applications/Utilities/uvc-util -I 0 -s focus-abs="${ptzFocus}"`)
        }
        break;
      //Auto focus on/off
      case "[144,103,127]":
        setCommandText(`Applications/Utilities/uvc-util -I 0 -s auto-focus="true"`)
        break;
    }
  });

      //gamepad
      window.addEventListener("gamepad-message", function (event) {
        let gamepadData = JSON.parse(event.detail.gamepadEvent);
        //Next slide code
        if (gamepadData.buttons[1].value === 1) {
          Reveal.next()
        }
        //Previous slide code
        if (gamepadData.buttons[3].value === 1) {
          Reveal.prev()
        }
      });
      
      //mediapipe pose
      window.addEventListener("pose-landmarks", function (event) {
        if(event.detail.poseLandmarkerResult[16].y < event.detail.poseLandmarkerResult[0].y && poseNextControl ==='off'){
          Reveal.next()
          poseNextControl = 'on';
        }
        if(event.detail.poseLandmarkerResult[16].y > event.detail.poseLandmarkerResult[0].y){
          poseNextControl = "off";
        }
        if(event.detail.poseLandmarkerResult[15].y < event.detail.poseLandmarkerResult[0].y && posePreviousControl ==='off'){
          Reveal.prev()
          posePreviousControl = 'on';
        }
        if(event.detail.poseLandmarkerResult[15].y > event.detail.poseLandmarkerResult[0].y){
          posePreviousControl = "off";
        }
      });  
      
      //ZoomOSC 
      //OSC to Websocket https://github.com/UUoocl/OSC_to_OBS_WebSocket  
      window.addEventListener("zoomOSC-message", function (event) {
        console.log(event)
        let zoomMessage = JSON.parse(JSON.parse(JSON.stringify(event.detail.webSocketMessage)))
        console.log(typeof zoomMessage, zoomMessage)
        console.log(zoomMessage[0])
        //Next slide on hand raised
        if (zoomMessage[0].includes("/handRaised")) {
          Reveal.next()
        }
      });