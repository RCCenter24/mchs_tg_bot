import logging
from xlsx2csv import Xlsx2csv


async def df_converter(latest_file_path):
    conveted_name = latest_file_path.split('.')[0]
    try:
        Xlsx2csv(latest_file_path,
                outputencoding="utf-8").convert(f"{conveted_name}.csv")
        return conveted_name
    except Exception as e:
        logging.error(f'Ошибка в конвертировании check_news', str(e))