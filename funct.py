import sys, os
import pandas as pd
import numpy as np
from scipy.special import gamma

def read_data_excel(IndexTable, indices, file, sheet_name=None, extra_columns=None):
    if not all(np.in1d([i for i in indices],IndexTable.IndexLetter)):
        raise Exception("Not all indices are part of the IndexTable!")
    df = pd.read_excel(file, sheet_name=sheet_name)
    if indices=='':
        s = pd.DataFrame(df['value'].tolist(), columns=['value'])
    else:
        aspects = [IndexTable.IndexLetter[IndexTable.IndexLetter == i].index.values[0] for i in indices]
        cols = [asp.lower() for asp in aspects]
        cols.append('value')
        if extra_columns:
            for i in extra_columns:
                cols.append(i)
        df = df[cols]
        for asp in aspects:
            items = IndexTable.Classification[asp].Items
            df = df[df[asp.lower()].isin(items)]
    return df

def reduce_dimensions(IndexTable, durable, par_dict):
    dict_values = {}
    for name in par_dict.keys():
        indices = par_dict[name].Indices
        values = par_dict[name].Values
        if 'd' in indices: # reduce the d dimension
            M = indices.index('d') # dimension of Durable
            index = [slice(None)]*len(indices)
            index[M] = IndexTable.Classification['Durable'].Items.index(durable)
            values = values[tuple(index)]
        if 'a' in indices and durable not in ['furniture', 'cupboard']: # reduce the a dimension
            M = indices.index('a') # dimension of Appliance
            index = [slice(None)]*len(indices)
            index[M] = IndexTable.Classification['Appliance'].Items.index(durable)
            values = values[tuple(index)]
        dict_values[name] = values
    return dict_values

def multiply_by_uncertainty(durable, problem, param_values_r, dict_values,ParameterDict):
    dict_values_r = {}
    for name in ParameterDict.keys():
        if name in problem['names']:
            i = problem['names'].index(name)
            dict_values_r[name] = dict_values[name]*(1+param_values_r[i])
        else:
            dict_values_r[name] = dict_values[name]
    u_inflows = [param_values_r[i] for i,name in enumerate(problem['names']) if name.startswith('I-seg-')]
    if u_inflows:
        i_seg_d = ParameterDict['I'].MetaData[durable]
        dict_values_r['I'] = i_seg_d.multiply_inflows_by_piecewise_uncert(u_inflows)
    return dict_values_r


def reciprocal(array):
    mask = array != 0
    with np.errstate(divide='ignore'):
        new_array = 1 / array
    new_array[mask == 0] = 0
    return new_array

def read_parameter_excel(IndexTable, indices, file, sheet_name=None, append_value=True, extra_columns=None, df_as_output=False):
    if len(IndexTable.Classification['Element'].Items) == 1:
        indices2 = indices.replace('e','') #element ignored
    else:
        indices2 = indices
    if not all(np.in1d([i for i in indices2],IndexTable.IndexLetter)):
        raise Exception("Not all indices are part of the IndexTable!")
    df = pd.read_excel(file, sheet_name=sheet_name)
    
    add_cols = []
    if append_value:
        add_cols.append('value')
    if extra_columns:
        for i in extra_columns:
            add_cols.append(i)

    if indices=='':
        s = pd.DataFrame(df[add_cols], columns=add_cols)
    else:
        aspects = [IndexTable.IndexLetter[IndexTable.IndexLetter == i].index.values[0] for i in indices2]
        cols = [asp.lower() for asp in aspects]
        for i in add_cols:
            cols.append(i)
        df = df[cols]
        for asp in aspects:
            items = IndexTable.Classification[asp].Items
            df = df[df[asp.lower()].isin(items)]
        arrays = [pd.CategoricalIndex(df[asp.lower()], categories=IndexTable.Classification[asp].Items, ordered=True) for asp in aspects]
        names = [asp.lower() for asp in aspects]
        index = pd.MultiIndex.from_arrays(arrays, names=names)
        s = pd.DataFrame(df[add_cols].values, columns=add_cols, index=index)
        s = s.sort_values(by=names)
    if df_as_output is False:
        try:
            aspects_with_e = [IndexTable.IndexLetter[IndexTable.IndexLetter == i].index.values[0] for i in indices]
            output = np.reshape(s['value'].values,[IndexTable.IndexSize[asp] for asp in aspects_with_e])
        except ValueError:
            raise Exception('Not all values were found')
    else:
        output = s
    return output


def calculate_age(array, isstock=True, inflows=None):
    years = np.arange(len(array))
    if isstock: # stock at the end of the year
        age_matrix = np.array([years]).T - np.array([years])+1
        age_matrix[np.triu_indices(age_matrix.shape[0])] = 0
        np.fill_diagonal(age_matrix, 1)
    else: # outflows during the year
        age_matrix = np.array([years]).T - np.array([years])
        age_matrix[np.triu_indices(age_matrix.shape[0])] = 0
    if inflows is not None:
        array = np.einsum('tc,c->tc', array, reciprocal(inflows))
    
    shares = np.einsum('tc,t->tc',array, reciprocal(array.sum(axis=1))) # calculate the distribution of cohorts in each year (shares of the total)
    age = np.einsum('tc,tc->t',shares,age_matrix)
    return age


def mean_from_scale_parameters(scale, dict_values):
    shape = dict_values['k']
    mu = scale*gamma(1+1/shape) # λΓ(1+1/k)
    return mu