//hotkeys
let refreshOBSbrowsers_HK

obsWss.on("Identified", async (data) => {
  obsWss.connected = true;
  console.log("OBS WebSocket successfully identified", data);

  await obsWss.call("GetInputSettings", { inputName: "Connection Manager Hotkeys Settings"})
  .then((result) => {
      const hotkeys = JSON.parse(`{${result.inputSettings.text}}`);
      console.log("Hotkeys from Settings Source:", hotkeys);
      refreshOBSbrowsers_HK = hotkeys.refreshOBSbrowsers_HK;
    });
});
    
obsWss.on("InputSettingsChanged", async function (event) {
    switch (event.inputName) {            
        case 'keyHotkey':
            console.log(event);
        switch (event.inputSettings.text) {
            case ' ':
                break;
            case refreshOBSbrowsers_HK: 
                refreshOBSbrowsers();
                break;
            }
        default:
            break;
            }
        })