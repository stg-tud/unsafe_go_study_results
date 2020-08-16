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


def with_thousands_comma(n):
    return '{:,}'.format(n)

data = packages_df\
    .drop_duplicates(subset=['import_path', 'dir', 'module_path', 'module_version']).dropna()\
    .loc[:,['package_geiger_unsafe_pointer_sum', 'package_geiger_unsafe_sizeof_sum', 'package_geiger_unsafe_offsetof_sum',
           'package_geiger_unsafe_alignof_sum', 'package_geiger_slice_header_sum', 'package_geiger_string_header_sum',
           'package_geiger_uintptr_sum']]\
    .rename(columns={'package_geiger_unsafe_pointer_sum': 'unsafe.Pointer', 'package_geiger_unsafe_sizeof_sum': 'unsafe.Sizeof',
                    'package_geiger_unsafe_offsetof_sum': 'unsafe.Offsetof', 'package_geiger_unsafe_alignof_sum': 'unsafe.Alignof',
                    'package_geiger_slice_header_sum': 'reflect.SliceHeader', 'package_geiger_string_header_sum': 'reflect.StringHeader',
                    'package_geiger_uintptr_sum': 'uintptr'})\
    .sum()\
    .sort_values(ascending=False)

sns.set(style="whitegrid")

fig, ax = plt.subplots(figsize=(6, 2.5))

# Plot the distribution among types
sns.set_color_codes("muted")
g = sns.barplot(data.values, data.index, color="b")

# Add values next to the bars
for p in ax.patches:
    ax.annotate("{}".format(with_thousands_comma(int(p.get_width()))), (p.get_width(), p.get_y() + p.get_height() / 2.0),
                ha='left', va='center', fontsize=11, color='black', xytext=(5, 0),
                textcoords='offset points')
#_ = g.set_xlim(0, 120000) #To make space for the annotations

# Add a legend and informative axis label
ax.set(ylabel="", xlabel="Number of Unsafe Findings by Type")
sns.despine(bottom=True)

# Add thousands separator to x axis
ax.get_xaxis().set_major_formatter(matplotlib.ticker.FuncFormatter(lambda x, p: format(int(x), ',')))

plt.tight_layout()
plt.savefig('distribution-unsafe-types.pdf')
