HEADER = 10

function startClient(name)
    changed, check = imgui.Checkbox(name, check)
    if changed then
        if check then
            client = Support.File.uvFifo("127.0.0.1", 9999)
            print(changed, check)
        else
            client:close()
            print(changed, check)
        end
    elseif check then
        client:write(PCSX.SIO0.slots[1].pads[1].getButton(PCSX.CONSTS.PAD.BUTTON.CROSS))
        data = client:readU8()
        if data == 1 then
            print("1")
            PCSX.SIO0.slots[1].pads[1].setOverride(PCSX.CONSTS.PAD.BUTTON.CROSS)
        else
            print("2")
            PCSX.SIO0.slots[1].pads[1].clearOverride(PCSX.CONSTS.PAD.BUTTON.CROSS)
        end
        -- a = PCSX.GPU.takeScreenShot()
        -- print (a.width)
        -- client:write(a.width)
        data = 0
    end
end
