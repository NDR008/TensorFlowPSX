hasPal = false
hasUs = false
hasJap = false
forPlay = true
setTCP = false
dumpTrack = false
hi_res = false
smoke = false
HeldCollState = 0

loadfile("memory.lua")()
loadfile("tcp.lua")()
loadfile("track.lua")()
loadfile("track_prog.lua")()

local function reload()
    PCSX.pauseEmulator()
    loadfile("memory.lua")()
    loadfile("gt.lua")()
    loadfile("tcp.lua")()
    loadfile("track.lua")()
    loadfile("track_prog.lua")()
end

saveList = {
    { "Start",                 "start1.slice" },
    { "Arcade Start",          "arc1.slice" },
    { "Arcade HS R33",         "arc2.slice" },
    { "Arcade HS R33 mid-lap", "arc4.slice" },
    { "Arcade HS Corv",        "arc3.slice" },
    { "Arcade MR2 TT HS",      "arc5.slice" },
    { "Hi-Def",                "arc6.slice" },
    { "Sim Endurance Race",    "sim4.slice" },
    { "Simulation Home",       "sim1.slice" },
    { "SARD Supra HS",         "sim2.slice" },
    { "0-400m Test MR2",       "sim3.slice" }

}


mem = PCSX.getMemPtr()

function carInfo()
    if (imgui.CollapsingHeader("Car", ImGuiTreeNodeFlags_None)) then
        doSliderInt(mem, 0x800b66ec, 'Speed', 0, 5000, 'uint16_t*')
        doSliderInt(mem, 0x800b66ee, 'Engine Speed', 0, 9000, 'uint16_t*')
        doSliderInt(mem, 0x800b66f8, 'Boost', 0, 12000, 'uint16_t*')
        doSliderInt(mem, 0x800bd990, 'Max Speed', 0, 5000, 'uint16_t*')
        doSliderInt(mem, 0x800b66e8, 'Gear', 0, 10, 'uint8_t*')
        doSliderInt(mem, 0x800b66d6, 'Steering', -580, 580, 'int16_t*')
        doSliderInt(mem, 0x800b6d63, 'Clutch', 0, 3, 'uint16_t*')
        doSliderInt(mem, 0x800b66d8, 'Accel (input)', 0, 4096, 'int16_t*')
        doSliderInt(mem, 0x800b66da, 'Accel (Transfer)', 0, 4096, 'int16_t*')
        doSliderInt(mem, 0x800b66dc, 'Brake (input)', 0, 4096, 'int16_t*')
        doSliderInt(mem, 0x800b66de, 'Brake (Front? ABS1)', 0, 4096, 'int16_t*')
        doSliderInt(mem, 0x800b66e0, 'Brake (Rear?  ABS2)', 0, 4096, 'int16_t*')
        doSliderInt(mem, 0x800b6d64, 'P-Brake', 0, 16, 'int16_t*')
        doCheckbox(mem, 0x800b67bd, 'Car in sun', 0, 2, 'int16_t*')
    end
end

function tyres()
    if (imgui.CollapsingHeader("Tyres", ImGuiTreeNodeFlags_None)) then
        imgui.BeginTable("Tyre", 2, imgui.constant.TableFlags.Resizable)
        imgui.TableNextRow()
        imgui.TableSetColumnIndex(0)
        imgui.TextUnformatted("Road / Kerb / Grass / Dirt")
        doSliderInt(mem, 0x800b6778, 'Fr Left off', 0, 5, 'int8_t*')
        doSliderInt(mem, 0x800b67bc, 'Fr Right off', 0, 5, 'int8_t*')
        doSliderInt(mem, 0x800b6800, 'Re Left off', 0, 5, 'int8_t*')
        doSliderInt(mem, 0x800b6844, 'Re Right off', 0, 5, 'int8_t*')
        imgui.TableSetColumnIndex(1)
        imgui.TextUnformatted("0 = no slip")
        doSliderInt(mem, 0x800b674e, 'Fr Left slip', 0, 255, 'uint8_t*')
        doSliderInt(mem, 0x800b6792, 'Fr Right slip', 0, 255, 'uint8_t*')
        doSliderInt(mem, 0x800b67d6, 'Re Left slip', 0, 255, 'uint8_t*')
        doSliderInt(mem, 0x800b681a, 'Re Right slip', 0, 255, 'uint8_t*')
        doCheckbox(mem, 0x800b6d62, 'Tyres on Ground', 0, 1, 'uint8_t*')
        --imgui.TableNextRow()
        --imgui.TableSetColumnIndex(0)
        imgui.EndTable()
    end
end

