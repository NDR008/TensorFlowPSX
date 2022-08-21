--https://github.com/ocornut/imgui/blob/master/imgui_demo.cpp
--https://github.com/grumpycoders/pcsx-redux/blob/main/src/gui/widgets/memcard_manager.cc#L122-L139
--https://github.com/grumpycoders/pcsx-redux/blob/main/third_party/imgui_lua_bindings/imgui_iterator.inl#L576

hasPal = false
hasUs = false
hasJap = false

forPlay = true

local function checkValue(mem, address, value, type)
    address = bit.band(address, 0x1fffff)
    local pointer = mem + address
    pointer = ffi.cast(type, pointer)
    local tempvalue = pointer[0]
    local check = false
    if tempvalue == value then
        check = true
    end
    return check
end

local function doCheckbox(mem, address, name, value, original, type)
    address = bit.band(address, 0x1fffff)
    local pointer = mem + address
    pointer = ffi.cast(type, pointer)
    local changed
    local check
    local tempvalue = pointer[0]
    if tempvalue == original then check = false end
    if tempvalue == value then check = true else check = false end
    changed, check = imgui.Checkbox(name, check)
    if changed then
        if check then pointer[0] = value else pointer[0] = original end
    end
end

local function createClient(name)
    changed, check = imgui.Checkbox(name, check)
    if changed then
        if check then
            createClient("activate")
        end
    end
end

local function debug(name)
    changed, check = imgui.Checkbox(name, forPlay)
    if changed then
        forPlay = not forPlay
    end
end

-- Declare a helper function with the following arguments:
--   mem: the ffi object representing the base pointer into the main RAM
--   address: the address of the uint32_t to monitor and mutate
--   name: the label to display in the UI
--   min, max: the minimum and maximum values of the slider
local function doSliderInt(mem, address, name, min, max, type)
    address = bit.band(address, 0x1fffff)
    local pointer = mem + address
    pointer = ffi.cast(type, pointer)
    local value = pointer[0]
    local changed
    changed, value = imgui.SliderInt(name, value, min, max, '%d')
    if changed then pointer[0] = value end
end

local function reload()
    PCSX.pauseEmulator()
    loadfile("gt.lua")()
end

