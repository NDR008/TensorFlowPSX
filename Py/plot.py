# Plot the driving

import pandas as pd
import matplotlib.pyplot as plt

file_path = 'Py/drive.csv'

column_names = ['lap', 'x', 'y', 'red']

df = pd.read_csv(file_path, header=None, names=column_names)

lap_values = df['lap']
x_values = df['x']
y_values = df['y']
red_values = df['red']

normalized_red_values = red_values / 300.0

plt.scatter(x_values, y_values, c=[[r, 0, 0]
            for r in normalized_red_values], marker='.')

# Add labels and title
plt.xlabel('X-coordinate')
plt.ylabel('Y-coordinate')
plt.title('Scatter Plot with Red Shades')

# Show the plot
plt.show()
