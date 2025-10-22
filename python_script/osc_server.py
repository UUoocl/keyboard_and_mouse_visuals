import obspython as obs
import json
from pythonosc import udp_client
from pythonosc import dispatcher
from pythonosc import osc_server
import threading

# Defaults
DEFAULT_SERVER_IP = "127.0.0.1"
DEFAULT_SERVER_PORT = 12345
DEFAULT_TEXT_SOURCE_RECEIVE = "OSC Client {} Receive"
DEFAULT_TEXT_SOURCE_SEND = "OSC Client {} Send"
DEFAULT_OSC_ADDRESS = ""
DEFAULT_TEXT_SOURCE_SETTINGS = "Client Settings Output"
DEFAULT_NUM_CLIENTS = 5  # Hardcoded number of clients
DEFAULT_SCENE_NAME = "Inputs"

# Global variables
server_ip = DEFAULT_SERVER_IP
server_port = DEFAULT_SERVER_PORT
server = None
server_thread = None
server_running = False
clients = []  # List to hold client dictionaries
text_source_settings_name = DEFAULT_TEXT_SOURCE_SETTINGS
scene_name = DEFAULT_SCENE_NAME
settings = None  # OBS settings
num_clients = 5

source_signal_handlers = {}


def script_description():
    return "Receives OSC messages and sends them to a text source in JSON format. Includes Start/Stop Server buttons and a UI for adding/editing 5 hardcoded clients. Writes client settings to a text source."


def script_defaults(settings):
    obs.obs_data_set_default_string(settings, "server_ip", DEFAULT_SERVER_IP)
    obs.obs_data_set_default_int(settings, "server_port", DEFAULT_SERVER_PORT)
    obs.obs_data_set_default_string(settings, "text_source_settings", DEFAULT_TEXT_SOURCE_SETTINGS)
    
    obs.obs_data_set_default_int(settings, "number_of_clients", DEFAULT_NUM_CLIENTS)

    for i in range(DEFAULT_NUM_CLIENTS):
        obs.obs_data_set_default_string(settings, f"client_ip_{i}", "")  # Default to blank IP
        obs.obs_data_set_default_int(settings, f"client_port_{i}", 45678)
        obs.obs_data_set_default_string(settings, f"text_source_receive_{i}", DEFAULT_TEXT_SOURCE_RECEIVE.format(i+1))
        obs.obs_data_set_default_string(settings, f"text_source_send_{i}", DEFAULT_TEXT_SOURCE_SEND.format(i + 1))
        obs.obs_data_set_default_string(settings, f"osc_address_{i}", "")


def script_properties():
    props = obs.obs_properties_create()
    obs.obs_properties_add_text(props, "server_ip", "Server IP Address", obs.OBS_TEXT_DEFAULT)
    obs.obs_properties_add_int(props, "server_port", "Server Port", 1, 65535, 1)

    obs.obs_properties_add_int(props, "number_of_clients", "number_of_clients", 1, 10, 1)
    
    obs.obs_properties_add_text(props, "text_source_settings", "Client Settings Text Source", obs.OBS_TEXT_DEFAULT)
    obs.obs_properties_add_text(props, f"server blank", "-----", obs.OBS_TEXT_DEFAULT)

    for i in range(num_clients):
        obs.obs_properties_add_text(props, f"client_ip_{i}", f"Client {i+1} IP Address", obs.OBS_TEXT_DEFAULT)
        obs.obs_properties_add_int(props, f"client_port_{i}", f"Client {i+1} Port", 1, 65535, 1)
        obs.obs_properties_add_text(props, f"text_source_receive_{i}", f"Client {i+1} Text Source Receive Name", obs.OBS_TEXT_DEFAULT)
        obs.obs_properties_add_text(props, f"text_source_send_{i}", f"Client {i + 1} Text Source Send Name", obs.OBS_TEXT_DEFAULT)
        obs.obs_properties_add_text(props, f"osc_address_{i}", f"Client {i + 1} OSC Address", obs.OBS_TEXT_DEFAULT)
        obs.obs_properties_add_text(props, f"blank {i}", "-----", obs.OBS_TEXT_DEFAULT)

    obs.obs_properties_add_button(props, "start_server", "Start Server", start_server_callback)  # Add Start button
    obs.obs_properties_add_button(props, "stop_server", "Stop Server", stop_server_callback)  # Add Stop button
    return props


def source_signal_callback(calldata):
    """
    Signal callback for text source updates.
    message format
    {"address": "/address/filter/", "arguments": ["Arg0","Argument1"]}
    """
    
    try:
        source = obs.calldata_source(calldata,"source")
        source_name = obs.obs_source_get_name(source)

        # find client that matches updated text source
        target_client = next((client for client in clients if client["text_source_send_name"] == source_name), None)
        
        source_settings = obs.obs_source_get_settings(source)
        text = obs.obs_data_get_string(source_settings, "text")

        data = json.loads(text)
        address = data.get("address")
        arguments = data.get("arguments")

        if address and arguments is not None:
            send_osc_message(target_client, address, arguments)
        else:
            print("Invalid JSON format: Missing 'address' or 'arguments'")

        obs.obs_data_release(source_settings)
        obs.obs_source_release(source_name)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
    except Exception as e:
        print(f"Error processing OSC send data: {e}")