function raceCondition()
    if (imgui.CollapsingHeader("Race Condition", ImGuiTreeNodeFlags_None)) then
        imgui.BeginTable("Tyre", 2, imgui.constant.TableFlags.Resizable)
        imgui.TableNextRow()
        imgui.TableSetColumnIndex(0)

        doSliderInt(mem, 0x800b6d69, 'Car Position', 1, 6, 'uint8_t*')

        doSliderInt(mem, 0x800b6700, 'Lap', -5, 100, 'int8_t*')
        doSliderInt(mem, 0x800b619c, 'Max Laps', 0, 100, 'int32_t*')

        if (imgui.Button("Start Pits")) then
            setValue(mem, 0x800b66d4, 127, 'int16_t*')
        end
        local pitTime = readValue(mem, 0x800b66d4, 'int16_t*')
        imgui.SameLine()
        imgui.TextUnformatted(pitTime)

        imgui.TableSetColumnIndex(1)
        doSliderInt(mem, 0x800b6d60, 'raceStart', 0, 1, 'uint8_t*')
        local way = readValue(mem, 0x800b6702, 'int16_t*')
        local str = '? ['
        if way == 0 then
            str = 'Direction: Right ['
        elseif way == 1 then
            str = 'Direction: Wrong ['
        elseif way == 2 then
            str = 'Direction: Wrong -ve laps ['
        elseif way == 3 then
            str = 'Direction: Right -ve laps ['
        end
        str = str .. tostring(way) .. ']'

        local collisionState = readValue(mem, 0x800b66e9, 'int8_t*')
        local collisionValue = readValue(mem, 0x800b66ea, 'int8_t*')
        
        print("pre", HeldCollState, collisionState, collisionValue)
        if collisionValue > 0 and collisionState > 0 then
            HeldCollState = collisionState
        elseif collisionValue == 0 then
            HeldCollState = 0
        end
        print("pos", HeldCollState, collisionState, collisionValue)
        local collisionText = getCollision(HeldCollState)

        imgui.TextUnformatted(collisionText)
        doCheckbox(mem, 0x800b6358, 'HUD On', 0, 1, 'int16_t*')     -- (PAL SCES-00984)
        doCheckbox(mem, 0x800b615c, 'Not Replay', 0, 1, 'int32_t*') -- (PAL SCES-00984)
        doCheckbox(mem, 0x800b6d61, 'AI mode', 2, 0, 'int16_t*')
        imgui.TextUnformatted(str)
        --doCheckbox(mem, 0x800b6702, str, 0, 1, 'int16_t*')
        imgui.EndTable()
    end
end

function lapTimes()
    if (imgui.CollapsingHeader("Lap Times", ImGuiTreeNodeFlags_None)) then
        doSliderInt(mem, 0x80093bc8, 'Total_race1', 0, 500000, 'uint32_t*') -- mirror of 0x800bdb54?
        doSliderInt(mem, 0x800bdb54, 'Total_race2', 0, 500000, 'uint32_t*')
        doSliderInt(mem, 0x800bd9c0, 'First_Lap(set)', 0, 500000, 'uint32_t*')
        doSliderInt(mem, 0x800bd9c4, 'Second_Lap', 0, 500000, 'uint32_t*')

        doSliderInt(mem, 0x800bd994, 'DisplayedBestTotal', 0, 500000, 'uint32_t*')
        doSliderInt(mem, 0x800bd998, 'DisplayedBestLap', 0, 500000, 'uint32_t*')
        doSliderInt(mem, 0x800cac90, 'LoadedBestLap', 0, 500000, 'uint32_t*')
    end
end

function simulation()
    if (imgui.CollapsingHeader("Simulation", ImGuiTreeNodeFlags_None)) then
        doSliderInt(mem, 0x8009b874, 'Credit (Simu)', -999999999, 999999999, 'int32_t*')
        if (imgui.Button("All Gold licence")) then
            setValue(mem, 0x8009e3c4, 50529027, 'int32_t*')
            setValue(mem, 0x8009e3c8, 50529027, 'int32_t*')
            setValue(mem, 0x8009e3cc, 50529027, 'int32_t*')
            setValue(mem, 0x8009e3d0, 50529027, 'int32_t*')
            setValue(mem, 0x8009e3d4, 50529027, 'int32_t*')
            setValue(mem, 0x8009e3d8, 50529027, 'int32_t*')
        end
        imgui.SameLine()
        if (imgui.Button("No licence")) then
            setValue(mem, 0x8009e3c4, 0, 'int32_t*')
            setValue(mem, 0x8009e3c8, 0, 'int32_t*')
            setValue(mem, 0x8009e3cc, 0, 'int32_t*')
            setValue(mem, 0x8009e3d0, 0, 'int32_t*')
            setValue(mem, 0x8009e3d4, 0, 'int32_t*')
            setValue(mem, 0x8009e3d8, 0, 'int32_t*')
        end
    end
end

