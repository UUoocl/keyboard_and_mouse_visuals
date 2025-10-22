import obspython as obs
import threading  # Required by advss helpers


from pythonosc.dispatcher import Dispatcher
from pythonosc import osc_server

condition_name = "Open Sound Control"
server = None
ip = None
port = None
received_messages = []


def append_message(addr, message, volume):
    global received_messages
    print(f"received message! {message}")
    received_messages.append(message)


def start_server():
    global server, ip, port
    if ip is None or port is None:
        return
    dispatcher = Dispatcher()
    dispatcher.map("/testing", append_message)

    server = osc_server.ThreadingOSCUDPServer((ip, port), dispatcher)
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.start()


def stop_server():
    global received_messages
    if server is not None:
        server.shutdown()
    received_messages.clear()


def restart_server():
    stop_server()
    start_server()


# ------------------------------------------------------------


def check_condition(data):
    global received_messages
    expected_message = obs.obs_data_get_string(data, "value")
    return_value = False
    print(received_messages)
    for message in received_messages:
        if message == expected_message:
            return_value = True
    received_messages.clear()
    return return_value 


def get_condition_properties():
    props = obs.obs_properties_create()
    obs.obs_properties_add_text(props, "value", "Expected Value:", obs.OBS_TEXT_DEFAULT)
    return props


def get_condition_defaults():
    default_settings = obs.obs_data_create()
    obs.obs_data_set_default_string(
        default_settings, "value", "Your expected value here!"
    )
    return default_settings


# ------------------------------------------------------------


def script_description():
    return (
        f'Adds the macro condition "{condition_name}" for the advanced scene switcher'
    )


def script_update(settings):
    global ip, port
    ip = obs.obs_data_get_string(settings, "ip")
    port = obs.obs_data_get_int(settings, "port")


def script_defaults(settings):
    obs.obs_data_set_default_string(settings, "ip", "127.0.0.1")
    obs.obs_data_set_default_int(settings, "port", 5005)


def restart_pressed(props, prop):
    restart_server()


def script_properties():
    props = obs.obs_properties_create()
    obs.obs_properties_add_text(props, "ip", "IP Address", obs.OBS_TEXT_DEFAULT)
    obs.obs_properties_add_int(props, "port", "Port", 0, 65535, 1)
    obs.obs_properties_add_button(props, "button", "Restart OSC server", restart_pressed)
    return props


# ------------------------------------------------------------


def script_load(settings):
    global condition_name
    advss_register_condition(
        condition_name,
        check_condition,
        get_condition_properties,
        get_condition_defaults(),
    )
    start_server()

def script_unload():
    global condition_name
    advss_deregister_condition(condition_name)


###############################################################################

# Advanced Scene Switcher helper functions below:
# Usually you should not have to modify this code.
# Simply copy paste it into your scripts.

###############################################################################
# Actions
###############################################################################


# The advss_register_action() function is used to register custom actions
# It takes the following arguments:
# 1. The name of the new action type.
# 2. The function callback which should run when the action is executed.
# 3. The optional function callback which return the properties to display the
#    settings of this action type.
# 4. The optional default_settings pointer used to set the default settings of
#    newly created actions.
#    The pointer must not be freed within this script.
def advss_register_action(name, callback, get_properties=None, default_settings=None):
    advss_register_segment_type(True, name, callback, get_properties, default_settings)


def advss_deregister_action(name):
    advss_deregister_segment(True, name)


###############################################################################
# Conditions
###############################################################################


# The advss_register_condition() function is used to register custom conditions
# It takes the following arguments:
# 1. The name of the new condition type.
# 2. The function callback which should run when the condition is executed.
# 3. The optional function callback which return the properties to display the
#    settings of this condition type.
# 4. The optional default_settings pointer used to set the default settings of
#    newly created condition.
#    The pointer must not be freed within this script.
def advss_register_condition(
    name, callback, get_properties=None, default_settings=None
):
    advss_register_segment_type(False, name, callback, get_properties, default_settings)


def advss_deregister_condition(name):
    advss_deregister_segment(False, name)


###############################################################################
# (De)register helpers
###############################################################################