def send_osc_message(client, address, arguments):
    """Sends an OSC message to the specified address with the given arguments."""
    try:
      client_ip = client.get("client_ip")
      client_port = client.get("client_port")
      osc_client = udp_client.SimpleUDPClient(client_ip, client_port)
      osc_client.send_message(address, arguments)
    
    except Exception as e:
        print(f"Error sending OSC message: {e}")


def start_server_callback(props, property):
    global server_running, server_thread
    if not server_running:
        start_osc_server()
        server_running = True
        print("OSC Server Started via button.")


def stop_server_callback(props, property):
    global server_running, server, server_thread
    if server_running:
        if server:
            server.shutdown()
        if server_thread:
            server_thread.join()
        server_running = False
        print("OSC Server Stopped via button.")


def update_text(address, *args):
    """
    Callback function to update the text source with received OSC in JSON format.
    Iterates through the clients to find the correct receive text source.
    """
    
    data = {"address": address, "arguments": args}
    json_string = json.dumps(data)

    target_source = next((client["text_source_receive_name"] for client in clients if args[0].startswith(client["osc_address"])), "OSC Message")
    
    if target_source:
        try:
            source = obs.obs_get_source_by_name(target_source)
            if source is not None:
                settings = obs.obs_data_create()
                obs.obs_data_set_string(settings, "text", json_string)
                obs.obs_source_update(source, settings)
                obs.obs_data_release(settings)  # Release settings after use
                obs.obs_source_release(source)
            else:
                print(f"Text source '{target_source}' not found!")
        except Exception as e:
            print(f"Error updating OSC message: {e}")

    
def start_osc_server():
    global server, server_thread, server_running
    if not server_running:
        disp = dispatcher.Dispatcher()
        disp.set_default_handler(update_text, True)
        
        server = osc_server.ThreadingOSCUDPServer((server_ip, server_port), disp)
        print(f"Serving on {server.server_address}")
        server_thread = threading.Thread(target=server.serve_forever, daemon=True)
        server_thread.start()
        server_running = True


def write_client_settings_to_text_source(settings):
    """Writes the client settings to the specified text source in JSON format."""
    global text_source_settings_name

    client_data = []

    for i in range(num_clients):
        client_ip = obs.obs_data_get_string(settings, f"client_ip_{i}")
        client_port = obs.obs_data_get_int(settings, f"client_port_{i}")
        text_source_receive_name = obs.obs_data_get_string(settings, f"text_source_receive_{i}")
        text_source_send_name = obs.obs_data_get_string(settings, f"text_source_send_{i}")
        osc_address = obs.obs_data_get_string(settings, f"osc_address_{i}")

        if client_ip:  # Only include client if IP is not blank
            client_info = {
                "client_ip": client_ip,
                "client_port": client_port,
                "text_source_receive_name": text_source_receive_name,
                "text_source_send_name": text_source_send_name,
                "osc_address": osc_address,
            }
            client_data.append(client_info)

    output = json.dumps(client_data, indent=4)  # Convert to JSON with indentation for readability

    text_settings = obs.obs_data_create()
    obs.obs_data_set_string(text_settings, "text", output)

    source = obs.obs_get_source_by_name(text_source_settings_name)
    if source is not None:
        obs.obs_source_update(source, text_settings)
        obs.obs_source_release(source)
    else:
        print(f"Writing text source '{text_source_settings_name}' not found!")

    obs.obs_data_release(text_settings)


def script_load(script_settings):
    global server_ip, server_port, server_thread, client, server_running, clients, text_source_settings_name, settings, num_clients, source_signal_handlers

    settings = script_settings  # Store OBS settings
    server_ip = obs.obs_data_get_string(settings, "server_ip")
    server_port = obs.obs_data_get_int(settings, "server_port")

    num_clients = obs.obs_data_get_int(settings, "number_of_clients")

    text_source_settings_name = obs.obs_data_get_string(settings, "text_source_settings")

    clients = []  # Clear existing clients
    # Initialize OSC clients
    for i in range(num_clients):
        client_ip = obs.obs_data_get_string(settings, f"client_ip_{i}")
        client_port = obs.obs_data_get_int(settings, f"client_port_{i}")
        text_source_receive_name = obs.obs_data_get_string(settings, f"text_source_receive_{i}")
        text_source_send_name = obs.obs_data_get_string(settings, f"text_source_send_{i}")
        osc_address = obs.obs_data_get_string(settings, f"osc_address_{i}")

        if client_ip: #Only create the client data, if there is an IP
            client_data = {
                "client_ip": client_ip,
                "client_port": client_port,
                "text_source_receive_name": text_source_receive_name,
                "text_source_send_name": text_source_send_name,
                "osc_address": osc_address,
            }
            clients.append(client_data)

    # Optionally start OSC server on load
    start_osc_server()
    server_running = True
    print("osc server started on script load")

    write_client_settings_to_text_source(settings)
    rebuild_properties()

    # Attach signal handlers to text sources
    for client in clients:
        source_name = client["text_source_send_name"]
        source = obs.obs_get_source_by_name(source_name)
        if source:
            signal_handler = obs.obs_source_get_signal_handler(source)
            obs.signal_handler_connect(signal_handler,"update", source_signal_callback)
            obs.obs_source_release(source)
        else:
            print(f"Source {source_name} not found for signal handler.")


