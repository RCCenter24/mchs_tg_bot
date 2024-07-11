import logging
import pandas as pd


async def result_df_maker(df, df_2):

    date_format = '%d.%m.%Y %H:%M:%S'
    result_df = df.merge(df_2, left_on='ID Карты', right_on='map_id')
    try:
        result_df[['Дата ликвидации пожара', 'Дата изменения данных', 'Актуальность данных', 'Дата возникновения пожара']] = result_df[['Дата ликвидации пожара', 'Дата изменения данных', 'Актуальность данных', 'Дата возникновения пожара']]\
            .apply(pd.to_datetime, format=date_format, dayfirst=True, errors='coerce')

        result_df[['Дата ликвидации пожара', 'Дата изменения данных', 'Актуальность данных', 'Дата возникновения пожара']] = result_df[['Дата ликвидации пожара', 'Дата изменения данных', 'Актуальность данных', 'Дата возникновения пожара']]\
            .apply(lambda x: x.dt.strftime('%d.%m %H:%M'))
    except (KeyError, IndexError, AttributeError) as e:
        logging.error(f"ошибка при форматировании дат {e}")
        
        
    try:
        result_df[['Дата ликвидации', 'Актуально', 'Дата обнаружения']] = result_df[['Дата ликвидации', 'Актуально', 'Дата обнаружения']]\
            .apply(pd.to_datetime, format=date_format, dayfirst=True, errors='coerce')

        result_df[['Дата ликвидации', 'Актуально', 'Дата обнаружения']] = result_df[['Дата ликвидации', 'Актуально', 'Дата обнаружения']]\
            .apply(lambda x: x.dt.strftime('%d.%m %H:%M'))
    except (KeyError, IndexError, AttributeError) as e:
        logging.error(f"ошибка при форматировании дат {e}")
        
    return pd.DataFrame(result_df)