--
-- OBS Mouse Position
-- An OBS lua script to capture the mouse location.
--

local obs = obslua
local ffi = require("ffi")
local VERSION = "0.0.1"

local g_source_name = ""
local g_source_text = ""

local win_point = nil
local x11_display = nil
local x11_root = nil
local x11_mouse = nil
local osx_lib = nil
local osx_nsevent = nil
local osx_mouse_location = nil

local use_auto_follow_mouse = true
local is_following_mouse = false

local is_obs_loaded = false
local version = obs.obs_get_version_string()
local m1, m2 = version:match("(%d+%.%d+)%.(%d+)")
local major = tonumber(m1) or 0
local minor = tonumber(m2) or 0
   
local previous_X = 0    
local previous_Y = 0

-- Define the mouse cursor functions for each platform
if ffi.os == "Windows" then
    ffi.cdef([[
        typedef int BOOL;
        typedef struct{
            long x;
            long y;
        } POINT, *LPPOINT;
        BOOL GetCursorPos(LPPOINT);
    ]])
    win_point = ffi.new("POINT[1]")
elseif ffi.os == "Linux" then
    ffi.cdef([[
        typedef unsigned long XID;
        typedef XID Window;
        typedef void Display;
        Display* XOpenDisplay(char*);
        XID XDefaultRootWindow(Display *display);
        int XQueryPointer(Display*, Window, Window*, Window*, int*, int*, int*, int*, unsigned int*);
        int XCloseDisplay(Display*);
    ]])

    x11_lib = ffi.load("X11.so.6")
    x11_display = x11_lib.XOpenDisplay(nil)
    if x11_display ~= nil then
        x11_root = x11_lib.XDefaultRootWindow(x11_display)
        x11_mouse = {
            root_win = ffi.new("Window[1]"),
            child_win = ffi.new("Window[1]"),
            root_x = ffi.new("int[1]"),
            root_y = ffi.new("int[1]"),
            win_x = ffi.new("int[1]"),
            win_y = ffi.new("int[1]"),
            mask = ffi.new("unsigned int[1]")
        }
    end
elseif ffi.os == "OSX" then
    ffi.cdef([[
        typedef struct {
            double x;
            double y;
        } CGPoint;
        typedef void* SEL;
        typedef void* id;
        typedef void* Method;

        SEL sel_registerName(const char *str);
        id objc_getClass(const char*);
        Method class_getClassMethod(id cls, SEL name);
        void* method_getImplementation(Method);
        int access(const char *path, int amode);
    ]])

    osx_lib = ffi.load("libobjc")
    if osx_lib ~= nil then
        osx_nsevent = {
            class = osx_lib.objc_getClass("NSEvent"),
            sel = osx_lib.sel_registerName("mouseLocation")
        }
        local method = osx_lib.class_getClassMethod(osx_nsevent.class, osx_nsevent.sel)
        if method ~= nil then
            local imp = osx_lib.method_getImplementation(method)
            osx_mouse_location = ffi.cast("CGPoint(*)(void*, void*)", imp)
        end
    end
end

---
-- Get the current mouse position
---@return table Mouse position
function get_mouse_pos()
    local mouse = { x = 0, y = 0 }
    
    if ffi.os == "Windows" then
        if win_point and ffi.C.GetCursorPos(win_point) ~= 0 then
            mouse.x = win_point[0].x
            mouse.y = win_point[0].y
        end
    elseif ffi.os == "Linux" then
        if x11_lib ~= nil and x11_display ~= nil and x11_root ~= nil and x11_mouse ~= nil then
            if x11_lib.XQueryPointer(x11_display, x11_root, x11_mouse.root_win, x11_mouse.child_win, x11_mouse.root_x, x11_mouse.root_y, x11_mouse.win_x, x11_mouse.win_y, x11_mouse.mask) ~= 0 then
                mouse.x = tonumber(x11_mouse.win_x[0])
                mouse.y = tonumber(x11_mouse.win_y[0])
            end
        end
    elseif ffi.os == "OSX" then
        if osx_lib ~= nil and osx_nsevent ~= nil and osx_mouse_location ~= nil then
            local point = osx_mouse_location(osx_nsevent.class, osx_nsevent.sel)
            mouse.x = point.x
            mouse.y = point.y
        end
    end
    
    mouse.x = math.floor(mouse.x + 0.5) -- round to nearest integer
    mouse.y = math.floor(mouse.y + 0.5) -- round to nearest integer
    
    -- if mouse moved update the text source
    if mouse.x ~= previous_X or mouse.y ~= previous_Y then
        previous_X = mouse.x
        previous_Y = mouse.y
        log("Getting mouse position " .. mouse.x .. ", " .. mouse.y)
        log("Mouse position: " .. mouse.x .. ", " .. mouse.y)
        update_text("" .. mouse.x .. " " .. mouse.y)
    end
    --return mouse
end

-- update text source with mouse position

function update_text(text)
	local source = obs.obs_get_source_by_name(g_source_name)
	if source ~= nil then
		local settings = obs.obs_data_create()
		obs.obs_data_set_string(settings, "text", text)
		obs.obs_source_update(source, settings)
		obs.obs_data_release(settings)
		obs.obs_source_release(source)
	end
