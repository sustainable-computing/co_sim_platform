'''
Created on Aug. 24, 2019
Data scope of the simulation results.

@file    simulator_scope.py
@author  Evandro de Souza
@date    2019.08.24  
@version 0.1
@company University of Alberta - Computing Science
'''

import pandas as pd
import sys
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
 
 
#--- select dataset file
if len(sys.argv) > 1:
    storename = sys.argv[1]
else:
    storename = 'CollectorStore.hd5'
  
#--- Load data
store = pd.HDFStore(storename)
df = store['Collector']
store.close()
  
#--- select sets
df_sets = []
df_names = []
max_t = 0
min_t = 100000000
for col in df:
    df_sets.append(df[col])
    df_names.append(col)
    if (max_t < max(df[col]['t'])): max_t = max(df[col]['t'])
    if (min_t > min(df[col]['t'])): min_t = min(df[col]['t'])
 
 
fig, axs = plt.subplots(len(df_sets)+1)
plt.tight_layout()

 
for i in range(len(df_sets)): 
    axs[i].plot(df_sets[i]['t'], df_sets[i]['v'], '.')
    axs[i].set_xlim(-5, max_t+5)
    axs[i].set_title(df_names[i], loc='center')
    axs[i].grid(b=True, which='both', axis='both')
    

axs[len(df_sets)].axis('off')
 
axcolor = 'lightgoldenrodyellow'
axUpper = plt.axes([0.15, 0.10, 0.65, 0.03],  facecolor=axcolor)
axLower = plt.axes([0.15, 0.15, 0.65, 0.03], facecolor=axcolor)
 
sUpper = Slider(axUpper, 'Upper', min_t+1, max_t,   valinit = max_t - 10, valstep=1)
sLower = Slider(axLower, 'Lower', min_t,   max_t-1, valinit = min_t + 10, valstep=1)
 

def update(val):
    top = sUpper.val
    bottom = sLower.val
    if (top < bottom):
        top    = max_t
        bottom = min_t
    for i in range(len(df_sets)):
        axs[i].set_xlim(bottom-5, top+5)
    fig.canvas.draw_idle()   
 
sUpper.on_changed(update)
sLower.on_changed(update)
 
 
plt.show()