function funkyStuff()
    if (imgui.CollapsingHeader("Misc", ImGuiTreeNodeFlags_None)) then
        imgui.BeginTable("Tyre", 3, imgui.constant.TableFlags.Resizable)
        imgui.TableNextRow()
        imgui.TableSetColumnIndex(0)
        --imgui.TextUnformatted(readValue(mem, 0x800b6162, "int16_t*"))
        a, hi_res = imgui.Checkbox("Hi Res", hi_res)
        if hi_res then
            if readValue(mem, 0x800B6168, 'int16_t*') == 2 then
                setValue(mem, 0x800B6168, 1, 'int16_t*')
            end
            b, smoke = imgui.Checkbox("Tyre smoke", smoke)
            if smoke then
                if readValue(mem, 0x8002E560, 'int16_t*') == 2 then
                    setValue(mem, 0x8002E560, 1, 'int16_t*')
                end
            else
                if readValue(mem, 0x8002E560, 'int16_t*') == 1 then
                    setValue(mem, 0x8002E560, 2, 'int16_t*')
                end
            end
            c, mirror = imgui.Checkbox("Mirror", mirror)
            if mirror then
                if readValue(mem, 0x8002AA7C, 'int16_t*') == 2 then
                    setValue(mem, 0x8002AA7C, 1, 'int16_t*')
                end
            else
                if readValue(mem, 0x8002AA7C, 'int16_t*') == 1 then
                    setValue(mem, 0x8002AA7C, 2, 'int16_t*')
                end
            end
        end


        imgui.TextUnformatted("PhysicsTimeStep0")
        imgui.SameLine()
        imgui.TextUnformatted(readValue(mem, 0x800bf364, "int8_t*"))

        imgui.TextUnformatted("PhysicsTimeStep2")
        imgui.SameLine()
        imgui.TextUnformatted(readValue(mem, 0x800bf365, "int8_t*"))

        imgui.TextUnformatted("PhysicsTimeStep1")
        imgui.SameLine()
        imgui.TextUnformatted(readValue(mem, 0x800bf368, "int16_t*"))

        doSliderInt(mem, 0x8009056a, 'DAT_8009056a', -2500, 2500, 'int16_t*')
        doSliderInt(mem, 0x8009056c, 'DAT_8009056c', -2500, 2500, 'int16_t*')

        imgui.TableSetColumnIndex(1)
        doSliderInt(mem, 0x800cb646, 'raceModeIndex', 0, 20, 'int8_t*')
        doSliderInt(mem, 0x800b6226, 'raceMode', 0, 30, 'uint16_t*')
        doSliderInt(mem, 0x800cb644, 'raceModeA', 0, 5, 'int8_t*')
        doSliderInt(mem, 0x800cb645, 'raceModeB', 0, 5, 'int8_t*')
        doSliderInt(mem, 0x800cb649, 'raceModeC', 0, 6, 'int8_t*')
        doSliderInt(mem, 0x800b6210, 'postRace', 0, 6, 'int8_t*')
        imgui.TableSetColumnIndex(2)

        doSliderInt(mem, 0x800b6356, 'Camera Mode1', 00, 02, 'uint16_t*')
        doSliderInt(mem, 0x800b6268, 'Camera Yawn', -3600, 3600, 'int16_t*')
        doSliderInt(mem, 0x800b626a, 'Camera Pitch', -3600, 3600, 'int16_t*')
        doSliderInt(mem, 0x800b6362, 'Camera Position', 0, 9, 'int8_t*')
        doSliderInt(mem, 0x800b6363, 'Camera Related', 0, 512, 'int8_t*')
        -- rearViewMirror = forceCheckbox(mem, 0x800b635e, 'Rear View Mirror', 0, 1, rearViewMirror , 'int8_t*')
        doSliderInt(mem, 0x800b635e, 'Rear', 0, 1, 'int8_t*')

        -- doSliderInt(mem, 0x800b626c, 'Camera Zoom', -3600, 3600, 'int16_t*')

        imgui.EndTable()
        if (imgui.Button("All Unlocked")) then
            setValue(mem, 0x80081b48, 67372036, 'int32_t*')
            setValue(mem, 0x80081b4c, 67372036, 'int32_t*')
            setValue(mem, 0x80081b50, 67372036, 'int32_t*')
            setValue(mem, 0x80081b54, 67372036, 'int32_t*')
            setValue(mem, 0x80081b58, 67372036, 'int32_t*')
            setValue(mem, 0x80081b5c, 67372036, 'int32_t*')
            setValue(mem, 0x80081b60, 67372036, 'int32_t*')
            setValue(mem, 0x80081b64, 263172, 'int32_t*')
        end
        imgui.SameLine()
        if (imgui.Button("All Locked")) then
            setValue(mem, 0x80081b48, 0, 'int32_t*')
            setValue(mem, 0x80081b4c, 0, 'int32_t*')
            setValue(mem, 0x80081b50, 0, 'int32_t*')
            setValue(mem, 0x80081b54, 0, 'int32_t*')
            setValue(mem, 0x80081b58, 0, 'int32_t*')
            setValue(mem, 0x80081b5c, 0, 'int32_t*')
            setValue(mem, 0x80081b60, 0, 'int32_t*')
            setValue(mem, 0x80081b64, 0, 'int32_t*')
        end
    end
