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


def number_or_nothing(n):
    if n > 0:
        return str(n).rjust(3)
    else:
        return " "

labels2_in_order = ['efficiency', 'serialization', 'generics', 'no-gc', 'atomic', 'ffi',
                  'hide-escape', 'layout', 'types', 'reflect', 'unused']

labels2_abbrev = { 'generics': 'gen', 'efficiency': 'eff', 'serialization': 'ser',
                'reflect': 'reflect', 'layout': 'layout', 'hide-escape': 'HE', 'unused': 'unused',
                'no-gc': 'no GC', 'ffi': 'FFI', 'atomic': 'atomic', 'types': 'types'}

labels1_in_order = [ # 'cast',
                   'memory-access', 'pointer-arithmetic', 'definition', 'delegate',
                   'syscall', 'unused']

column_sums_app = [0] * len(labels2_in_order)
column_sums_std = [0] * len(labels2_in_order)


## add header

classification_summary = [[' '] +
                          [item for sublist in
                              [[labels2_abbrev[label2], '']
                               for label2 in labels2_in_order]
                               for item in sublist] +
                          ['.', '']]
classification_summary.append([' '] +
                              [item for sublist in
                                  [['app', 'std'] for i in range(len(labels2_in_order)+1)]
                                  for item in sublist])

## add 'cast' row

labels1_cast = ['cast-struct', 'cast-basic', 'cast-header', 'cast-bytes', 'cast-pointer']

values_app_cast = [sampled_usages_app\
            .where(sampled_usages_app['label'].isin(labels1_cast))\
            .where(sampled_usages_app['label2']==label2)\
            .dropna()\
            ['line_number'].count()
         for label2 in labels2_in_order]
values_std_cast = [sampled_usages_std\
            .where(sampled_usages_std['label'].isin(labels1_cast))\
            .where(sampled_usages_std['label2']==label2)\
            .dropna()\
            ['line_number'].count()
         for label2 in labels2_in_order]

for i, value in enumerate(values_app_cast):
    column_sums_app[i] += value
for i, value in enumerate(values_std_cast):
    column_sums_std[i] += value

classification_summary.append(['cast'] +
                              [item for sublist in
                                   [[number_or_nothing(value_app_cast), number_or_nothing(value_std_cast)]
                                   for value_app_cast, value_std_cast in zip(values_app_cast, values_std_cast)]
                                   for item in sublist] +
                              [sum(values_app_cast), sum(values_std_cast)])

## add remaining rows

for label1 in labels1_in_order:
    values_app = [sampled_usages_app\
                .where(sampled_usages_app['label']==label1)\
                .where(sampled_usages_app['label2']==label2)\
                .dropna()\
                ['line_number'].count()
             for label2 in labels2_in_order]
    values_std = [sampled_usages_std\
                .where(sampled_usages_std['label']==label1)\
                .where(sampled_usages_std['label2']==label2)\
                .dropna()\
                ['line_number'].count()
             for label2 in labels2_in_order]

    for i, value in enumerate(values_app):
        column_sums_app[i] += value
    for i, value in enumerate(values_std):
        column_sums_std[i] += value

    classification_summary.append([label1] +
                                  [item for sublist in
                                       [[number_or_nothing(value_app), number_or_nothing(value_std)]
                                       for value_app, value_std in zip(values_app, values_std)]
                                       for item in sublist] +
                                  [sum(values_app), sum(values_std)])

classification_summary.append(['.'] +
                              [item for sublist in
                                  [[sum_app, sum_std]
                                  for sum_app, sum_std in zip(column_sums_app, column_sums_std)]
                                  for item in sublist] +
                              [sum(column_sums_app), sum(column_sums_std)])

column_names = classification_summary.pop(0)
df = pd.DataFrame(classification_summary, columns=column_names)

tex = df.to_latex(index=False).split('\n')

del tex[1]
del tex[2]
del tex[-3]

tex[0] = '\\begin{tabular}{r|cc|cc|cc|cc|cc|cc|cc|cc|cc|cc|cc|cc}'
tex[1] = tex[1].replace(".", "total")
tex[1] = tex[1].replace("{2}{l}", "{2}{c|}")
tex[1] = "{2}{c}".join(tex[1].rsplit('{2}{c|}', 1))
tex[1] += ' \\hline'
tex[2] += ' \\hline'
tex[-4] += ' \\hline'
tex[-3] = tex[-3].replace(".", "total")

for i in range(0, 6):
    tex.insert(4 + i*3, '\\rowcolor{verylightgray}')

print("\n".join(tex))

