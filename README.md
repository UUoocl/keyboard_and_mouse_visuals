- [How it works](#how-it-works)
- [Required Software](#required-software)
- [Getting started](#getting-started)
  - [Download this repository](#download-this-repository)
  - [Turn on the OBS WebSocket Server](#turn-on-the-obs-websocket-server)
  - [Import Scene Collection](#import-scene-collection)
  - [User Interface.](#user-interface)
  - [Create your own Visualization](#create-your-own-visualization)
- [Examples](#examples)
  - [Key overlay](#key-overlay)
  - [Mouse overlay](#mouse-overlay)
  - [Follow and Zoom to Mouse](#follow-and-zoom-to-mouse)
- [Learn javaScript](#learn-javascript)


# keyboard and mouse visuals
Use javaScript to Visualize keyboard and mouse input in OBS.  
Create graphics to highlight mouse position and Key presses.  

If your learning to code to make art, use OBS to share your creative expressions through live streams, online meetings or recordings. 

The examples in this repository feature the javaScript libraries [P5.js](https://p5js.org/) and [Cables.gl](https://cables.gl/). Both are free and open source tools for making beautiful interactive content.

## How it works

1. OBS captures keyboard and mouse input that happens anywhere on your computer. 
2. Keyboard and Mouse events trigger an Advanced Scene Switcher macro that displays the event data in a Text Source.  
3. A Browser Source with javaScript listens for changes and renders the visualization


![image](https://github.com/user-attachments/assets/8336e25f-2731-449c-a2f5-56f463d57a16)


## Required Software

[OBS](https://obsproject.com/) and the following plug-ins are required.
- [Advanced Scene Switcher](https://github.com/WarmUpTill/SceneSwitcher/releases)
- [Move Transition](https://obsproject.com/forum/resources/move.913/)
- [Source Dock](https://obsproject.com/forum/resources/source-dock.1317/)
- [Source Clone](https://obsproject.com/forum/resources/source-clone.1632/)
- [Advanced Masks](https://obsproject.com/forum/resources/advanced-masks.1856/)
- [Composite Blur](https://obsproject.com/forum/resources/composite-blur.1780/)
- [Stroke Glow Shadow](https://obsproject.com/forum/resources/stroke-glow-shadow.1800/)

> [!NOTE] 
> 
> macOS Installing plug-in note:
>  1. After Downloading a plug-in, expand the .zip file and in the expanded folder click to open the installer for your Mac.
>  2. A warning will appear that Apple could not verify the plug-in.  Click the "Done" button
>
>![image](https://github.com/user-attachments/assets/ceef4d62-0e3c-4fd8-9faf-14099fda2c78)
>
>3. Go to System Settings, 
>    1. choose Privacy & Security settings. 
>    2. scroll to the bottom of the settings page.
>    3. click "Open Anyway" 
>
> ![image](https://github.com/user-attachments/assets/e0c393c0-0302-41ac-9ed6-7ceb22f796e7)
> 

## Getting started

### Download this repository
1. After installing OBS and the requisite plug-ins, download [this](https://github.com/UUoocl/keyboard_and_mouse_visuals) repository. 

![image](https://github.com/user-attachments/assets/6cfc3b41-d711-4b84-9618-c51fe3826b2b)

1. Extract the .zip download

### Turn on the OBS WebSocket Server

OBS includes a webSocket server.  The webSocket server will allow the Browser Source to receive the Keyboard and Mouse event messages. 

1. Turn on the WebSocKet Server, from the file menu select "Tools --> WebSocket Server Settings"
 ![image](https://github.com/user-attachments/assets/b38def9b-be32-41d7-a962-bb76c2bbdd36)

2. check the "Enable WebSocket server" setting

![image](https://github.com/user-attachments/assets/7cfc0075-b39e-47d7-8686-044d9426e216)

5. Click the "Show Connect Info Button" to get the WebSocket Server Password.
6. Navigate to the folder where extracted the "keyboard and mouse visuals" are saved. 
7. Open the file /browser_Sources/obs_webSocket_details/websocketDetails.js

  > [!TIP] 
	>Use a Text Editor, like [VS Code](https://code.visualstudio.com/), to open the file.  

8. Enter the WebSocket Server Password.
   - enter the password after "PW":" 
9.  Save the change to "websocketDetails.js"
### Import Scene Collection

Use the file "Key_and_Mouse_Visuals_Collection.json" to configure OBS .
- In OBS, on the file menu click "Scene Collection --> Import"

![image](https://github.com/user-attachments/assets/35d4b1e7-dbf1-4e11-b617-5adec4d180e4)

- navigate to the file "Key_and_Mouse_Visuals_Collection.json", in the downloaded folder.
- Change to the imported Scene Collection. "Scene Collection --> Key_and_Mouse_Visuals_Collection"

- OBS will ask where the local webpages are located.  

![image](https://github.com/user-attachments/assets/22dd38fa-7db9-4975-adb0-294c846f9e7a)

  - click the "Search Directory..." button
  - navigate to where this repo is saved on your computer.

### User Interface. 

The Source Dock Plug-in is used to display the Keyboard and Mouse  values.  Mouse Follow and Zoom controls allow switching the scene view.   
![image](https://github.com/user-attachments/assets/1c68fcd3-7aaf-4a3e-81c0-17e333f6941a)

> [!NOTE] Rearrange the docks however you'd like.  

### Create your own Visualization
    The repo includes a starter template to 
     - replace mouse input with eventListeners
     - add OBS WebSocket connection.  

## Examples
Attribution for the examples used in this repo
### Key overlay
 - [Space Type Generator](https://spacetypegenerator.com/stripes) "Stripes" by [Kiel Mutschelknaus](https://www.kielm.com/) 
  
![keyAndMouse00108162](https://github.com/user-attachments/assets/541bf569-4818-4227-9743-d4bbe5fbd87f)
 
### Mouse overlay
Example of mouse visualizations created with javaScript libraries.
 - cables.gl [Fast Fluid V2](https://cables.gl/p/J9WzcP)
   - [modified for OBS WebSocket Input](https://cables.gl/p/Z14eIm) 
  
  ![keyAndMouse00108000](https://github.com/user-attachments/assets/1ed4ad3d-c07d-454f-b3f3-2f477dc60df7)

- [Procedural 2d fish](https://cables.gl/p/ocCn6p)
  
   - [modified for OBS WebSocket Input](https://cables.gl/p/JQjuZp)
 
 - P5 js [soft body example](https://p5js.org/examples/math-and-physics-soft-body/)
  
### Follow and Zoom to Mouse
The Follow and Zoom to Mouse Visualizations are created using javaScript to control the OBS Plug-ins Advanced Mask and Move Transition. 

Follow Mouse

![keyAndMouse00108392](https://github.com/user-attachments/assets/1f6805b9-6f37-4967-b558-1a907b3e7683)

Zoom and Follow Mouse

![keyAndMouse00108707](https://github.com/user-attachments/assets/caf748be-94d6-4e4d-b176-da76e26661d6)

  
## Learn javaScript
Recommendations for learning javascript with a creative coding approach
- https://thecodingtrain.com/
- https://www.pattvira.com/
- [Intro to Cables GL](https://www.youtube.com/playlist?list=PLYimpE2xWgBveaPOiV_2_42kZEl_1ExB0)
