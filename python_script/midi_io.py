import obspython as obs
import rtmidi
import threading

midi_in = None
midi_out = None
midi_ports = []
selected_midi_port = ""
input_text_source = ""
output_text_source = ""
stop_flag = False
script_settings = None  # Global variable to store script settings


def script_description():
    return "Select a single MIDI device for both input and output, directing MIDI data to and from OBS text sources."


def script_defaults(settings):
    obs.obs_data_set_default_string(settings, "midi_device", "")
    obs.obs_data_set_default_string(settings, "input_text_source", "")
    obs.obs_data_set_default_string(settings, "output_text_source", "")


def script_properties():
    props = obs.obs_properties_create()

    # MIDI Device Selection
    p = obs.obs_properties_add_list(
        props,
        "midi_device",
        "MIDI Device",
        obs.OBS_COMBO_TYPE_LIST,  # Use OBS_COMBO_TYPE_LIST
        obs.OBS_COMBO_FORMAT_STRING,  # Use OBS_COMBO_FORMAT_STRING
    )
    for port_name in midi_ports:
        obs.obs_property_list_add_string(p, port_name, port_name)

    # Input Text Source Selection
    p = obs.obs_properties_add_list(
        props,
        "input_text_source",
        "Input Text Source",
        obs.OBS_COMBO_TYPE_LIST,
        obs.OBS_COMBO_FORMAT_STRING,
    )
    sources = obs.obs_enum_sources()
    if sources is not None:
        for source in sources:
            source_type = obs.obs_source_get_type(source)
            if source_type == obs.OBS_SOURCE_TYPE_INPUT:
                unversioned_id = obs.obs_source_get_unversioned_id(source)
                if unversioned_id == "text_gdiplus" or unversioned_id == "text_ft2_source":
                    name = obs.obs_source_get_name(source)
                    obs.obs_property_list_add_string(p, name, name)
        obs.source_list_release(sources)

    # Output Text Source Selection
    p = obs.obs_properties_add_list(
        props,
        "output_text_source",
        "Output Text Source",
        obs.OBS_COMBO_TYPE_LIST,
        obs.OBS_COMBO_FORMAT_STRING,
    )
    sources = obs.obs_enum_sources()
    if sources is not None:
        for source in sources:
            source_type = obs.obs_source_get_type(source)
            if source_type == obs.OBS_SOURCE_TYPE_INPUT:
                unversioned_id = obs.obs_source_get_unversioned_id(source)
                if unversioned_id == "text_gdiplus" or unversioned_id == "text_ft2_source":
                    name = obs.obs_source_get_name(source)
                    obs.obs_property_list_add_string(p, name, name)
        obs.source_list_release(sources)
    return props


def script_update(settings):
    global input_text_source, output_text_source, selected_midi_port

    selected_midi_port = obs.obs_data_get_string(settings, "midi_device")
    input_text_source = obs.obs_data_get_string(settings, "input_text_source")
    output_text_source = obs.obs_data_get_string(settings, "output_text_source")

    stop_midi()  # Stop MIDI threads if running
    start_midi()  # Restart MIDI threads if a device is selected


def script_load(script_settings):
    global midi_ports

    script_settings = script_settings  # Store OBS settings

    try:
        midi_in = rtmidi.MidiIn()
        midi_out = rtmidi.MidiOut()
        midi_ports = midi_in.get_ports()  # Get available ports
        del midi_in
        del midi_out
        print("Available MIDI ports:", midi_ports)
    except Exception as e:
        print(f"Error initializing MIDI: {e}")


def script_unload():
    stop_midi()


def midi_input_callback(message, time_stamp=None):
    global input_text_source

    midi_data = message[0]
    midi_status = midi_data[0]
    midi_note = midi_data[1]
    midi_velocity = midi_data[2] if len(midi_data) > 2 else 0

    midi_message = f"Status: {midi_status}, Note: {midi_note}, Velocity: {midi_velocity}"

    # Update the OBS text source
    if input_text_source:
        source = obs.obs_get_source_by_name(input_text_source)
        if source:
            settings = obs.obs_data_create()
            obs.obs_data_set_string(settings, "text", midi_message)
            obs.obs_source_update(source, settings)
            obs.obs_data_release(settings)
            obs.obs_source_release(source)


def midi_output_handler():
    global output_text_source, stop_flag, midi_out
    while not stop_flag:
        if output_text_source and midi_out:
            source = obs.obs_get_source_by_name(output_text_source)
            if source:
                # Corrected: Get settings directly from the source
                settings = obs.obs_source_get_settings(source)
                if settings:  # Check if settings were successfully retrieved
                    text = obs.obs_data_get_string(settings, "text")
                    obs.obs_data_release(settings)  # Free the settings
                    obs.obs_source_release(source)
                    # Parse the text for MIDI commands (example: "noteon 60 100")
                    try:
                        parts = text.split()
                        if len(parts) >= 3:
                            command = parts[0].lower()
                            note = int(parts[1])
                            velocity = int(parts[2])

                            if command == "noteon":
                                send_midi_message([0x90, note, velocity])  # 0x90 is Note On status
                            elif command == "noteoff":
                                send_midi_message([0x80, note, velocity])  # 0x80 is Note Off status
                            # Add more commands as needed (control change, etc.)
                    except ValueError:
                        print("Invalid MIDI command format in text source.")
                    except Exception as e:
                        print(f"Midi Output Handler: {e}")
        obs.timer_sleep(100)  # Check every 100 ms


def send_midi_message(message):
    global midi_out
    if midi_out:
        try:
            midi_out.send_message(message)
            print(f"Sent MIDI message: {message}")
        except rtmidi.InvalidPortError as e:
            print(f"Error sending MIDI message: {e}")
        except Exception as e:
            print(f"Unexpected error sending MIDI message: {e}")


def start_midi():
    global midi_in, midi_out, selected_midi_port, midi_thread, stop_flag

    stop_flag = False

    if not selected_midi_port:
        return  # No MIDI device selected

    try:
        port_index = midi_ports.index(selected_midi_port)

        # Start MIDI Input
        midi_in = rtmidi.MidiIn()
        midi_in.open_port(port_index)
        midi_in.set_callback(midi_input_callback)
        midi_in.ignore_types(False, False, False)  # Don't ignore anything
        print(f"Started MIDI input on port: {selected_midi_port}")

        # Start MIDI Output
        midi_out = rtmidi.MidiOut()
        midi_out.open_port(port_index)
        print(f"Started MIDI output on port: {selected_midi_port}")

    except ValueError as e:
        print(f"Error opening MIDI port: {e}")
        return  # Don't start the thread if MIDI ports failed to open
    except Exception as e:
        print(f"Error initializing MIDI: {e}")
        return  # Don't start the thread if MIDI ports failed to open

    # Start the output handling thread only if MIDI output is initialized
    if midi_out and output_text_source:
        midi_thread = threading.Thread(target=midi_output_handler)
        midi_thread.start()


def stop_midi():
    global midi_in, midi_out, midi_thread, stop_flag

    # Stop MIDI Input
    if midi_in:
        try:
            midi_in.close_port()
            del midi_in
            midi_in = None
            print("Stopped MIDI input.")
        except Exception as e:
            print(f"Error stopping MIDI input: {e}")

    # Stop MIDI Output
    if midi_out:
        try:
            midi_out.close_port()
            del midi_out
            midi_out = None
            print("Stopped MIDI output.")
        except Exception as e:
            print(f"Error stopping MIDI output: {e}")

    # Stop the output handling thread
    stop_flag = True
    if midi_thread and midi_thread.is_alive():
        midi_thread.join()