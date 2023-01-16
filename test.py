import pandas as pd

df = pd.DataFrame(index=["mcw1217","adfad"],data=[[0,1,2],[0,1,3]],columns=[0,1,2])
df.reset_index()
df.index=['as','asd']
print(df)


