from icecream import ic

async def response_maker(df):
    grouped_by_municipality = df
    response = ""
    for municipality, fires in grouped_by_municipality:
        response += f"\n\n\n<b>{municipality}</b>\n"
        status_counts = fires['icon_status'].value_counts()
        for status, count in status_counts.items():
            response += f"{count}{status}  "
        for idx, row in fires.iterrows():
            response += (f"\n\n{row['icon_status']} {row['Статус']} пожар №{row['Номер пожара']} "
                            f"{row['Лесничество']} лесничество "
                            f"на площади {row['Площадь пожара']} га. "
                            f"{row['Зона']} ")
            aps = row['АПС']
            lps = row['ЛПС']
            
            if aps and lps:
                response += (f"Работает {aps} АПС и {lps} ЛПС ") 
            elif aps:
                response += (f"Работает {aps} АПС ")
            elif lps:
                response += (f"Работает {lps} ЛПС ")
                
            response +=  (f" ({row['Зона']} {row['Расстояние']} км от {row['Город']}) ")
    return response