import logging
import pandas as pd
from icecream import ic

async def modify_dataframe(df_1):
    # Убедитесь, что создается копия датафрейма, если необходимо
    df_1 = df_1.copy()
    
    df_1['icon_status'] = ''
    # Применяем функции к столбцам
    df_1['forces_aps'] = df_1['forces_aps'].apply(lambda x: x if x > 0 else '')
    df_1['forces_lps'] = df_1['forces_lps'].apply(lambda x: x if x > 0 else '')

    # Добавляем новый столбец icon_status и заполняем его
    df_1['icon_status'] = df_1['fire_status'].apply(
        lambda x: '🔴' if x == 'Продолжается' else
        '🟢' if x == 'Ликвидирован' else
        '🟠' if x == 'Частично локализован' else
        '🟡' if x == 'Локализован' else
        '❌' if x == 'Закрыт по решению КЧС' else
        '⬇️' if x == 'Ослабевает' else
        '🔺' if x == 'Усиливается' else ""
    )

    return df_1
