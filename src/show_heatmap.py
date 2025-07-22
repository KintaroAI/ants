import pandas as pd
import numpy as np

df = pd.read_csv('results.txt', header=None, names=['num_ants', 'num_food', 'steps', 'a_alive', 'b_alive'])

MAX_STEPS = 500000  # Adjust based on your code

def classify(row):
    if row['steps'] >= MAX_STEPS:
        return 'Timeout (No Divergence)'
    elif row['a_alive'] + row['b_alive'] < 2:
        return 'Colony Death'
    else:
        return 'Successful Divergence'

df['outcome'] = df.apply(classify, axis=1)
df['steps_norm'] = np.clip(df['steps'], 0, MAX_STEPS)

# Heatmaps
# Seaborn Code

import seaborn as sns
import matplotlib.pyplot as plt

# Outcome numeric for coloring
outcome_map = {'Successful Divergence': 2, 'Colony Death': 1, 'Timeout (No Divergence)': 0}
df['outcome_num'] = df['outcome'].map(outcome_map)

# Pivot for grid
pivot_outcome = df.pivot(index='num_ants', columns='num_food', values='outcome_num')
pivot_steps = df.pivot(index='num_ants', columns='num_food', values='steps_norm')

# Outcome Heatmap
plt.figure(figsize=(12, 10))
sns.heatmap(pivot_outcome, cmap='RdYlGn', annot=False, cbar_kws={'ticks': [0,1,2], 'label': 'Outcome (0=Timeout, 1=Death, 2=Success)'})
plt.title('Outcome Heatmap: Divergence Success by Ants and Food')
plt.xlabel('Number of Food')
plt.ylabel('Number of Ants')
plt.show()

# Steps Heatmap (among successes only, to focus on divergence time)
success_df = df[df['outcome'] == 'Successful Divergence']
pivot_steps_success = success_df.pivot(index='num_ants', columns='num_food', values='steps_norm')
plt.figure(figsize=(12, 10))
sns.heatmap(pivot_steps_success, cmap='viridis_r', annot=False)  # _r for reverse: low steps = dark
plt.title('Steps to Divergence (Success Cases Only)')
plt.xlabel('Number of Food')
plt.ylabel('Number of Ants')
plt.show()

# Plotly Code
import plotly.express as px

# Outcome Heatmap
fig = px.imshow(pivot_outcome, color_continuous_scale='RdYlGn', aspect='auto',
                labels=dict(color='Outcome (0=Timeout, 1=Death, 2=Success)'))
fig.update_layout(title='Outcome Heatmap: Divergence Success by Ants and Food',
                  xaxis_title='Number of Food', yaxis_title='Number of Ants')
fig.show()  # Or fig.write_html('outcome_heatmap.html') for export

# Steps Heatmap
fig_steps = px.imshow(pivot_steps, color_continuous_scale='viridis_r', aspect='auto')
fig_steps.update_layout(title='Steps to Outcome Heatmap',
                        xaxis_title='Number of Food', yaxis_title='Number of Ants')
fig_steps.show()

# Contour Plot (For Steps Gradient)
# Matplotlib Code

from scipy.interpolate import griddata

# Grid for interpolation
xi = np.linspace(1, 100, 100)
yi = np.linspace(1, 100, 100)
zi = griddata((df['num_ants'], df['num_food']), df['steps_norm'], (xi[None,:], yi[:,None]), method='linear')

plt.figure(figsize=(12, 10))
contour = plt.contourf(xi, yi, zi, levels=20, cmap='viridis_r')
plt.colorbar(contour)
plt.scatter(df['num_ants'], df['num_food'], c='black', s=5)  # Overlay points
plt.title('Contour Plot: Steps to Outcome')
plt.xlabel('Number of Ants')
plt.ylabel('Number of Food')
plt.show()

# 3D Surface/Scatter (Depth for Steps)
# Plotly Code (Interactive 3D)

fig_3d = px.scatter_3d(df, x='num_ants', y='num_food', z='steps_norm', color='outcome',
                       size='steps_norm', opacity=0.7, color_discrete_map={'Successful Divergence': 'green', 'Colony Death': 'red', 'Timeout (No Divergence)': 'blue'})
fig_3d.update_layout(title='3D Scatter: Steps by Outcome')
fig_3d.show()

# Faceted Plots (Breakdown by Outcome)
# Seaborn Code
g = sns.FacetGrid(df, col='outcome', col_wrap=3, height=5)
g.map(sns.scatterplot, 'num_ants', 'num_food', 'steps_norm')  # Color by steps
g.add_legend()
g.set_titles('{col_name}')
plt.show()