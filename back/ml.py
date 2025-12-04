import pandas as pd
import numpy as np

data = pd.read_csv('usd_history.csv', encoding='latin1')
features = ['date', 'rate']
data = data[features]

mode_value = data['rate'].mode()[0]
data['rate'].fillna(mode_value, inplace=True)


