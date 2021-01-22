![](https://www.politico.com/interactives/cdn/images/badge.svg)

# scraper_senate-lobbying-disclosures

Scripts to process quarterly [Lobbying Disclosure Act Reports](https://lda.senate.gov/system/public/) from the United States Senate.


## Requirements

-   Python 3.x — `brew install python`
-   Pipenv — `brew install pipenv`


## What's in here

-   [`.env.example`](.env.example): Sample configuration variables.
-   [`scrape_lda_filings.py`](scrape_lda_filings.py): The principal code of this repo, which pulls these disclosure reports and related files. **NOTE:** This needs to be refactored into numerous smaller files.
-   [`utils/`](utils): Utilities called in `scrape_lda_filings.py`.
-   [`reports`](reports): A folder to contain all downloaded quarters' reports.

## Getting started

#### First-time installation

1. Clone this repo and `cd` into it:

    ```sh
    $ git clone git@github.com:The-Politico/scraper_senate-lobbying-disclosures.git
    $ cd scraper_senate-lobbying-disclosures
    ```

2. Create a `.env` file with the following setting (see [.env.example](.env.example)):

    ```sh
    SENATE_LDA_API_KEY='token-goes-here'
    ```


3. Setup a Python 3 virtual environment, step into it and install dependencies:

   ```sh
    $ pipenv install --dev
    ```

#### Updating your local project

After pulling someone else's changes from Github you may need to run a couple of commands to sync your local database and virtual environment:

1. Use `pipenv sync` to make sure your local dependencies line up with the latest version of the requirements file (be sure you're in your virtual environment for this step):

    ```sh
    $ pipenv install --dev
    $ pipenv sync
    ```


## Configuration

The following configuration is automatically read from a `.env` file in the project's root.

Variable | What it does
-- | --
`SENATE_LDA_API_KEY` | **Required:** An API key from the Senate LDA site, used to request data from their systems. Sign up [at this link](https://lda.senate.gov/api/register/), or use the INT's existing key as listed in the password manager.


## Capturing a new quarterly report

For now, run the following code (replacing `2020` and `Q4` with your desired year and quarter):

```sh
  pipenv run python -c \
    'from scrape_lda_filings import scrape_lda_filings; filings = scrape_lda_filings("2020", "Q4")'
```


## Copyright

&copy; 2020&thinsp;&ndash;&thinsp;present POLITICO LLC.
