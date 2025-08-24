//Connect an OBS browser source to the OBS Web Socket Server(WSS).
//1. Check if the browser local storage includes WSS details
//2. listen for local storage change event

var obs = new OBSWebSocket();

window.addEventListener('DOMContentLoaded', async function() {        
  obs.connected = false;
      console.log("obsConnect.js loaded");
  //get local storage
  const localStorageWssDetails = localStorage.getItem('wssDetails');
  
  switch(true){
    case (localStorageWssDetails !== null):
      console.log("try saved websocket details")
      const localStorageConnected = await connectOBS(JSON.parse(window.localStorage.getItem('wssDetails')))    
      if(localStorageConnected === 'connected'){break;}
  }
})

//2. get web socket details from a local storage event
window.addEventListener('storage', function(e) {
  console.log("storage event",e)
  if (e.key === 'wssDetails' && e.newValue !== null) {
    const newWssDetails = JSON.parse(e.newValue);
    connectOBS(newWssDetails);
  }
})

//connect to OBS web socket server
async function connectOBS(wssDetails) {
  console.log("connectOBS", wssDetails);
  try {
    //avoid duplicate connections
    await disconnect();

    //connect to OBS Web Socket Server
    const { obsWebSocketVersion, negotiatedRpcVersion } = 
    await obs.connect(`ws://${wssDetails.IP}:${wssDetails.PORT}`,wssDetails.PW,{rpcVersion: 1,});
    console.log(`Connected to server ${obsWebSocketVersion} (using RPC ${negotiatedRpcVersion})`);
    
    return "connected";
  } catch (error) {
    console.error("Failed to connect", error.code, error.message);
    //localStorage.setItem("wssDetails",null)
    return "failed";
  }
  //console.log(`ws://${wssDetails.IP}:${wssDetails.PORT}`);
}

async function disconnect () {
  try{
    await obs.disconnect()
    console.log("disconnected")
    obs.connected = false
  } catch(error){
    console.error("disconnect catch",error)
  }  
}

obs.on('ConnectionOpened', () => {
  console.log('Connection to OBS WebSocket successfully opened');
  obs.status = "connected";
});

obs.on('ConnectionClosed', () => {
  console.log('Connection to OBS WebSocket closed');
  obs.status = "disconnected";
});

obs.on('ConnectionError', err => {
  console.error('Connection to OBS WebSocket failed', err);
});

obs.on("Identified", async (data) => {
  obs.connected = true;
  console.log("OBS WebSocket successfully identified", data);

});

obs.on("error", (err) => {
  console.error("Socket error:", err);
});