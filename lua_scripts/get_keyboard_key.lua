-- This Source Code Form is subject to the terms of the
-- Mozilla Public License, v. 2.0. If a copy of the MPL
-- was not distributed with this file, You can obtain one
-- at https://mozilla.org/MPL/2.0/.
--
-- Modified showhtk.lua by poypoyan. https://github.com/poypoyan/showhtk
-- 
--https://github.com/obsproject/obs-studio/blob/master/libobs/obs-hotkeys.h

obs = obslua
ffi = require("ffi")

-- constants
if ffi.os == "Windows" then
	SUPER_KEY = "Win"
	RETURN_KEY = "Enter"
elseif ffi.os == "OSX" then
	SUPER_KEY = "Cmd"
	RETURN_KEY = "Return"
else
	SUPER_KEY = "Super"
	RETURN_KEY = "Return"
end

KEYBOARD_LAYOUT = { -- ind = true means that the key can be a standalone hotkey
{id = "ESC", jsn = "OBS_KEY_ESCAPE", txt = "Esc", ind = true, type = false},
{id = "F1", jsn = "OBS_KEY_F1", txt = "F1", ind = true, type = false},
{id = "F2", jsn = "OBS_KEY_F2", txt = "F2", ind = true, type = false},
{id = "F3", jsn = "OBS_KEY_F3", txt = "F3", ind = true, type = false},
{id = "F4", jsn = "OBS_KEY_F4", txt = "F4", ind = true, type = false},
{id = "F5", jsn = "OBS_KEY_F5", txt = "F5", ind = true, type = false},
{id = "F6", jsn = "OBS_KEY_F6", txt = "F6", ind = true, type = false},
{id = "F7", jsn = "OBS_KEY_F7", txt = "F7", ind = true, type = false},
{id = "F8", jsn = "OBS_KEY_F8", txt = "F8", ind = true, type = false},
{id = "F9", jsn = "OBS_KEY_F9", txt = "F9", ind = true, type = false},
{id = "F10", jsn = "OBS_KEY_F10", txt = "F10", ind = true, type = false},
{id = "F11", jsn = "OBS_KEY_F11", txt = "F11", ind = true, type = false},
{id = "F12", jsn = "OBS_KEY_F12", txt = "F12", ind = true, type = false},
{id = "F13", jsn = "OBS_KEY_F13", txt = "F13", ind = true, type = false},
{id = "F14", jsn = "OBS_KEY_F14", txt = "F14", ind = true, type = false},
{id = "F15", jsn = "OBS_KEY_F15", txt = "F15", ind = true, type = false},
{id = "F16", jsn = "OBS_KEY_F16", txt = "F16", ind = true, type = false},
{id = "F17", jsn = "OBS_KEY_F17", txt = "F17", ind = true, type = false},
{id = "F18", jsn = "OBS_KEY_F18", txt = "F18", ind = true, type = false},
{id = "F19", jsn = "OBS_KEY_F19", txt = "F19", ind = true, type = false},
{id = "F20", jsn = "OBS_KEY_F20", txt = "F20", ind = true, type = false},
{id = "F21", jsn = "OBS_KEY_F21", txt = "F21", ind = true, type = false},
{id = "F22", jsn = "OBS_KEY_F22", txt = "F22", ind = true, type = false},
{id = "F23", jsn = "OBS_KEY_F23", txt = "F23", ind = true, type = false},
{id = "F24", jsn = "OBS_KEY_F24", txt = "F24", ind = true, type = false},
{id = "DELETE", jsn = "OBS_KEY_DELETE", txt = "Del", ind = true, type = false},
{id = "RETURN", jsn = "OBS_KEY_RETURN", txt = RETURN_KEY, ind = true, type = false},
{id = "TILDE", jsn = "OBS_KEY_ASCIITILDE", txt = "`", shiftTxt = "~", ind = true, type = true},
{id = "TILDE~", jsn = "OBS_KEY_DEAD_GRAVE", txt = "`", shiftTxt = "~", ind = true, type = true},
{id = "MINUS", jsn = "OBS_KEY_MINUS", txt = "-", shiftTxt = "_", ind = true, type = true},
{id = "PLUS", jsn = "OBS_KEY_PLUS", txt = "=", shiftTxt = "+", ind = true, type = true},
{id = "QOUTE", jsn = "OBS_KEY_QUOTE", txt = "\'", shiftTxt = "\"", ind = true, type = true},
{id = "EQUAL", jsn = "OBS_KEY_EQUAL", txt = "=", shiftTxt = "+", ind = true, type = true},
{id = "BSPACE", jsn = "OBS_KEY_BACKSPACE", txt = "BS", ind = true, type = false},
{id = "TAB", jsn = "OBS_KEY_TAB", txt = "Tab", ind = true, type = false},
{id = "CAPSLOCK", jsn = "OBS_KEY_CAPSLOCK", txt = "CAPS", ind = true, type = false},
{id = "BLEFT", jsn = "OBS_KEY_BRACKETLEFT", txt = "[", shiftTxt = "{", ind = true, type = true},
{id = "BRIGHT", jsn = "OBS_KEY_BRACKETRIGHT", txt = "]", shiftTxt = "}", ind = true, type = true},
{id = "BSLASH", jsn = "OBS_KEY_BACKSLASH", txt = "\\", shiftTxt = "|", ind = true, type = true},
{id = "SCOLON", jsn = "OBS_KEY_SEMICOLON", txt = ";", shiftTxt = ":", ind = true, type = true},
{id = "APOS", jsn = "OBS_KEY_APOSTROPHE", txt = "'", shiftTxt = "\"", ind = true, type = true},
{id = "COMMA", jsn = "OBS_KEY_COMMA", txt = ",", shiftTxt = "<", ind = true, type = true},
{id = "PERIOD", jsn = "OBS_KEY_PERIOD", txt = ".", shiftTxt = ">", ind = true, type = true},
{id = "SLASH", jsn = "OBS_KEY_SLASH", txt = "/", shiftTxt = "?", ind = true, type = true},
{id = "SPACE", jsn = "OBS_KEY_SPACE", txt = "Space", shiftTxt = "Space", ind = true, type = true},
{id = "LEFTARROW", jsn = "OBS_KEY_LEFT", txt = "LeftArrow", shiftTxt = "LeftArrow", ind = true, type = true},
{id = "RIGHTARROW", jsn = "OBS_KEY_RIGHT", txt = "RightArrow", shiftTxt = "RightArrow", ind = true, type = true},
{id = "UPARROW", jsn = "OBS_KEY_UP", txt = "UpArrow", shiftTxt = "UpArrow", ind = true, type = true},
{id = "DOWNARROW", jsn = "OBS_KEY_DOWN", txt = "DownArrow", shiftTxt = "DownArrow", ind = true, type = true},
{id = "0", jsn = "OBS_KEY_0", txt = "0", shiftTxt = ")", ind = true, type = false},
{id = "1", jsn = "OBS_KEY_1", txt = "1", shiftTxt = "!", ind = true, type = true},
{id = "2", jsn = "OBS_KEY_2", txt = "2", shiftTxt = "@", ind = true, type = true},
{id = "3", jsn = "OBS_KEY_3", txt = "3", shiftTxt = "#", ind = true, type = true},
{id = "4", jsn = "OBS_KEY_4", txt = "4", shiftTxt = "$", ind = true, type = true},
{id = "5", jsn = "OBS_KEY_5", txt = "5", shiftTxt = "%", ind = true, type = true},
{id = "6", jsn = "OBS_KEY_6", txt = "6", shiftTxt = "^", ind = true, type = true},
{id = "7", jsn = "OBS_KEY_7", txt = "7", shiftTxt = "&", ind = true, type = true},
{id = "8", jsn = "OBS_KEY_8", txt = "8", shiftTxt = "*", ind = true, type = true},
{id = "9", jsn = "OBS_KEY_9", txt = "9", shiftTxt = "(", ind = true, type = true},
{id = "A", jsn = "OBS_KEY_A", txt = "a", shiftTxt = "A", ind = true, type = true},
{id = "B", jsn = "OBS_KEY_B", txt = "b", shiftTxt = "B", ind = true, type = true},
{id = "C", jsn = "OBS_KEY_C", txt = "c", shiftTxt = "C", ind = true, type = true},
{id = "D", jsn = "OBS_KEY_D", txt = "d", shiftTxt = "D", ind = true, type = true},
{id = "E", jsn = "OBS_KEY_E", txt = "e", shiftTxt = "E", ind = true, type = true},
{id = "F", jsn = "OBS_KEY_F", txt = "f", shiftTxt = "F", ind = true, type = true},
{id = "G", jsn = "OBS_KEY_G", txt = "g", shiftTxt = "G", ind = true, type = true},
{id = "H", jsn = "OBS_KEY_H", txt = "h", shiftTxt = "H", ind = true, type = true},
{id = "I", jsn = "OBS_KEY_I", txt = "i", shiftTxt = "I", ind = true, type = true},
{id = "J", jsn = "OBS_KEY_J", txt = "j", shiftTxt = "J", ind = true, type = true},
{id = "K", jsn = "OBS_KEY_K", txt = "k", shiftTxt = "K", ind = true, type = true},
{id = "L", jsn = "OBS_KEY_L", txt = "l", shiftTxt = "L", ind = true, type = true},
{id = "M", jsn = "OBS_KEY_M", txt = "m", shiftTxt = "M", ind = true, type = true},
{id = "N", jsn = "OBS_KEY_N", txt = "n", shiftTxt = "N", ind = true, type = true},
{id = "O", jsn = "OBS_KEY_O", txt = "o", shiftTxt = "O", ind = true, type = true},
{id = "P", jsn = "OBS_KEY_P", txt = "p", shiftTxt = "P", ind = true, type = true},
{id = "Q", jsn = "OBS_KEY_Q", txt = "q", shiftTxt = "Q", ind = true, type = true},
{id = "R", jsn = "OBS_KEY_R", txt = "r", shiftTxt = "R", ind = true, type = true},
{id = "S", jsn = "OBS_KEY_S", txt = "s", shiftTxt = "S", ind = true, type = true},
{id = "T", jsn = "OBS_KEY_T", txt = "t", shiftTxt = "T", ind = true, type = true},
{id = "U", jsn = "OBS_KEY_U", txt = "u", shiftTxt = "U", ind = true, type = true},
{id = "V", jsn = "OBS_KEY_V", txt = "v", shiftTxt = "V", ind = true, type = true},
{id = "W", jsn = "OBS_KEY_W", txt = "w", shiftTxt = "W", ind = true, type = true},
{id = "X", jsn = "OBS_KEY_X", txt = "x", shiftTxt = "X", ind = true, type = true},
{id = "Y", jsn = "OBS_KEY_Y", txt = "y", shiftTxt = "Y", ind = true, type = true},
{id = "Z", jsn = "OBS_KEY_Z", txt = "z", shiftTxt = "Z", ind = true, type = true},
{id = "Num0", jsn = "OBS_KEY_NUM0", txt = "n0", shiftTxt = "Ins", ind = true, type = true},
{id = "Num1", jsn = "OBS_KEY_NUM1", txt = "n1", shiftTxt = "End", ind = true, type = true},
{id = "Num2", jsn = "OBS_KEY_NUM2", txt = "n2", shiftTxt = "ArrowDown", ind = true, type = true},
{id = "Num3", jsn = "OBS_KEY_NUM3", txt = "n3", shiftTxt = "PgDn", ind = true, type = true},
{id = "Num4", jsn = "OBS_KEY_NUM4", txt = "n4", shiftTxt = "ArrowLeft", ind = true, type = true},
{id = "Num5", jsn = "OBS_KEY_NUM5", txt = "n5", shiftTxt = "5", ind = true, type = false},
{id = "Num6", jsn = "OBS_KEY_NUM6", txt = "n6", shiftTxt = "ArrowRight", ind = true, type = true},
{id = "Num7", jsn = "OBS_KEY_NUM7", txt = "n7", shiftTxt = "Home", ind = true, type = true},
{id = "Num8", jsn = "OBS_KEY_NUM8", txt = "n8", shiftTxt = "ArrowUp", ind = true, type = true},
{id = "Num9", jsn = "OBS_KEY_NUM9", txt = "n9", shiftTxt = "PgUp", ind = true, type = true},
{id = "NumAsterisk", jsn = "OBS_KEY_NUMASTERISK", txt = "n*", ind = true, type = true},
{id = "NumMinus", jsn = "OBS_KEY_NUMMINUS", txt = "n-",  ind = true, type = true},
{id = "NumPlus", jsn = "OBS_KEY_NUMPLUS", txt = "n+", ind = true, type = true},
{id = "NumPeriod", jsn = "OBS_KEY_NUMPERIOD", txt = "n.", ind = true, type = true},
{id = "NumLock", jsn = "OBS_KEY_CLEAR", txt = "NumLock", ind = true, type = true},
{id = "NumSlash", jsn = "OBS_KEY_NUMSLASH", txt = "n/", ind = true, type = true},
{id = "NumEnter", jsn = "OBS_KEY_ENTER", txt = "Enter", ind = true, type = true},
}

