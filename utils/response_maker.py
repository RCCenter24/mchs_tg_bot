

async def response_maker(df):
    grouped_by_municipality = df
    response = ""
    for municipality, fires in grouped_by_municipality:
        response += f"\n<b>{municipality}</b>\n"
        response += "<blockquote>"
        for idx, row in fires.iterrows():
            response += (
                f"{row['icon_status']} {row['fire_status']} пожар №{row['fire_num']} "
                f"{row['forestry_name']} лесничество "
                f"на площади {row['fire_area']} га. "
                f"{row['fire_zone']} "
            )
            aps = row["forces_aps"]
            lps = row["forces_lps"]

            if aps and lps:
                response += f"Работает {aps} АПС и {lps} ЛПС "
            elif aps:
                response += f"Работает {aps} АПС "
            elif lps:
                response += f"Работает {lps} ЛПС "

            response += f" ({row['fire_zone']} {row['distance']} км от {row['city']})\n"
        response += "</blockquote>"
        response += "\n"

    return response
