Xc = {}
Yc = {}
Pp = {}
local csv = require("csv")
local f = csv.open("HighSpeedRing.csv")
TableSize = 0

for fields in f:lines() do
    table.insert(Xc,tonumber(fields[1]))
    table.insert(Yc,tonumber(fields[2]))
    table.insert(Pp,tonumber(fields[3]))
    TableSize = TableSize + 1
end

 

-- function closestValue(array, value)
--     local low = 1
--     local high = #array
--     local closest = nil
--     local mid

--     while low <= high do
--         mid = math.floor((low + high) / 2)
--         local diff = math.abs(value - array[mid])

--         if closest == nil or diff < math.abs(value - closest) then
--             closest = array[mid]
--         end

--         if array[mid] == value then
--             return array[mid]
--         elseif array[mid] < value then
--             low = mid + 1
--         else
--             high = mid - 1
--         end
--     end
--     return mid
-- end

function closestPoints(x,y, target_x, target_y)
    local closest = nil
    local closest_distance = nil
    local indFound

    for ind, point in ipairs(x) do
        local distance = math.sqrt((target_x - x[ind]) ^ 2 + (target_y - y[ind]) ^ 2)

        if closest == nil or distance < closest_distance then
            closest = point
            closest_distance = distance
            indFound = ind
        end
    end
    return indFound
end
