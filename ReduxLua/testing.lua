local pb = require('pb')
local protoc = require('protoc')

local function read_file_as_string(filename)
    local file = Support.File.open(filename)
    local buffer = file:read(tonumber(file:size()))
    file:close()
    return tostring(buffer)
end

local function check_load(chunk)
    local pbdata = protoc.new():compile(chunk)
    local ret, offset = pb.load(pbdata)
    if not ret then
        error("load error at " .. offset ..
            "\nproto: " .. chunk ..
            "\ndata: " .. buffer(pbdata):tohex())
    end
end

local proto_file = read_file_as_string('game.proto')
check_load(proto_file)

local screen = PCSX.GPU.takeScreenShot()
print(#screen.data)
screen.data = tostring(screen.data)
screen.bpp = tonumber(screen.bpp)
enc_bytes = assert(pb.encode("GT.Screen", screen))
print(#enc_bytes)
dec_bytes = pb.decode("GT.Screen", enc_bytes)
print(dec_bytes.bpp)
print(#dec_bytes.data)