-- Utilizing the DrawImguiFrame periodic function to draw our UI.
-- We are declaring this function global so the emulator can
-- properly call it periodically.
function DrawImguiFrame()
    local show = imgui.Begin('GT Hacking', true)
    if not show then imgui.End() return end
    local mem = PCSX.getMemPtr()

    -- All for the PAL SCES-00984 version of the game.
    -- Now calling our helper function for each of our pointer.

    local racing = checkValue(mem, 0x8008df72, 58, "int8_t*") -- check if the time is displayed

    if hasPal then
        imgui.BeginTable("GT", 2, ImGuiTableFlags_Resizable)

        imgui.TableSetupColumn("test1")
        imgui.TableSetupColumn("test2")
        imgui.TableHeadersRow();
        imgui.TableNextRow()
        imgui.TableSetColumnIndex(0)
        if (imgui.Button("Reload")) then
            reload()
        end
        imgui.SameLine(80)
        if (imgui.Button("Save state")) then
            local save = PCSX.createSaveState()
            local file = Support.File.open("savestate.slice", "TRUNCATE")
            file:write(save)
            file:close()
        end
        imgui.SameLine(160)
        if (imgui.Button("Load state")) then
            local file = Support.File.open("savestate.slice", "READ")
            PCSX.loadSaveState(file)
            file:close()
        end
        if racing then
            imgui.TableNextRow()
            imgui.TableSetColumnIndex(0)

            --if forPlay then
            --createClient('Texture Swap')
            --debug('Turn on Debug')
            if (imgui.CollapsingHeader("Header", ImGuiTreeNodeFlags_None)) then

                doSliderInt(mem, 0x800b66ec, 'Speed1', 0, 5000, 'uint16_t*')
                doSliderInt(mem, 0x800b66ee, 'Engine Speed', 0, 12000, 'uint16_t*')
                doSliderInt(mem, 0x800bd990, 'Max Seen Speed', 0, 5000, 'uint16_t*')
                doSliderInt(mem, 0x800b66e8, 'Gear', 0, 10, 'uint8_t*')
                doSliderInt(mem, 0x800b66d6, 'Steering', -580, 580, 'int16_t*')
                doSliderInt(mem, 0x800b6d69, 'Car Position', 1, 6, 'int16_t*')
            end

            imgui.TableSetColumnIndex(1)

            doSliderInt(mem, 0x800b66fa, 'Accel0 (changes with X)', 65525, 0, 'uint16_t*')
            doSliderInt(mem, 0x800b66d9, 'Accel1 (equal to button press)', 0, 16, 'uint16_t*')
            doSliderInt(mem, 0x800b66db, 'Accel2 (blips on shift)', 0, 16, 'uint16_t*')
            doSliderInt(mem, 0x800b66dd, 'Brake1', 0, 16, 'uint16_t*')
            doSliderInt(mem, 0x8009b874, 'Credit (Simu)', -999999999, 999999999, 'int32_t*')
            doSliderInt(mem, 0x800b626a, 'Camera Pitch', 104, 256, 'int16_t*')

            imgui.TableNextRow()
            imgui.TableSetColumnIndex(0)
            --else
            -- hunting model-view-controller
            doSliderInt(mem, 0x800b6700, 'Hidden Current Lap', 0, 5000, 'int32_t*')
            doSliderInt(mem, 0x800b619c, 'Displayed Max Laps', 0, 5000, 'int32_t*')
            doSliderInt(mem, 0x800b6356, 'Replay?', 00, 02, 'int16_t*')
            doSliderInt(mem, 0x800b6226, 'DAT_800b6226', 0, 30, 'uint16_t*')
            doSliderInt(mem, 0x8009056a, 'DAT_8009056a', -2500, 2500, 'int16_t*')
            doSliderInt(mem, 0x8009056c, 'DAT_8009056c', -2500, 2500, 'int16_t*')
            doSliderInt(mem, 0x80093bc8, 'DAT_80093bc8', 0, 5000, 'uint16_t*')
            doSliderInt(mem, 0x800b66f4, 'DAT_800b66f4', 0, 5000, 'uint16_t*')
            doSliderInt(mem, 0x800bdb54, 'DAT_800bdb54', 0, 5000, 'uint16_t*')
            doSliderInt(mem, 0x800bd998, 'hiddenInRaceBestLap?', 0, 5000, 'uint16_t*')
            doSliderInt(mem, 0x800cac90, 'hiddenInGameBestLap?', 0, 5000, 'uint16_t*')
            doSliderInt(mem, 0x801d393c, 'DAT_801d393c', 0, 5000, 'uint16_t*')
            --debug("Turn off Debug")
            imgui.TableSetColumnIndex(1)
            doCheckbox(mem, 0x800b6358, 'HUD', 0, 1, 'int16_t*') -- (PAL SCES-00984)
        end
        imgui.EndTable()
    elseif hasUs then
        doCheckbox(mem, 0x800b6508, '(NTSC-U SCUS-94194) HUD', 0, 1, 'int16_t*')

    elseif hasJap then
        -- 8B20 lower than pal
        doSliderInt(mem, 0x800adbcc, 'Speed1', 0, 5000, 'uint16_t*')
        doSliderInt(mem, 0x800adbce, 'Engine Speed', 0, 12000, 'uint16_t*')
        doSliderInt(mem, 0x800adbc8, 'Gear', 0, 10, 'uint8_t*')
        doSliderInt(mem, 0x800adbda, 'Accel0 (changes with X)', 65525, 0, 'uint16_t*')
        doSliderInt(mem, 0x800adbb9, 'Accel1 (equal to button press)', 0, 16, 'uint16_t*')
        doSliderInt(mem, 0x800adbbb, 'Accel2 (blips on shift)', 0, 16, 'uint16_t*')
        doSliderInt(mem, 0x800adbbd, 'Brake1', 0, 16, 'uint16_t*')
        doSliderInt(mem, 0x800adbbf, 'Brake2', 0, 16, 'uint16_t*')
        doSliderInt(mem, 0x800adbc1, 'Brake3', 0, 16, 'uint16_t*')
        doSliderInt(mem, 0x800adbb6, 'Steering', -580, 580, 'int16_t*')
        doSliderInt(mem, 0x800ae249, 'Car Position', 1, 6, 'int16_t*')
        doCheckbox(mem, 0x800ad838, '(NTSC-J SCPS-10045) HUD', 0, 1, 'int16_t*')
    end

    -- Don't forget to close the ImGui window.
    imgui.End()

end

function myFunc()
    print("GT1 region detection started!")
    local reader = PCSX.getCurrentIso():createReader()
    local pal = reader:open('SCES_009.84;1')
    local us = reader:open('SCUS_941.94;1')
    local jap = reader:open('SCPS_100.45;1')

    hasPal = not pal:failed() -- this line crashes redux :(
    hasUs = not us:failed()
    hasJap = not jap:failed()
end

-- if bob then
--     bob:remove()
-- end
if bob then bob:remove() end
bob = PCSX.Events.createEventListener('ExecutionFlow::Run', myFunc)
PCSX.resumeEmulator()

-- function createClient(check)
--   client = luv.new_tcp()

--   luv.tcp_connect(client, "127.0.0.1", 9999, function (err)
--     luv.read_start(client, function(err, chunk)
--         assert(not err, err)
--         if chunk then
--             print(chunk)
--         end
--     end)
--     luv.write(client, check)
--   luv.close(client)
--   end)
-- end


function createClient(check)
    client = Support.File.uvFifo("127.0.0.1", 9999)
    client:write('bob')
    client:close()
end
