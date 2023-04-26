import csv
import numpy as np
import matplotlib.pyplot as plt
XY = []
dataPoints = 0

with open('./ReduxLua/HighSpeedRing.csv', 'r', encoding = 'utf-8-sig') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    for row in csv_reader:
       XY.append((int(row[0]),int(row[1]))) 
       dataPoints += 1 

XYarr = np.array(XY)

print(XYarr[0], XYarr[1])

m = (XYarr[1,0] - XYarr[1,1]) / (XYarr[0,0] - XYarr[0,1])
print(m)