end

---
-- Logs a message to the OBS script console
---@param msg string The message to log
function log(msg)
    if debug_logs then
        obs.script_log(obs.OBS_LOG_INFO, msg)
    end
end

function on_toggle_follow(pressed)
    if pressed then
        is_following_mouse = not is_following_mouse
        log("Tracking mouse is " .. (is_following_mouse and "on" or "off"))

        if is_following_mouse == true then
            local timer_interval = math.floor(obs.obs_get_frame_interval_ns() / 1000000)
            obs.timer_add(get_mouse_pos, timer_interval)
        else
            obs.timer_remove(get_mouse_pos)
        end
    end
end

function script_description()
    return "Capture the mouse X,Y location"
end

function script_properties()
    local props = obs.obs_properties_create()

    local p = obs.obs_properties_add_list(props, "source", "Text Source", obs.OBS_COMBO_TYPE_EDITABLE, obs.OBS_COMBO_FORMAT_STRING)
	local sources = obs.obs_enum_sources()
	if sources ~= nil then
		for _, source in ipairs(sources) do
			source_id = obs.obs_source_get_unversioned_id(source)
			if source_id == "text_gdiplus" or source_id == "text_ft2_source" then
				local name = obs.obs_source_get_name(source)
				obs.obs_property_list_add_string(p, name, name)
			end
		end
	end
	obs.source_list_release(sources)

    local follow = obs.obs_properties_add_bool(props, "follow", "Start mouse follow with OBS")
    obs.obs_property_set_long_description(follow,
        "When enabled mouse tracking will auto-start without waiting for tracking toggle hotkey")

    local debug = obs.obs_properties_add_bool(props, "debug_logs", "Enable debug logging ")
    obs.obs_property_set_long_description(debug,
        "When enabled the script will output diagnostics messages to the script log (useful for debugging/github issues)")

    return props
end

function script_load(settings)

    -- Workaround for detecting if OBS is already loaded and we were reloaded using "Reload Scripts"
    local current_scene = obs.obs_frontend_get_current_scene()
    is_obs_loaded = current_scene ~= nil -- Current scene is nil on first OBS load
    obs.obs_source_release(current_scene)

    -- Add our hotkey
    hotkey_follow_id = obs.obs_hotkey_register_frontend("toggle_follow_hotkey", "Toggle follow mouse",
        on_toggle_follow)

    -- Attempt to reload existing hotkey bindings if we can find any
    local hotkey_save_array = obs.obs_data_get_array(settings, "obs_zoom_to_mouse.hotkey.follow")
    obs.obs_hotkey_load(hotkey_follow_id, hotkey_save_array)
    obs.obs_data_array_release(hotkey_save_array)

    -- Load any other settings
    use_auto_follow_mouse = obs.obs_data_get_bool(settings, "follow")

    obs.obs_frontend_add_event_callback(on_frontend_event)

    if debug_logs then
        log_current_settings()
    end

    if ffi.os == "Linux" and not x11_display then
        log("ERROR: Could not get X11 Display for Linux\n" ..
            "Mouse position will be incorrect.")
    end

    is_script_loaded = true

    use_auto_follow_mouse = obs.obs_data_get_bool(settings, "follow")
    
    if use_auto_follow_mouse then
        on_toggle_follow(true)
    end
end

function script_unload()
    is_script_loaded = false

    -- Clean up the memory usage
    if major > 29.1 or (major == 29.1 and minor > 2) then -- 29.1.2 and below seems to crash if you do this, so we ignore it as the script is closing anyway
        local transitions = obs.obs_frontend_get_transitions()
        if transitions ~= nil then
            for i, s in pairs(transitions) do
                local handler = obs.obs_source_get_signal_handler(s)
                obs.signal_handler_disconnect(handler, "transition_start", on_transition_start)
            end
            obs.source_list_release(transitions)
        end

        obs.obs_hotkey_unregister(on_toggle_follow)
        obs.obs_frontend_remove_event_callback(on_frontend_event)
        release_sceneitem()
    end

    if x11_lib ~= nil and x11_display ~= nil then
        x11_lib.XCloseDisplay(x11_display)
        x11_display = nil
        x11_lib = nil
    end

end

function script_defaults(settings)
    -- Default values for the script
    obs.obs_data_set_default_bool(settings, "follow", true)
    obs.obs_data_set_default_bool(settings, "debug_logs", false)
end

function script_save(settings)
    -- Save the custom hotkey information
    if hotkey_follow_id ~= nil then
        local hotkey_save_array = obs.obs_hotkey_save(hotkey_follow_id)
        obs.obs_data_set_array(settings, "obs_zoom_to_mouse.hotkey.follow", hotkey_save_array)
        obs.obs_data_array_release(hotkey_save_array)
    end
end

function script_update(settings)
    local old_follow = use_auto_follow_mouse
    -- Update the settings
    g_source_name = obs.obs_data_get_string(settings, "source")
    use_auto_follow_mouse = obs.obs_data_get_bool(settings, "follow")
    debug_logs = obs.obs_data_get_bool(settings, "debug_logs")

    if old_follow ~= use_auto_follow_mouse then
       on_toggle_follow(true)
    end
end