end

function position()
    if (imgui.CollapsingHeader("Position", ImGuiTreeNodeFlags_None)) then
        local x = readValue(mem, 0x800b6704, 'int32_t*')
        local y = readValue(mem, 0x800b6708, 'int32_t*')
        local ind = closestPoints(Xc, Yc, x, y)
        doSliderInt(mem, 0x800b6704, 'Map X', -3000000, 3000000, 'int32_t*')
        doSliderInt(mem, 0x800b6708, 'Map Y', -2000000, 2000000, 'int32_t*')
        doSliderInt(mem, 0x800b670c, 'Map Z', -300000, 300000, 'int16_t*')

        imgui.TextUnformatted(Pp[ind])
        -- doSliderInt(mem, 0x800b6728, 'Map X2', -3000000, 3000000, 'int32_t*')
        -- doSliderInt(mem, 0x800b6724, 'Map Z2', -3000000, 300000, 'int16_t*')
        -- doSliderInt(mem, 0x800b672c, 'Map Y2', -3000000, 3000000, 'int32_t*')
    end
end

function saveMenu()
    if (imgui.CollapsingHeader("Saves", ImGuiTreeNodeFlags_None)) then
        imgui.BeginTable("SaveTable", 2, imgui.constant.TableFlags.Resizable)
        imgui.TableSetupColumn("Load")
        imgui.TableSetupColumn("Save")
        imgui.TableHeadersRow();
        for i, f in pairs(saveList) do
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
    end
end

function pythonStuff()
    if (imgui.CollapsingHeader("Python", ImGuiTreeNodeFlags_None)) then
        toggledTCP, setTCP = imgui.Checkbox("TCP", setTCP)
        netTCP(toggledTCP, setTCP)

        trackChanged, dumpTrack = imgui.Checkbox("Dump Track X-Y", dumpTrack)
        if trackChanged then
            if dumpTrack then
                openTrack()
            else
                closeTrack()
            end
        else
            if dumpTrack then writeTrack() end
        end
    end
end

function DrawImguiFrame()
    -- Utilizing the DrawImguiFrame periodic function to draw our UI.
    -- We are declaring this function global so the emulator can
    -- properly call it periodically.
    local show = imgui.Begin('GT Panel', true)
    if not show then
        imgui.End()
        return
    end
    -- local racing = checkValue(mem, 0x8008df72, 58, "int8_t*") -- check if the time is displayed
    if hasPal then
        if (imgui.Button("Reload")) then
            reload()
        end


        imgui.BeginTable("TopTable", 2, imgui.constant.TableFlags.Resizable)
        imgui.TableNextRow()
        imgui.TableSetColumnIndex(0)
        saveMenu()
        imgui.TableSetColumnIndex(1)
        pythonStuff()
        imgui.EndTable()

        imgui.BeginTable("VehicleTable", 2, imgui.constant.TableFlags.Resizable)
        imgui.TableNextRow()
        imgui.TableSetColumnIndex(0)
        carInfo()
        lapTimes()
        imgui.TableSetColumnIndex(1)
        tyres()
        raceCondition()
        position()
        simulation()
        imgui.EndTable()
        funkyStuff()
        imgui.End()
    end
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

function getCollision(state)

    if state == 1 then
        return "front left"
    elseif state == 2 then
        return "front right"
    elseif state == 3 then
        return "front"
    elseif state == 4 then
        return "rear left"
    elseif state == 5 then
        return "unknown 1"
    elseif state == 6 then
        return "unknown 2"
    elseif state == 7 then
        return "unknown 3"
    elseif state == 8 then
        return "rear right"
    elseif state == 12 then
        return "rear"
    else 
        return "no collision"
    end
end


if checked then checked:remove() end
checked = PCSX.Events.createEventListener('ExecutionFlow::Run', checkRegion)
PCSX.resumeEmulator()

-- to check https://www.mogelpower.de/cheats/Gran-Turismo-PAL_XP-PSX_4107.html
-- to check https://www.gtplanet.net/forum/threads/xenns-cheat-device-codes-includes-demo-codes.187354/
-- A6 is an if/set
-- if address equals 0002, set to 0001
-- A7 is an if/set with a restore option, so if you disable cheats as the game is running, it reverses the operation
