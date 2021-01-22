# Imports from python.
from csv import DictWriter
from datetime import datetime
import json
from math import ceil
import os
from time import sleep


# Imports from other dependencies.
import requests


# Imports from this library.
from utils.qs_to_dict import querystring_to_dict
from utils.url_parsing import parse_safe_query_dict


BASE_SESSION = requests.Session()

BASE_API_URL = "https://lda.senate.gov/api/v1"

LDA_API_ENDPOINTS = dict(
    filing_types=f"{BASE_API_URL}/constants/filing/filingtypes/",
    filings=f"{BASE_API_URL}/filings/",
)

RESULTS_PER_PAGE = 250

TIME_PERIOD_SLUGS = dict(
    Q1="first_quarter",
    Q2="second_quarter",
    Q3="third_quarter",
    Q4="forth_quarter",
    MY="mid_year",
    YE="year_end",
)

TIME_PERIOD_PREFIXES = dict(
    Q1="1st Quarter",
    Q2="2nd Quarter",
    Q3="3rd Quarter",
    Q4="4th Quarter",
    MY="Mid-Year",
    YE="Year-End",
)


def get_types_for_quarter(time_period, common_session=None):
    session = BASE_SESSION if common_session is None else common_session

    rq = requests.Request(
        "GET",
        LDA_API_ENDPOINTS["filing_types"],
        headers={
            "Accept-Encoding": "gzip,deflate,br",
            "Accept": "application/json",
            "Authorization": f'Token {os.getenv("SENATE_LDA_API_KEY")}',
        },
    ).prepare()

    request_result = session.send(rq)

    if 200 <= request_result.status_code <= 299:
        all_types = json.loads(request_result.text)

        return [
            type_dict
            for type_dict in all_types
            if type_dict["name"].startswith(TIME_PERIOD_PREFIXES[time_period])
        ]

    return []


def get_filings_page(time_config, common_session=None, extra_fetch_params={}):
    session = BASE_SESSION if common_session is None else common_session

    query_dict = dict(
        **time_config,
        # ordering="-dt_posted,id",
        ordering="dt_posted,id",
        page_size=RESULTS_PER_PAGE,
        **extra_fetch_params,
    )

    rq = requests.Request(
        "GET",
        f"{LDA_API_ENDPOINTS['filings']}?{parse_safe_query_dict(query_dict)}",
        headers={
            "Accept-Encoding": "gzip,deflate,br",
            "Accept": "application/json",
            "Authorization": f'Token {os.getenv("SENATE_LDA_API_KEY")}',
        },
    ).prepare()

    request_result = session.send(rq)

    if 200 <= request_result.status_code <= 299:
        return dict(
            range=200,
            status=request_result.status_code,
            headers=request_result.headers,
            body=json.loads(request_result.text),
        )
    elif 400 <= request_result.status_code <= 499:
        return dict(
            range=400,
            status=request_result.status_code,
            headers=request_result.headers,
            body=None,
        )

    return dict(
        status=request_result.status_code,
        headers=request_result.headers,
        body=None,
    )


def process_result(raw_result, type_dict):
    posting_date = datetime.fromisoformat(raw_result["dt_posted"])

    return dict(
        UUID=raw_result["filing_uuid"],
        RegistrantName=raw_result["registrant"]["name"],
        ClientName=raw_result["client"]["name"],
        FilingType=type_dict[raw_result["filing_type"]].replace(" - ", " "),
        AmountReported=raw_result["income"],
        DatePosted=posting_date.strftime("%Y-%m-%d"),
        FilingYear=raw_result["filing_year"],
    )


def collect_filings(time_config, type_dict, session):
    current_page = get_filings_page(time_config, session)

    results_count = current_page["body"]["count"]
    results_lang = "filings" if results_count != 1 else "filing"

    page_count = ceil(results_count / RESULTS_PER_PAGE)
    page_lang = "pages" if page_count != 1 else "page"

    print(f"  ### {results_count} {results_lang} / {page_count} {page_lang}")

    all_filings = [
        process_result(result, type_dict)
        for result in current_page["body"]["results"]
    ]

    print("  - PAGE 1")

    while current_page["body"]["next"] is not None:
        next_query_dict = querystring_to_dict(current_page["body"]["next"])

        next_query_diff = {
            k: v
            for k, v in next_query_dict.items()
            if k not in [*time_config.keys(), "ordering", "page_size"]
        }

        sleep(1)

        current_page = get_filings_page(time_config, session, next_query_diff)

        print(f"  - PAGE {next_query_diff['page']}")

        all_filings.extend(
            [
                process_result(result, type_dict)
                for result in current_page["body"]["results"]
            ]
        )

    return all_filings


def scrape_lda_filings(year, time_period, common_session=None):
    session = BASE_SESSION if common_session is None else common_session

    types_for_period = get_types_for_quarter(time_period, session)

    type_dict = {
        filing_type["value"]: filing_type["name"]
        for filing_type in types_for_period
    }

    all_filings = {}

    for filing_type in types_for_period:
        print("")

        print(f"{filing_type['name']} ({filing_type['value']}):")

        time_config = dict(
            filing_year=year,
            filing_period=TIME_PERIOD_SLUGS[time_period],
            filing_type=filing_type["value"],
        )

        all_filings[filing_type["value"]] = collect_filings(
            time_config, type_dict, session,
        )

        print("")

    with open(f"reports/{year}-{time_period.lower()}.csv", "w") as output_file:
        writer = DictWriter(
            output_file,
            fieldnames=[
                "UUID",
                "RegistrantName",
                "ClientName",
                "FilingType",
                "AmountReported",
                "DatePosted",
                "FilingYear",
            ],
        )
        writer.writeheader()

        for type_slug, filings_for_type in all_filings.items():
            for filing in filings_for_type:
                writer.writerow(filing)

    return all_filings
