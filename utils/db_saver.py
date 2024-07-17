import logging
import pandas as pd
from xlsx2csv import Xlsx2csv
from icecream import ic
from io import BytesIO, StringIO
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import Fires



async def save_to_db(file_bytes, email_id, session: AsyncSession):
    bytes_io = BytesIO(file_bytes)
    csv_io = StringIO()
    Xlsx2csv(bytes_io, outputencoding="utf-8").convert(csv_io)
    csv_io.seek(0)
    try:
        df_chunks = pd.read_csv(csv_io, chunksize=10)

        for chunk in df_chunks:
            chunk['Дата обнаружения'] = chunk['Дата обнаружения'].apply(
                lambda x: pd.to_datetime(x, format='mixed', errors='coerce'))
            chunk['Дата ликвидации'] = chunk['Дата ликвидации'].apply(
                lambda x: pd.to_datetime(x, format='mixed', errors='coerce'))
            chunk['Актульно'] = chunk['Актульно'].apply(
                lambda x: pd.to_datetime(x, format='mixed', errors='coerce'))
            
            chunk['Дата ликвидации'] = chunk['Дата ликвидации'].apply(
                lambda x: None if pd.isnull(x) else x)
            chunk['email_id'] = email_id
            to_db_data = [
                {
                    "fire_ext_id": row['ID'],
                    "ext_log": row['log'],
                    "fire_num": row['Номер пожара'],
                    "date_detect": row['Дата обнаружения'],
                    "fire_zone": row['Зона'],
                    "map_id": row['ID Карты'],
                    "region": row['Район'],
                    "forestry_id": row['ID лесничества'],
                    "forestry_name": row['Лесничество'],
                    "city": row['Город'],
                    "azimuth": row['Азимут'],
                    "distance": row['Расстояние'],
                    "fire_status": row['Статус'],
                    "fire_area": row['Площадь пожара'],
                    "forces_aps": row['АПС'],
                    "forces_lps": row['ЛПС'],
                    "forces_": row['Привл'],
                    "forces_rent": row['Аренд'],
                    "forces_mchs": row['МЧС'],
                    "date_terminate": row['Дата ликвидации'],
                    "date_actual": row['Актульно'],
                    "email_id": email_id
                }
                for _, row in chunk.iterrows()
            ]
            add_db_query = insert(Fires).values(
                to_db_data).on_conflict_do_nothing()
            await session.execute(add_db_query)
            await session.commit()
    except Exception as e:
        logging.error(f"Error reading CSV data: {e}")
