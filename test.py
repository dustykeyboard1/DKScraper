# Main File
from tqdm import tqdm
from tqdm.auto import tqdm
import numpy as np

print(float(np.nan))

list = [1, 2, 3, 4, float(np.nan), float(np.nan), 1, 2, 3, 4]
import statistics as st

print(st.mean(list))
print(sum(list))
