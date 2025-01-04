from curl_cffi import requests
from loguru import logger
from itertools import product
import json
import pandas as pd
import os
import time


def get_data(url, querystring, headers):
    time.sleep(2)
    response = requests.request(
        "GET", url, headers=headers, params=querystring, impersonate="chrome"
    )

    if response.status_code == 200:
        data = json.loads(response.text)["Results"]
        return data

    else:
        logger.warning(f"Failed Requests - {response.status_code}")
        return None


if __name__ == "__main__":

    url = "https://www.idx.co.id/primary/ListedCompany/GetFinancialReport"
    years = [2021, 2022, 2023, 2024, 2025]
    report_type = ["rdf", "rda"]
    emiten_type = ["s", "o"]
    periode = ["TW1", "TW2", "TW3", "audit"]

    headers = {
        "referer": "https://www.idx.co.id/id/perusahaan-tercatat/laporan-keuangan-dan-tahunan",  # important header for idx website
    }

    combinations = product(years, report_type, emiten_type, periode)

    for comb in combinations:
        logger.info(f"Start {comb}")
        querystring = {
            "indexFrom": "1",
            "pageSize": "10000",
            "year": comb[0],
            "reportType": comb[1],
            "EmitenType": comb[2],
            "periode": comb[3],
            "kodeEmiten": "",
            "SortColumn": "KodeEmiten",
            "SortOrder": "asc",
        }

        json_data: list[dict] = get_data(url, querystring, headers)
        all_data = []
        for company in json_data:
            result = {}
            result["kode_emiten"] = company.get("KodeEmiten", None)
            result["company_name"] = company.get("NamaEmiten", None)
            result["modify_date"] = company.get("File_Modified", None)
            result["period"] = company.get("Report_Period", None)
            result["year"] = company.get("Report_Year", None)

            attachments: list[dict] = company.get("Attachments", [])
            files = {}
            for file in attachments:
                desc = file.get("File_Name", None)
                path = file.get("File_Path", None)
                files[desc] = path

            result["attachments"] = files

            all_data.append(result)

        df = pd.DataFrame(all_data)
        head = not os.path.exists("data.csv")
        df.to_csv("data.csv", mode="a", header=head, index=False)
