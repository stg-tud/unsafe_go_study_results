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


study_projects_df = packages_df\
    [packages_df['is_standard']==False]\
    .groupby('project_name')['package_unsafe_sum'].sum()\
    .sort_values(ascending=False)\
    .reset_index()[:10]

df = pd.merge(study_projects_df, projects_df, how='left', on='project_name', validate='many_to_one')\
    .loc[:,['project_name', 'project_number_of_stars', 'project_number_of_forks', 'project_revision']]\
    .rename(columns={'project_name': 'Name', 'project_number_of_stars': 'Stars', 'project_number_of_forks': 'Forks',
                    'project_revision': 'Revision'})

df.index = df.index + 1

print(df.to_latex(index=True))