SHORTCUT_COMBO = {
{id = "_", jsn = ""}, -- for ind = true keys in KEYBOARD_LAYOUT
{id = "_SHIFT_", jsn = ", \"shift\": true", txt = "Shift"}, -- for ind = true keys in KEYBOARD_LAYOUT
{id = "_CTRL_", jsn = ", \"control\": true", txt = "Ctrl"},
{id = "_CTRL_SHIFT_", jsn = ", \"control\": true, \"shift\": true", txt = "Ctrl+Shift"},
{id = "_CTRL_ALT_", jsn = ", \"control\": true, \"alt\": true", txt = "Ctrl+Alt"},
{id = "_CTRL_ALT_SHIFT_", jsn = ", \"control\": true, \"alt\": true, \"shift\": true", txt = "Ctrl+Alt+Shift"},
{id = "_ALT_", jsn = ", \"alt\": true", txt = "Alt"},
{id = "_ALT_SHIFT_", jsn = ", \"alt\": true, \"shift\": true", txt = "Alt+Shift"},
{id = "_CMD_", jsn = ", \"command\": true", txt = SUPER_KEY},
{id = "_CMD_SHIFT_", jsn = ", \"command\": true, \"shift\": true", txt = SUPER_KEY .. "+Shift"},
{id = "_CMD_CTRL_", jsn = ", \"command\": true, \"control\": true", txt = SUPER_KEY .. "+Ctrl"},
{id = "_CMD_ALT_", jsn = ", \"command\": true, \"alt\": true", txt = SUPER_KEY .. "+Alt"},
{id = "_CMD_CTRL_ALT_", jsn = ", \"command\": true, \"alt\": true, \"control\": true", txt = SUPER_KEY .. "+Ctrl+Alt"},
{id = "_CMD_SHIFT_ALT_", jsn = ", \"command\": true, \"alt\": true, \"shift\": true", txt = SUPER_KEY .. "+Shift+Alt"},
{id = "_CMD_CTRL_SHIFT_ALT_", jsn = ", \"command\": true, \"control\": true, \"alt\": true, \"shift\": true", txt = SUPER_KEY .. "+Ctrl+Shift+Alt"},
}

