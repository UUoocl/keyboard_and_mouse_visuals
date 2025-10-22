import asyncio
import argparse
from simpleobsws import WebSocketClient, Request, IdentificationParameters
from pynput import mouse

# Default values (can be overridden by command line arguments)
DEFAULT_HOST = 'localhost'
DEFAULT_PORT = 4455
DEFAULT_PASSWORD = 'your_obs_websocket_password'  # Replace with your actual password
DEFAULT_TEXT_SOURCE_NAME = 'MouseHotKey'  # Replace with the name of your text source in OBS

async def update_obs_text(ws, text, text_source_name):
    """Updates the OBS text source with the specified text."""
    try:
        payload = {
            'inputName': text_source_name,
            'inputSettings': {'text': text}
        }
        request = Request('SetInputSettings', payload)
        asyncio.create_task(ws.call(request)) # Run call without waiting
    except Exception as e:
        print(f"Error updating OBS text: {e}")

async def main(host, port, password, text_source_name):

    parameters = IdentificationParameters(ignoreNonFatalRequestChecks = False)

    """Connects to OBS and listens for mouse clicks."""
    ws = WebSocketClient(url=f'ws://{host}:{port}', password=password, identification_parameters = parameters)
    try:
        await ws.connect()
        await ws.wait_until_identified() # Wait for the identification handshake to complete
  
        def on_click(x, y, button, pressed):
            """Callback function for mouse clicks."""
            if pressed:
                if button == mouse.Button.left:
                    text_to_send = "MB1"
                elif button == mouse.Button.right:
                    text_to_send = "MB2"
                elif button == mouse.Button.middle:
                    text_to_send = "MB3"
                else:
                    return  # Ignore other buttons

                asyncio.run(update_obs_text(ws, text_to_send, text_source_name)) # Schedule the text update

        # Start the mouse listener
        with mouse.Listener(on_click=on_click) as listener:
            print("Listening for mouse clicks...") 
            listener.join()

    except Exception as e:
        print(f"Connection error: {e}")
    finally:
        await ws.disconnect()
        print("Disconnected from OBS")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="OBS WebSocket Mouse Click Listener")
    parser.add_argument("--host", type=str, default=DEFAULT_HOST, help="OBS WebSocket host")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="OBS WebSocket port")
    parser.add_argument("--password", type=str, default=DEFAULT_PASSWORD, help="OBS WebSocket password")
    parser.add_argument("--text_source_name", type=str, default=DEFAULT_TEXT_SOURCE_NAME, help="OBS Text Source Name")

    args = parser.parse_args()

    asyncio.run(main(args.host, args.port, args.password, args.text_source_name))