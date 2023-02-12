hasPal = false
hasUs = false
hasJap = false
forPlay = true
netStatus = false
dumpTrack = false

loadfile("memory.lua")()
loadfile("tcp.lua")()
loadfile("track.lua")()

local function reload()
    PCSX.pauseEmulator()
    loadfile("memory.lua")()
    loadfile("gt.lua")()
    loadfile("tcp.lua")()
    loadfile("track.lua")()
end

saveList = {
    { "Start",                 "start1.slice" },
    { "Arcade Start",          "arc1.slice" },
    { "Arcade HS R33",         "arc2.slice" },
    { "Arcade HS R33 mid-lap", "arc4.slice" },
    { "Arcade HS Corv",        "arc3.slice" },
    { "Sim Endurance Race",    "sim4.slice" },
    { "Simulation Home",       "sim1.slice" },
    { "SARD Supra HS",         "sim2.slice" },
    { "0-400m Test MR2",       "sim3.slice" }
}


mem = PCSX.getMemPtr()

function DrawImguiFrame()
    -- Utilizing the DrawImguiFrame periodic function to draw our UI.
    -- We are declaring this function global so the emulator can
    -- properly call it periodically.
    local show = imgui.Begin('GT Panel', true)
    if not show then imgui.End() return end
    local racing = checkValue(mem, 0x8008df72, 58, "int8_t*") -- check if the time is displayed
    if hasPal then
        if (imgui.Button("Reload")) then
            reload()
        end
        
        imgui.BeginTable("TopTable", 2, imgui.constant.TableFlags.Resizable)
        imgui.TableNextRow()
        imgui.TableSetColumnIndex(0)
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

        imgui.TableSetColumnIndex(1)
        if (imgui.CollapsingHeader("Python", ImGuiTreeNodeFlags_None)) then
            netChanged, netStatus = imgui.Checkbox("TCP", netStatus)
            netStatus = netTCP(netChanged, netStatus)

            trackChanged, dumpTrack = imgui.Checkbox("Dump Track X-Y", dumpTrack)
            if trackChanged then
                if dumpTrack then openTrack()
                else closeTrack() end
            else 
                if dumpTrack then writeTrack() end
            end
        end
        imgui.EndTable() 
        
        imgui.BeginTable("VehicleTable", 2, imgui.constant.TableFlags.Resizable)
        imgui.TableNextRow()
        imgui.TableSetColumnIndex(0)
        if (imgui.CollapsingHeader("Car", ImGuiTreeNodeFlags_None)) then
            doSliderInt(mem, 0x800b66ec, 'Speed', 0, 5000, 'uint16_t*')
            doSliderInt(mem, 0x800b66ee, 'Engine Speed', 0, 9000, 'uint16_t*')
            doSliderInt(mem, 0x800b66f8, 'Boost', 0, 12000, 'uint16_t*')
            doSliderInt(mem, 0x800bd990, 'Max Speed', 0, 5000, 'uint16_t*')
            doSliderInt(mem, 0x800b66e8, 'Gear', 0, 10, 'uint8_t*')
            doSliderInt(mem, 0x800b66d6, 'Steering', -580, 580, 'int16_t*')
            doSliderInt(mem, 0x800b66d9, 'Accel (Button)', 0, 16, 'uint8_t*')
            doSliderInt(mem, 0x800b66db, 'Accel (Transfer)', 0, 16, 'uint8_t*')
            doSliderInt(mem, 0x800b66dd, 'Brake', 0, 16, 'uint16_t*')
            doSliderInt(mem, 0x800b6d63, 'Clutch', 0, 3, 'uint16_t*')
        end
        imgui.TableSetColumnIndex(1)
        if (imgui.CollapsingHeader("Tyres", ImGuiTreeNodeFlags_None)) then
            imgui.BeginTable("Tyre", 2, imgui.constant.TableFlags.Resizable)
            imgui.TableNextRow()
            imgui.TableSetColumnIndex(0)
            doSliderInt(mem, 0x800b6778, 'Fr Left off', 0, 2, 'int8_t*')
            doSliderInt(mem, 0x800b6800, 'Re Left off', 0, 2, 'int8_t*')
            doSliderInt(mem, 0x800b67d6, 'Left tyre slip', 0, 255, 'uint8_t*')
            imgui.TableSetColumnIndex(1)
            doSliderInt(mem, 0x800b67bc, 'Fr Right off', 0, 2, 'int8_t*')
            doSliderInt(mem, 0x800b6844, 'Re Right off', 0, 2, 'int8_t*')
            doSliderInt(mem, 0x800b681a, 'Right tyre slip', 0, 255, 'uint8_t*')
            --imgui.TableNextRow()
            --imgui.TableSetColumnIndex(0)
            imgui.EndTable()
        end
        if (imgui.CollapsingHeader("Race Condition", ImGuiTreeNodeFlags_None)) then
            imgui.BeginTable("Tyre", 2, imgui.constant.TableFlags.Resizable)
            imgui.TableNextRow()
            imgui.TableSetColumnIndex(0)
            doSliderInt(mem, 0x800b6d69, 'Car Position', 1, 6, 'uint8_t*')
            doCheckbox(mem, 0x800b6358, 'HUD On', 0, 1, 'int16_t*') -- (PAL SCES-00984)
            doCheckbox(mem, 0x800b615c, 'Not Replay', 0, 1, 'int32_t*') -- (PAL SCES-00984)
            imgui.EndTable()
        end
        imgui.EndTable()
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

if checked then checked:remove() end
checked = PCSX.Events.createEventListener('ExecutionFlow::Run', checkRegion)
PCSX.resumeEmulator()
