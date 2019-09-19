import auto_smart

import json
import os
import numpy as np
import pandas as pd

# info = auto_smart.read_info("demo/data")
# train_data,train_label = auto_smart.read_train("demo/data",info)
# test_data = auto_smart.read_test("demo/data",info)

TYPE_MAP = {
    'time': str,
    'cat': str,
    'multi-cat': str,
    'num': np.float64
}

def read_info(datapath):
    with open(join(datapath, 'info.json'), 'r') as info_fp:
        info = json.load(info_fp)
    return info


def read_train(datapath, info):
    train_data = {}
    
    info['main'] = pd.

        

        

    # get train label
    train_label = pd.read_csv(
        join(datapath, 'train', 'main_train.solution'))['label']
    return train_data, train_label


info = read_info('demo/test_data')

auto_smart.train_and_predict(train_data,train_label,info,test_data)

