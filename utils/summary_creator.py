




from datetime import timedelta, datetime as dt

import pandas as pd


async def summary_creator(df: pd.DataFrame, yesterday_end=None):
    
    now = dt.now()
    yesterday_end = (now - timedelta(days=1)).replace(hour=23,
                                                          minute=59, second=59, microsecond=999999)
    response = ""
    
    
    # for df.itterows():
        
    
    
    
    
    return response