JSON_DATA = "{"
KEY_FORM = "\"SHOWHTK%s%s\": [{\"key\": \"%s\"%s}]%s"
for k1,v1 in pairs(SHORTCUT_COMBO) do
	for k2,v2 in pairs(KEYBOARD_LAYOUT) do
		local htk_text
		--If no modifier Key pressed
		if v1.id == "_" then
			if not v2.ind then goto continue end
			htk_text = v2.txt
		elseif v1.id == "_SHIFT_" then
			if not v2.ind then goto continue end
			if v2.type then htk_text = v2.shiftTxt 
			else htk_text = v1.txt .. "+" .. v2.txt
			end
		else
			htk_text = v1.txt .. "+" .. v2.txt
		end

		-- final absense of comma is apparently important in obs_data_create_from_json
		local comma
		if k1 == table.getn(SHORTCUT_COMBO) and k2 == table.getn(KEYBOARD_LAYOUT) then
			comma = ""
		else
			comma = ","
		end

		JSON_DATA = JSON_DATA .. KEY_FORM:format(v1.id, v2.id, v2.jsn, v1.jsn, comma)
		_G["SHOWHTK" .. v1.id .. v2.id] = function(pressed)
			if pressed then
				update_text("" .. htk_text)
			end
		end
	::continue:: end
