# Main File
from tqdm import tqdm
from tqdm.auto import tqdm

tqdm.pandas()
import pandas as pd

df1 = pd.DataFrame([[1, 2, 3, 4], [2, 3, 4, 5], [4, 5, 6, 7]])
df_dict = {"p": df1, "a": df1, "c": df1}

with pd.ExcelWriter("DataFrames/testoutput.xlsx", engine="xlsxwriter") as writer:
    for stat_type, df in df_dict.items():
        df.to_excel(writer, sheet_name=stat_type)
