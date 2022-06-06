'''
Created on Jul. 23, 2019
Data analysis of the simulation results.

@file    simulator_analysis.py
@author  Evandro de Souza
@date    2019.07.23  
@version 0.1
@company University of Alberta - Computing Science
'''

import matplotlib.pyplot as plt
import pandas as pd
import sys

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
for col in df:
    df_sets.append(df[col])
    df_names.append(col)
    if (max_t < max(df[col]['t'])): max_t = max(df[col]['t'])

fig, axs = plt.subplots(len(df_sets))
fig.set_size_inches(11, 18.5)
plt.subplots_adjust(left=None, bottom=None, right=None, top=None, wspace=None, hspace=None)
plt.xlabel('Time (ms)')
with open('res_values.txt','w') as outfile:
    for i in range(len(df_sets)):
        axs[i].set_title(df_names[i])
        axs[i].plot(df_sets[i]['t'], df_sets[i]['v'], '.')
        axs[i].set_xlim(-5, max_t+5)
        axs[i].grid(visible=True, which='both', axis='both')
        outfile.write(df_names[i])
        outfile.write('\n')
        outfile.write('\n'.join(map(str, df_sets[i]['v'])))
        outfile.write('\n')

plt.tight_layout()
fig.savefig('Monitor.png', dpi=100)