def script_unload():
    global server, server_thread, clients, settings

    #Remove Signal handlers
    for client in clients:
        source_name = client["text_source_send_name"]
        source = obs.obs_get_source_by_name(source_name)
        if source:
            handler = obs.obs_source_get_signal_handler(source)
            obs.signal_handler_disconnect(handler, "update", source_signal_callback)
            obs.obs_source_release(source)

    if server:
        server.shutdown()
        print("Stopping OSC server...")
    if server_thread:
        server_thread.join()
        print("OSC server stopped.")
    global server_running
    server_running = False
    clients = []
    settings = None


def script_update(settings):
    global server_ip, server_port, server_thread, client, server_running, clients, text_source_settings_name, scene_name, num_clients

    new_server_ip = obs.obs_data_get_string(settings, "server_ip")
    new_server_port = obs.obs_data_get_int(settings, "server_port")

    num_clients = obs.obs_data_get_int(settings, "number_of_clients")
    new_text_source_settings_name = obs.obs_data_get_string(settings, "text_source_settings")

    # Check if Server IP or port changed, restart server if needed
    if new_server_ip != server_ip or new_server_port != server_port:
        print("Server IP or Port changed, restarting server...")
        server_ip = new_server_ip
        server_port = new_server_port
        if server:
            server.shutdown()
        if server_thread:
            server_thread.join()
        if server_running:  # Only restart if it was running
            start_osc_server()

    text_source_settings_name = new_text_source_settings_name

    new_clients = []
    for i in range(num_clients):
        client_ip = obs.obs_data_get_string(settings, f"client_ip_{i}")
        client_port = obs.obs_data_get_int(settings, f"client_port_{i}")
        text_source_receive_name = obs.obs_data_get_string(settings, f"text_source_receive_{i}")
        text_source_send_name = obs.obs_data_get_string(settings, f"text_source_send_{i}")
        osc_address = obs.obs_data_get_string(settings, f"osc_address_{i}")

        if client_ip: #Only create the client data, if there is an IP
            client_data = {
                "client_ip": client_ip,
                "client_port": client_port,
                "text_source_receive_name": text_source_receive_name,
                "text_source_send_name": text_source_send_name,
                "osc_address": osc_address,
            }
            new_clients.append(client_data)

    clients = new_clients  # Replace old clients with updated list

    write_client_settings_to_text_source(settings)
    rebuild_properties()

def rebuild_properties():
    """Rebuilds the script properties."""
    
    props = obs.obs_properties_create()
    obs.obs_properties_add_text(props, "server_ip", "Server IP Address", obs.OBS_TEXT_DEFAULT)
    obs.obs_properties_add_int(props, "server_port", "Server Port", 1, 65535, 1)
    obs.obs_properties_add_text(props, "text_source_settings", "Client Settings Text Source", obs.OBS_TEXT_DEFAULT)
    obs.obs_properties_add_text(props, f"server blank", "-----", obs.OBS_TEXT_DEFAULT)

    for i in range(num_clients):
        obs.obs_properties_add_text(props, f"client_ip_{i}", f"Client {i+1} IP Address", obs.OBS_TEXT_DEFAULT)
        obs.obs_properties_add_int(props, f"client_port_{i}", f"Client {i+1} Port", 1, 65535, 1)
        obs.obs_properties_add_text(props, f"text_source_receive_{i}", f"Client {i+1} Text Source Receive Name", obs.OBS_TEXT_DEFAULT)
        obs.obs_properties_add_text(props, f"text_source_send_{i}", f"Client {i + 1} Text Source Send Name", obs.OBS_TEXT_DEFAULT)
        obs.obs_properties_add_text(props, f"osc_address_{i}", f"Clien {i + 1} OSC Address", obs.OBS_TEXT_DEFAULT)
        obs.obs_properties_add_text(props, f"blank {i}", "-----", obs.OBS_TEXT_DEFAULT)

    obs.obs_properties_add_button(props, "start_server", "Start Server", start_server_callback)  # Add Start button
    obs.obs_properties_add_button(props, "stop_server", "Stop Server", stop_server_callback)  # Add Stop button
    obs.obs_properties_destroy(props)
