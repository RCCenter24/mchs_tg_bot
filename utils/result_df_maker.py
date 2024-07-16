import pandas as pd

async def result_df_maker(modified_df, df_subscribers):
    result_df = modified_df.merge(df_subscribers, left_on='map_id', right_on='map_id')
       
    return pd.DataFrame(result_df)