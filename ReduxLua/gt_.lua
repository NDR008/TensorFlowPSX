--ffi.cdef [[
--void loadSaveStateFromFile(LuaFile*);
--]]

--https://github.com/ocornut/imgui/blob/master/imgui_demo.cpp
--https://github.com/grumpycoders/pcsx-redux/blob/main/src/gui/widgets/memcard_manager.cc#L122-L139
--https://github.com/grumpycoders/pcsx-redux/blob/main/third_party/imgui_lua_bindings/imgui_iterator.inl#L576

hasPal = false
hasUs = false
hasJap = false
forPlay = true

netStatus = false

dumpTrack = false

loadfile("memory.lua")()
loadfile("tcp.lua")()

local function reload()
    PCSX.pauseEmulator()
    loadfile("memory.lua")()
    loadfile("gt.lua")()
    loadfile("tcp.lua")()
end

-- Utilizing the DrawImguiFrame periodic function to draw our UI.
-- We are declaring this function global so the emulator can
-- properly call it periodically.
function DrawImguiFrame()
    --print(PCSX.SIO0.slots[1].pads[1].getButton(PCSX.CONSTS.PAD.BUTTON.CROSS))
    local show = imgui.Begin('GT Hacking', true)
    if not show then imgui.End() return end
    local mem = PCSX.getMemPtr()

    -- All for the PAL SCES-00984 version of the game.
    -- Now calling our helper function for each of our pointer.

    local racing = checkValue(mem, 0x8008df72, 58, "int8_t*") -- check if the time is displayed

    local list = {
        { "Start", "start1.slice" },
        { "Arcade Start", "arc1.slice" },
        { "Arcade HS R33", "arc2.slice" },
        { "Arcade HS R33 mid-lap",   "arc4.slice" },
        { "Arcade HS Corv", "arc3.slice" },
        { "Sim Endurance Race",       "sim4.slice" },
        { "Simulation Home", "sim1.slice" },
        { "SARD Supra HS", "sim2.slice" },
        { "0-400m Test MR2", "sim3.slice" }
    }
    if hasPal then
        imgui.BeginTable("GT", 2, imgui.constant.TableFlags.Resizable)

        imgui.TableSetupColumn("Load")
        imgui.TableSetupColumn("Save")
        imgui.TableHeadersRow();
        for i, f in pairs(list) do
            imgui.TableNextRow()
            local text = f[1]
            local filename = f[2]
            imgui.TableSetColumnIndex(0)
            if (imgui.Button(text)) then
                local file = Support.File.open(filename, "READ")
                PCSX.loadSaveState(file)
                file:close()
            end
            imgui.TableSetColumnIndex(1)
            faketext = "Save/Update##" .. filename
            if (imgui.Button(faketext)) then
                local save = PCSX.createSaveState()
                local file = Support.File.open(filename, "TRUNCATE")
                file:writeMoveSlice(save)
                file:close()
                print(filename, "saved")
            end
        end
        imgui.EndTable()


        if (imgui.Button("Reload")) then
            reload()
        end
        imgui.SameLine(80)
        if (imgui.Button("Save state")) then
            local save = PCSX.createSaveState()
            local file = Support.File.open("savestate.slice", "TRUNCATE")
            file:writeMoveSlice(save)
            file:close()
        end
        imgui.SameLine(160)
        if (imgui.Button("Load state")) then
            local file = Support.File.open("savestate.slice", "READ")
            PCSX.loadSaveState(file)
            file:close()
        end
        if (imgui.Button("Funky HS")) then
            local file = Support.File.open("funky.slice", "READ")
            PCSX.loadSaveState(file)
            file:close()
        end
        imgui.SameLine(240)
        netChanged, netStatus = imgui.Checkbox("TCP", netStatus)
        netStatus = netTCP(netChanged, netStatus)
        
        trackChange, dumpTrack = imgui.Checkbox("dumpTrack", dumpTrack)
        if trackChange then
            if dumpTrack then
                openTrack()
            else
                closeTrack()
            end
        else
            if dumpTrack then
                writeTrack()
            end
        end
        doCheckbox(mem, 0x800b6168, 'HighFrameRate', 0, 1, 'int8_t*')

        if (imgui.CollapsingHeader("Not clear", ImGuiTreeNodeFlags_None)) then
            --imgui.TextUnformatted("START-countdown")
            --imgui.SameLine()
            --imgui.TextUnformatted(readValue(mem, 0x800b6162, "int16_t*"))

            imgui.TextUnformatted("PhysicsTimeStep0")
            imgui.SameLine()
            imgui.TextUnformatted(readValue(mem, 0x800bf364, "int8_t*"))

            imgui.TextUnformatted("PhysicsTimeStep2")
            imgui.SameLine()
            imgui.TextUnformatted(readValue(mem, 0x800bf365, "int8_t*"))

            imgui.TextUnformatted("PhysicsTimeStep1")
            imgui.SameLine()
            imgui.TextUnformatted(readValue(mem, 0x800bf368, "int16_t*"))
            
            
            imgui.TextUnformatted("Clutch")
            imgui.SameLine()
            imgui.TextUnformatted(readValue(mem, 0x800b6d63, "int8_t*"))
            


            doSliderInt(mem, 0x800b6702, 'Wrong Way', 0, 1, 'int8_t*')
            if (imgui.Button("Start Pits")) then
                setValue(mem, 0x800b66d4, 127, 'int16_t*')
            end
            doSliderInt(mem, 0x800b6160, 'Pit Related', 0, 127, 'int8_t*')
            doSliderInt(mem, 0x800b6708, 'Map Y', -3000000, 3000000, 'int32_t*')
            doSliderInt(mem, 0x800b6704, 'Map X', -3000000, 3000000, 'int32_t*')
            doSliderInt(mem, 0x800b670c, 'Map Z', -3000000, 3000000, 'int32_t*')
            doSliderInt(mem, 0x800b6716, 'hmmm', -300000, 300000, 'int16_t*')
            -- doSliderInt(mem, 0x800b672e, 'Map X', -30, 30, 'int16_t*')
            -- doSliderInt(mem, 0x800b6dea, 'FL Y', -30, 30, 'int16_t*')
            -- doSliderInt(mem, 0x800b6e0a, 'FL2 Y', -30, 30, 'int16_t*')
            -- doSliderInt(mem, 0x800b6dfa, 'RL X', -30, 30, 'int16_t*')
            -- doSliderInt(mem, 0x800b6706, 'RR X', -30, 30, 'int16_t*')
            -- doSliderInt(mem, 0x800b34f8, 'Global X?', -30, 30, 'int16_t*')

            doSliderInt(mem, 0x800b6778, 'FL off', 0, 2, 'int8_t*')
            doSliderInt(mem, 0x800b67bc, 'FR off', 0, 2, 'int8_t*')
            
            doSliderInt(mem, 0x800b6800, 'RL off', 0, 2, 'int8_t*')
            doSliderInt(mem, 0x800b6844, 'RR off', 0, 2, 'int8_t*')
            doSliderInt(mem, 0x800b67bd, 'Car in shadow', 0, 2, 'int8_t*')

            doSliderInt(mem, 0x800b67d6, '800b67d6 tyre slip?', 0, 255, 'uint8_t*')
            -- doSliderInt(mem, 0x800b67bc, '800b67bc bounce?', -255, 512, 'int16_t*')
            --doSliderInt(mem, 0x800b34a0, 'raceStart', 0, 1, 'uint8_t*') -- seems to be a couple of 100 ms ahead of time
            doSliderInt(mem, 0x800b6d60, 'raceStart', 0, 1, 'uint8_t*')
            doSliderInt(mem, 0x800b6226, 'raceMode', 0, 30, 'uint16_t*')
            doSliderInt(mem, 0x800cb644, 'raceModeA', 0, 5, 'int8_t*')
            doSliderInt(mem, 0x800cb645, 'raceModeB', 0, 5, 'int8_t*')
            doSliderInt(mem, 0x800cb646, 'raceMode_Index', 0, 20, 'int8_t*')
            doSliderInt(mem, 0x800cb649, 'raceModeC', 0, 6, 'int8_t*')

            doSliderInt(mem, 0x800b619c, 'Displayed Max Laps', 0, 5000, 'int32_t*')
            doSliderInt(mem, 0x800b6356, 'Replay?', 00, 02, 'int16_t*')
            doSliderInt(mem, 0x8009056a, 'DAT_8009056a', -2500, 2500, 'int16_t*')
            doSliderInt(mem, 0x8009056c, 'DAT_8009056c', -2500, 2500, 'int16_t*')
            doSliderInt(mem, 0x80093bc8, 'Total_race1', 0, 500000, 'uint32_t*') -- mirror of 0x800bdb54?
            doSliderInt(mem, 0x800bdb54, 'Total_race2', 0, 500000, 'uint32_t*')
            doSliderInt(mem, 0x800bd9c0, 'First_Lap(set)', 0, 500000, 'uint32_t*')
            doSliderInt(mem, 0x800bd9c4, 'Second_Lap', 0, 500000, 'uint32_t*')

            doSliderInt(mem, 0x800bd994, 'DisplayedBestTotal', 0, 500000, 'uint32_t*')
            doSliderInt(mem, 0x800bd998, 'DisplayedBestLap', 0, 500000, 'uint32_t*')
            doSliderInt(mem, 0x800cac90, 'LoadedBestLap', 0, 500000, 'uint32_t*')
            --doSliderInt(mem, 0x801d393c, 'DAT_801d393c', 0, 5000, 'uint16_t*')
        end
        if (imgui.CollapsingHeader("Racing Parameters", ImGuiTreeNodeFlags_None)) then
            if racing then
                doSliderInt(mem, 0x800b66f0, 'Vector?', -500, 500, 'int16_t*')
                doCheckbox(mem, 0x800b6358, 'HUD', 0, 1, 'int16_t*') -- (PAL SCES-00984)
                doCheckbox(mem, 0x800b615c, 'Not Replay', 0, 1, 'int32_t*') -- (PAL SCES-00984)
                doSliderInt(mem, 0x800b66ec, 'Speed', 0, 5000, 'uint16_t*')
                doSliderInt(mem, 0x800b66ee, 'Engine Speed', 0, 12000, 'uint16_t*')
                doSliderInt(mem, 0x800b66f8, 'Boost', 0, 12000, 'uint16_t*')
                doSliderInt(mem, 0x800bd990, 'Max Seen Speed', 0, 5000, 'uint16_t*')
                doSliderInt(mem, 0x800b66e8, 'Gear', 0, 10, 'uint8_t*')
                doSliderInt(mem, 0x800b66d6, 'Steering', -580, 580, 'int16_t*')
                doSliderInt(mem, 0x800b6d69, 'Car Position', 1, 6, 'int16_t*')
                -- doSliderInt(mem, 0x800b66fa, 'Accel0 (changes with X)', 65525, 0, 'uint16_t*')
                -- doSliderInt(mem, 0x800b66d9, 'Accel1 (equal to button press)', 0, 16, 'uint16_t*')
                -- doSliderInt(mem, 0x800b66db, 'Accel2 (blips on shift)', 0, 16, 'uint16_t*')
                doSliderInt(mem, 0x800b66dd, 'Brake1', 0, 16, 'uint16_t*')
                doSliderInt(mem, 0x800b6268, 'Camera Yawn', -3600, 3600, 'int16_t*')
                doSliderInt(mem, 0x800b626a, 'Camera Pitch', -3600, 3600, 'int16_t*')
                doSliderInt(mem, 0x800b626c, 'Camera Zoom', -3600, 3600, 'int16_t*')
            else
                imgui.TextUnformatted("Will be available during a race")
            end
        end
        if (imgui.CollapsingHeader("Simulation", ImGuiTreeNodeFlags_None)) then
            doSliderInt(mem, 0x8009b874, 'Credit (Simu)', -999999999, 999999999, 'int32_t*')
        end

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

function checkRegion()
    print("GT1 region detection started!")
    -- pprint(PCSX.CONSTS)

    local reader = PCSX.getCurrentIso():createReader()
    local pal = reader:open('SCES_009.84;1')
    local us = reader:open('SCUS_941.94;1')
    local jap = reader:open('SCPS_100.45;1')

    hasPal = not pal:failed() -- this line crashes redux :(
    hasUs = not us:failed()
    hasJap = not jap:failed()
end

if checked then checked:remove() end
checked = PCSX.Events.createEventListener('ExecutionFlow::Run', checkRegion)
PCSX.resumeEmulator()
