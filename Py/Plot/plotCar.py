import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

df1 = pd.read_csv('Py/plot/Submaniac_car.csv')
df2 = pd.read_csv('Py/plot/MR2_mode_3_cont_2_4.58_AS_[128x128]_1W_car.csv')
#df2 = df1

doublePlot = True
num_columns = len(df1.columns)

fig, axes = plt.subplots(nrows=num_columns, ncols=2,
                         sharex=True, figsize=(15, 6*num_columns))

label = ['Throttle',
         'Brake',
        'Clutch',
        'Engine speed',
        'Turbo boost',
        'Vehicle speed']

colors = ['b', 'r', 'g', 'r', 'y', 'm']
y_limits = [(-500, 4500), (-500, 4500), (-0.5, 3.5),
            (3000, 8000), (4000, 8000), (-50, 250)]

# Plot each column on a separate subplot
for j in range(2):
    if j == 0 and doublePlot:
        df = df1
    else:
        df = df2
    for i in range(num_columns):
        ax = axes[i, j]
        ax.plot(df.iloc[:,i], label=label[i], color=colors[i])
        ax.set_ylabel(label[i])
        ax.legend()
        ax.grid(True)
        ax.set_ylim(y_limits[i])
        #ax.set_xticks(np.arange(0, , 200))
    axes[-1, j].set_xlabel('Game Step')

#plt.tight_layout()
plt.show()
