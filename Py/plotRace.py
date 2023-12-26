import pandas as pd
import matplotlib.pyplot as plt

file_path = 'Py/CNN_trial4.csv'
plot_both_laps = False

column_names = ['laps', 'x', 'y', 'red_values']
df = pd.read_csv(file_path, header=None, names=column_names)

# Normalize red values to be in the range [0, 1]
df['normalized_red_values'] = df['red_values'] / 300

df = df[(df['laps'] != 0) & (df['laps'] != 3)]
unique_laps = df['laps'].unique()

if len(unique_laps) == 1:
    # Only one lap, create a single subplot
    fig, ax = plt.subplots(1, 1, figsize=(8, 5))
    
    lap_data = df[df['laps'] == unique_laps[0]]

    # Create a scatter plot for the lap
    ax.scatter(lap_data['x'], lap_data['y'], c=[[r, 1-r, 0]
               for r in lap_data['normalized_red_values']], marker='.', s=20)
    ax.tick_params(axis='both', which='both', bottom=False, top=False, left=False, right=False,
                   labelbottom=False, labeltop=False, labelleft=False, labelright=False)

    ax.set_title(f'Lap {unique_laps[0]}')
    text_box = f'Mean Speed: {lap_data["red_values"].mean():.2f} km/h\nMax Speed: {lap_data["red_values"].max():.2f} km/h '
    ax.text(0.05, 0.95, text_box, transform=ax.transAxes, fontsize=10,
            verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    ax.set_xlim(-2716523.4, 2324895.4)

else:
    # Two laps, create two subplots
    fig, axes = plt.subplots(2, 1, figsize=(8, 10))

    for lap, ax in zip(unique_laps, axes):
        lap_data = df[df['laps'] == lap]

        # Create a scatter plot for each lap
        ax.scatter(lap_data['x'], lap_data['y'], c=[[r, 1-r, 0]
                   for r in lap_data['normalized_red_values']], marker='.', s=20)
        ax.tick_params(axis='both', which='both', bottom=False, top=False, left=False, right=False,
                       labelbottom=False, labeltop=False, labelleft=False, labelright=False)

        ax.set_title(f'Lap {lap}')
        text_box = f'Mean Speed: {lap_data["red_values"].mean():.2f} km/h\nMax Speed: {lap_data["red_values"].max():.2f} km/h '
        ax.text(0.05, 0.95, text_box, transform=ax.transAxes, fontsize=10,
                verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        ax.set_xlim(-2716523.4, 2324895.4)

plt.tight_layout()
plt.show()