def advss_register_segment_type(
    is_action, name, callback, get_properties, default_settings
):
    proc_handler = obs.obs_get_proc_handler()
    data = obs.calldata_create()

    obs.calldata_set_string(data, "name", name)
    obs.calldata_set_ptr(data, "default_settings", default_settings)

    register_proc = (
        "advss_register_script_action"
        if is_action
        else "advss_register_script_condition"
    )
    obs.proc_handler_call(proc_handler, register_proc, data)

    success = obs.calldata_bool(data, "success")
    if success == False:
        segment_type = "action" if is_action else "condition"
        log_msg = f'failed to register custom {segment_type} "{name}"'
        obs.script_log(obs.LOG_WARNING, log_msg)
        obs.calldata_destroy(data)
        return

    # Run in separate thread to avoid blocking main OBS signal handler.
    # Operation completion will be indicated via signal completion_signal_name.
    def run_helper(data):
        completion_signal_name = obs.calldata_string(data, "completion_signal_name")
        id = obs.calldata_int(data, "completion_id")

        def thread_func(settings):
            settings = obs.obs_data_create_from_json(
                obs.calldata_string(data, "settings")
            )
            callback_result = callback(settings)
            if is_action:
                callback_result = True

            reply_data = obs.calldata_create()
            obs.calldata_set_int(reply_data, "completion_id", id)
            obs.calldata_set_bool(reply_data, "result", callback_result)
            signal_handler = obs.obs_get_signal_handler()
            obs.signal_handler_signal(
                signal_handler, completion_signal_name, reply_data
            )
            obs.obs_data_release(settings)
            obs.calldata_destroy(reply_data)

        threading.Thread(target=thread_func, args={data}).start()

    def properties_helper(data):
        if get_properties is not None:
            properties = get_properties()
        else:
            properties = None
        obs.calldata_set_ptr(data, "properties", properties)

    trigger_signal_name = obs.calldata_string(data, "trigger_signal_name")
    property_signal_name = obs.calldata_string(data, "properties_signal_name")

    signal_handler = obs.obs_get_signal_handler()
    obs.signal_handler_connect(signal_handler, trigger_signal_name, run_helper)
    obs.signal_handler_connect(signal_handler, property_signal_name, properties_helper)

    obs.calldata_destroy(data)


def advss_deregister_segment(is_action, name):
    proc_handler = obs.obs_get_proc_handler()
    data = obs.calldata_create()

    obs.calldata_set_string(data, "name", name)

    deregister_proc = (
        "advss_deregister_script_action"
        if is_action
        else "advss_deregister_script_condition"
    )

    obs.proc_handler_call(proc_handler, deregister_proc, data)

    success = obs.calldata_bool(data, "success")
    if success == False:
        segment_type = "action" if is_action else "condition"
        log_msg = f'failed to deregister custom {segment_type} "{name}"'
        obs.script_log(obs.LOG_WARNING, log_msg)

    obs.calldata_destroy(data)


###############################################################################
# Variables
###############################################################################


# The advss_get_variable_value() function can be used to query the value of a
# variable with a given name.
# None is returned in case the variable does not exist.
def advss_get_variable_value(name):
    proc_handler = obs.obs_get_proc_handler()
    data = obs.calldata_create()

    obs.calldata_set_string(data, "name", name)
    obs.proc_handler_call(proc_handler, "advss_get_variable_value", data)

    success = obs.calldata_bool(data, "success")
    if success == False:
        obs.script_log(obs.LOG_WARNING, f'failed to get value for variable "{name}"')
        obs.calldata_destroy(data)
        return None

    value = obs.calldata_string(data, "value")

    obs.calldata_destroy(data)
    return value


# The advss_set_variable_value() function can be used to set the value of a
# variable with a given name.
# True is returned if the operation was successful.
def advss_set_variable_value(name, value):
    proc_handler = obs.obs_get_proc_handler()
    data = obs.calldata_create()

    obs.calldata_set_string(data, "name", name)
    obs.calldata_set_string(data, "value", value)
    obs.proc_handler_call(proc_handler, "advss_set_variable_value", data)

    success = obs.calldata_bool(data, "success")
    if success == False:
        obs.script_log(obs.LOG_WARNING, f'failed to set value for variable "{name}"')

    obs.calldata_destroy(data)
    return success