end
JSON_DATA = JSON_DATA .. "}"

-- global variables
g_source_name = ""

----------------------------------------------------------

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

----------------------------------------------------------

-- a function named script_load will be called on startup
function script_load(settings)
	local jsn = obs.obs_data_create_from_json(JSON_DATA)

	for _,v1 in pairs(SHORTCUT_COMBO) do
		for _,v2 in pairs(KEYBOARD_LAYOUT) do
			if (v1.id == "_" or v1.id == "_SHIFT_") and not v2.ind then goto continue end
			reg_hotkey(jsn, "SHOWHTK" .. v1.id .. v2.id)
		::continue:: end
	end

	obs.obs_data_release(jsn)
end

-- auxiliary function to script_load to register hotkey
function reg_hotkey(jsn, name_htk)
	local arr = obs.obs_data_get_array(jsn, name_htk)
	local htk = obs.obs_hotkey_register_frontend(script_path() .. name_htk, name_htk, _G[name_htk])
	obs.obs_hotkey_load(htk, arr)
	obs.obs_data_array_release(arr)
end

-- A function named script_description returns the description shown to
-- the user
function script_description()
	return "Show pressed key \nSelect a Text Source to store the key."
end

-- A function named script_properties defines the properties that the user
-- can change for the entire script module itself
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

	return props
end

-- A function named script_update will be called when settings are changed
function script_update(settings)
	g_source_name = obs.obs_data_get_string(settings, "source")
end

-- A function named script_defaults will be called to set the default settings
function script_defaults(settings)
	
end