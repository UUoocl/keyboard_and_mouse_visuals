//Establish Connection for OBS browser sources to the OBS Web Socket Server(WSS).
//1. Check if the URL query parameters includes WSS details
//2. Check if the browser local storage includes WSS details
//3. listen for a WSS details event message
//4. listen for a button press to start
//5. Check if a websocket details js variable has been defined
//6. Check if css variables are defined

let obsWss = new OBSWebSocket();

window.addEventListener('DOMContentLoaded', async function() {
  //obs css added after page load
  setTimeout(async () => {
          
  obsWss.connected = false;
      console.log("obsConnect.js loaded");
  //get URL parameters
  const params = new URLSearchParams(window.location.search);
  //get local storage
  const localStorageWssDetails = localStorage.getItem('wssDetails');
  // console.log("varWebsocketDetails",typeof varWebsocketDetails,varWebsocketDetails);
  let cssVarWSSdetails = getComputedStyle(document.body).getPropertyValue('--websocket-details');  
  // const varWebsocketDetails = typeof websocketDetails;
  // console.log("cssVarWSSdetails",typeof cssVarWSSdetails,cssVarWSSdetails);
  switch(true){
    //1. check if the URL has WSS details
    case params.has("wsspw"):
        wssDetails = {
          IP: params.get("wssip"),
          PORT: params.get("wssport"),
          PW: params.get("wsspw"),
        };
        const paramsConnected = await connectOBS(wssDetails);    
        console.log("paramsConnected",paramsConnected)
        if(paramsConnected === 'connected'){
          console.log("paramsConnected",paramsConnected)
          break;}
    //2. check local storage for OBS Web Socket Details
    case (localStorageWssDetails !== null):
      console.log("try saved websocket details")
      const localStorageConnected = await connectOBS(JSON.parse(window.localStorage.getItem('wssDetails')))    
      if(localStorageConnected === 'connected'){
        console.log("localStorageConnected",localStorageConnected)
        break;}
    //5. check if the variable named websocketDetails is defined
    case (typeof websocketDetails !== 'undefined' && websocketDetails !== undefined):
      const localVarConnected = await connectOBS(websocketDetails);
      console.log("try websocketDetails variable",localVarConnected)
      if(localVarConnected === 'connected'){break;}
    //6. check if css variables are defined
    case (getComputedStyle(document.body).getPropertyValue('--websocket-details') != 'undefined'):
      console.log("cssVarWSSdetails",getComputedStyle(document.body).getPropertyValue('--websocket-details'))
      const cssVarWSSdetails = JSON.parse(getComputedStyle(document.body).getPropertyValue('--websocket-details'));
      console.log("cssVarWSSdetails",cssVarWSSdetails)
      const cssVarConnected = await connectOBS(cssVarWSSdetails);
      console.log("try css websocketDetails",cssVarConnected)
      if(cssVarConnected === 'connected'){
        console.log("cssVarConnected",cssVarConnected)
        break;}
  }
  }, 100);
})

//3. get web socket details from a message
window.addEventListener(`ws-details`, async function (event) {
  //event wss details
  console.log("message received: ", event)
  if(event.detail.hasOwnProperty('wssDetails')){
    await connectOBS(event.detail.wssDetails);
  }
})

//4. listen for a button press to start 
async function wsConnectButton() {
  //change to this.
  wssDetails = {
    IP: document.getElementById("IP").value,
    PORT: document.getElementById("Port").value,
    PW: document.getElementById("PW").value,
  };

  await connectOBS(wssDetails).then(async (result) => {
    if (result === "failed") {
      document.getElementById("WSconnectButton").style.background = "#ff0000";
    }
  });
}

//connect to OBS web socket server
async function connectOBS(wssDetails) {
  console.log("connectOBS", wssDetails);
  try {
    //avoid duplicate connections
    await disconnect();

    //connect to OBS Web Socket Server
    const { obsWebSocketVersion, negotiatedRpcVersion } = 
    await obsWss.connect(`ws://${wssDetails.IP}:${wssDetails.PORT}`,wssDetails.PW,{rpcVersion: 1,});
    console.log(`Connected to server ${obsWebSocketVersion} (using RPC ${negotiatedRpcVersion})`);
    
    localStorage.setItem("wssDetails", JSON.stringify(wssDetails));  

    return "connected";
  } catch (error) {
    console.error("Failed to connect", error.code, error.message);
    //localStorage.setItem("wssDetails",null)
    return "failed";
  }
  //console.log(`ws://${wssDetails.IP}:${wssDetails.PORT}`);
}

// window.addEventListener('storage', function(e) {
//   if (e.key === 'wssDetails') {
//     const newWssDetails = JSON.parse(e.newValue);
//     connectOBS(newWssDetails);
//   }})

async function disconnect () {
  try{
    await obsWss.disconnect()
    console.log("disconnected")
    obsWss.connected = false
  } catch(error){
    console.error("disconnect catch",error)
  }
}

obsWss.on('ConnectionOpened', () => {
  console.log('Connection to OBS WebSocket successfully opened');
  obsWss.status = "connected";
});

obsWss.on('ConnectionClosed', () => {
  console.log('Connection to OBS WebSocket closed');
  obsWss.status = "disconnected";
});

obsWss.on('ConnectionError', err => {
  console.error('Connection to OBS WebSocket failed', err);
});

obsWss.on("Identified", async (data) => {
  obsWss.connected = true;
  console.log("OBS WebSocket successfully identified", data);
  
  // //send websocket details to obs-browser sources
  // const wssDetails = JSON.parse(localStorage.getItem('wssDetails'));
  // await obsWss.call("CallVendorRequest", {
  //     vendorName: "obs-browser",
  //     requestType: "emit_event",
  //     requestData: {
  //         event_name: "ws-details",
  //         event_data: { wssDetails },
  //     },
  // });

});

obsWss.on("error", (err) => {
  console.error("Socket error:", err);
});

//refresh all browser connections in all scenes, when the "Browser Source Connection Manager" source is made invisible
// window.addEventListener('obsSourceActiveChanged', function(event) {
//       console.log("obsSourceActiveChanged",event)
//       if(event.detail.sourceName === "Browser Source Connection Manager" && event.detail.visible === false){
//         console.log("rtc_target is visible - refresh browsers")
//         // refreshOBSbrowsers()
//       }
//   }

async function refreshOBSbrowsers(){
  console.log("refreshOBSbrowsers")
//remove local storage wss details to force a reconnect
  const localStorageWssDetails = localStorage.getItem('wssDetails');
  localStorage.removeItem('wssDetails');

//refresh all browser sources
  let browserSources = await obsWss.call("GetInputList",{inputKind: "browser_source"})

  for(let i=0; i<browserSources.inputs.length; i++){
    await obsWss.call("PressInputPropertiesButton", {
        inputUuid: browserSources.inputs[i].inputUuid,
        propertyName: "refreshnocache",
      });
    }
    
  //connect again
  setTimeout( async () => {
    await connectOBS(localStorageWssDetails); 
    console.log("All browser sources refreshed")
  }, 500);
}