#!/usr/bin/env python3

import numpy as np
import pandas as pd
import matplotlib
from matplotlib import pyplot as plt
import tikzplotlib
import seaborn as sns

import json
from datetime import datetime


projects_df = pd.read_csv('../data/projects.csv', parse_dates=['project_created_at', 'project_last_pushed_at', 'project_updated_at'])
projects_df['project_revision'] = projects_df.apply(lambda x: x['project_revision'][:10], axis=1)
packages_df = pd.read_csv('../data/packages_0_499.csv').dropna()
geiger_df = pd.read_csv('../data/geiger_findings_0_499.csv')
sampled_usages_app = pd.read_csv('../data/sampled_usages_app.csv')
sampled_usages_std = pd.read_csv('../data/sampled_usages_std.csv')


## number of unsafe packages (without std) over hop count

df = packages_df\
    [(packages_df['is_standard']==False)&(packages_df['package_unsafe_sum']>0)]\
    .groupby(['project_name', 'package_hop_count'])['package_unsafe_sum'].count()\
    .unstack().fillna(0).T

distribution_df = packages_df\
    [(packages_df['is_standard']==False)&(packages_df['package_unsafe_sum']>0)]\
    .groupby('package_hop_count')['package_unsafe_sum'].count().T

sns.set(style="white")
sns.set(font_scale=1.4)

# create plot setup
fig, axs = plt.subplots(nrows=1, ncols=2, sharey=False, figsize=(24, 5), gridspec_kw={'width_ratios': [1, 14]})
fig.subplots_adjust(wspace=0)

# plot heatmap
sns.heatmap(df, ax=axs[1], cmap='Greens', cbar_kws={'label': 'Packages with Unsafe Usage'})

# plot distribution
sns.set_color_codes("pastel")
sns.barplot(distribution_df.values, distribution_df.index, orient='h', color="g", ax=axs[0])
axs[0].invert_xaxis()
axs[0].set_facecolor("white")

# labeling
for item in axs[1].get_yticklabels():
    item.set_rotation(0)
axs[1].set_xticks([])
axs[1].set_yticks([])
axs[1].set(ylabel="", xlabel="Projects (n={})".format(packages_df['project_name'].nunique()))
axs[0].set(ylabel="Import Depth", xlabel="")
sns.despine(bottom=True, left=True)
axs[0].set_xticks([])

plt.tight_layout()
plt.savefig('unsafe-import-depth.pdf', bbox_inches='tight')

