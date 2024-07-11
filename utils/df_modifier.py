import logging
import pandas as pd
from icecream import ic

async def df_mod(conveted_name):
    df = pd.read_csv(f"{conveted_name}.csv")
    
    
    df['АПС'] = df['АПС'].apply(lambda x: x  if x > 0 else '')
    df['ЛПС'] = df['ЛПС'].apply(lambda x: x  if x > 0 else '')

    
    df['icon_status'] = ""
    df['icon_status'] = df['Статус'].apply(
        lambda x: '🔴' if x == 'Продолжается' else
        '🟢' if x == 'Ликвидирован' else
        '🟠' if x == 'Частично локализован' else
        '🟡' if x == 'Локализован' else
        '❌' if x == 'Закрыт по решению КЧП' else
        '⬇️' if x == 'Ослабевает' else
        '🔺' if x == 'Усиливается' else ""
    )
    
    return pd.DataFrame(df)