import obspython as obs
import asyncio
import threading
from pynput import mouse

class ClickMonitor:
    def __init__(self, source_name):
        self.source_name = source_name
        self.running = True
        self.update_interval = 0.1  # Update interval in seconds
        self.mouse_listener = None
        self.last_text = "" #Prevent spamming the text source

    def on_click(self, x, y, button, pressed):
        if not self.running:
            return False

        if pressed:
            if button == mouse.Button.left:
                asyncio.run(self.update_text_source("MB1"))
            elif button == mouse.Button.right:
                asyncio.run(self.update_text_source("MB2"))
            elif button == mouse.Button.middle:
                asyncio.run(self.update_text_source("MB3"))

    async def update_text_source(self, text):
        if text == self.last_text: #Debounce text changes
            return

        self.last_text = text
        source = obs.obs_get_source_by_name(self.source_name)
        if source is not None:
            settings = obs.obs_data_create()
            obs.obs_data_set_string(settings, "text", text)
            obs.obs_source_update(source, settings)
            obs.obs_data_release(settings)
            obs.obs_source_release(source)


    def start_listener(self):
        with mouse.Listener(on_click=self.on_click) as listener:
            self.mouse_listener = listener
            listener.join()

    def stop_listener(self):
        self.running = False
        if self.mouse_listener:
            self.mouse_listener.stop()


click_monitor = None
listener_thread = None
available_text_sources = []

def script_description():
    return "Monitors mouse clicks (buttons 1 and 2) and sends 'MB1' or 'MB2' to a text source."

def script_properties():
    props = obs.obs_properties_create()
    # Populate the dropdown with available text sources
    available_text_sources.clear()
    sources = obs.obs_enum_sources()
    if sources is not None:
        source_list = []  # Temporarily store sources
        for source in sources:
            source_type = obs.obs_source_get_type(source)
            if source_type == obs.OBS_SOURCE_TYPE_INPUT:
                # Use obs_source_get_id to check for text sources as obs_source_get_input_kind is not available in older versions
                source_id = obs.obs_source_get_id(source)
                if source_id == "text_gdiplus" or source_id == "text_ft2_source":
                    name = obs.obs_source_get_name(source)
                    available_text_sources.append(name)
                source_list.append(source)  # Add source to the temporary list

        # Release sources after using them
        for source in source_list:
            obs.obs_source_release(source)

    p = obs.obs_properties_add_list(props, "source_name", "Text Source", obs.OBS_COMBO_TYPE_EDITABLE, obs.OBS_COMBO_FORMAT_STRING)
    for source_name in available_text_sources:
        obs.obs_property_list_add_string(p, source_name, source_name)

    return props

def script_defaults(settings):
    # Set a default value if there are any text sources available
    if available_text_sources:
         obs.obs_data_set_string(settings, "source_name", available_text_sources[0])
    else:
        obs.obs_data_set_string(settings, "source_name", "MouseHotKey")


def script_load(settings):
    global click_monitor, listener_thread

    source_name = obs.obs_data_get_string(settings, "source_name")
    click_monitor = ClickMonitor(source_name)
    listener_thread = threading.Thread(target=click_monitor.start_listener, daemon=True)
    listener_thread.start()


def script_unload():
    global click_monitor, listener_thread
    if click_monitor:
        click_monitor.stop_listener()
    if listener_thread:
        listener_thread.join()
    click_monitor = None
    listener_thread = None


def script_update(settings):
    global click_monitor, listener_thread
    if click_monitor:
        click_monitor.stop_listener() # Stop the old listener

    source_name = obs.obs_data_get_string(settings, "source_name")
    click_monitor = ClickMonitor(source_name)
    listener_thread = threading.Thread(target=click_monitor.start_listener, daemon=True)
    listener_thread.start()