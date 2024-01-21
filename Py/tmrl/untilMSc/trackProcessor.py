# https://github.com/trackmania-rl/tmrl/blob/e3254888ae7e865c56236d72fb03311a41c10310/tmrl/tools/record.py#L66
import numpy as np

def line(pt1, pt2, dist):
    """
    Creates a point between pt1 and pt2, at distance dist from pt1.

    If dist is too large, returns None and the remaining distance (> 0.0).
    Else, returns the point and 0.0 as remaining distance.
    """
    vec = pt2 - pt1
    norm = np.linalg.norm(vec)
    if norm < dist:
        return None, dist - norm  # we couldn't create a new point but we moved by a distance of norm
    else:
        vec_unit = vec / norm
        pt = pt1 + vec_unit * dist
        return pt, 0.0

def loadData(filename):
    originalTable = []
    import csv
    with open(filename, newline='') as csvfile:
        data = csv.reader(csvfile, delimiter=',')
        for row in data:
            originalTable.append((int(row[0]), int(row[1])))
            
    return np.array(originalTable)

def processData(originalTable, spacing):    
    dist_between_points = spacing
    index = 1
    move_by = dist_between_points
    pt1 = originalTable[0]
    finalTable = [originalTable[0]]
    while  index < len(originalTable):
        pt2 = originalTable[index]
        pt, dst = line(pt1, pt2, move_by)
        if pt is not None:  # a point was created
            savept = (round(pt[0], 10), round(pt[1], 10))
            finalTable.append(savept)  # add the point to the list
            move_by = dist_between_points
            pt1 = pt
        else:  # we passed pt2 without creating a new point
            pt1 = pt2
            index += 1
            move_by = dst  # remaining distance
    return finalTable
            
def saveData(filename, finalTable):
    filename = filename[:-4]
    name = filename + "Spaced.csv"
    np.savetxt(name, finalTable, delimiter=",")
    

def respaceTrackData(filename, spacing=50000):
    originalTable = loadData(filename)
    newTable = processData(originalTable, spacing)
    saveData(filename, newTable)
    
respaceTrackData('Py/route5.csv',spacing=700)