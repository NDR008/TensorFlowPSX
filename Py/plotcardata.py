import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


df1 = pd.read_csv('py/mr2.csv')
df2 = pd.read_csv('py/supra.csv')

num_columns = len(df1.columns)

fig, axes = plt.subplots(nrows=num_columns, ncols=2,
                         sharex=True, figsize=(15, 6*num_columns))

label = ['Throttle', 
        'Clutch',
        'Engine speed',
        'Turbo boost',
        'Vehicle speed']

colors = ['b', 'g', 'r', 'c', 'm']

# Plot each column on a separate subplot
for j in range(2):
    if j==0:
        df = df1
    else:
        df = df2
    for i in range(num_columns):
        ax = axes[i, j]
        ax.plot(df.iloc[:1600,i], label=label[i], color=colors[i])
        ax.set_ylabel(label[i])
        ax.legend()
        ax.grid(True)
        ax.set_xticks(np.arange(0, 1601, 200))
    axes[-1, j].set_xlabel('Game Step')

#plt.tight_layout()
plt.show()
