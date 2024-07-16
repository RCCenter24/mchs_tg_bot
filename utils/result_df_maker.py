import logging
import pandas as pd


async def result_df_maker(df, df_2):

    
    result_df = df.merge(df_2, left_on='ID Карты', right_on='map_id')
    
        
    return pd.DataFrame(result_df)