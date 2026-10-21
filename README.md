# SpaceX launch analysis

Course project for IBM's Applied Data Science Capstone. It covers data collection, cleaning, SQL analysis, maps, an interactive dashboard and four classification models.

The IBM datasets are separate snapshots: 90 records for modeling, 101 for SQL, 56 for the dashboard and maps, and 121 numbered launches from the saved Wikipedia page. They are kept separate because their coverage differs. Input links and SHA-256 hashes are in `SOURCES.json`.

## Run the project

Install the packages, then download the source files:

```bash
python -m pip install -r requirements.txt
python download_inputs.py
```

Run each analysis separately:

```bash
python scripts/01_data_wrangling.py
python scripts/02_visual_analysis.py
python scripts/03_sql_analysis.py
python scripts/04_predictive_models.py
python scripts/05_web_scraping.py
python scripts/06_api_data.py
python scripts/07_launch_site_maps.py
```

The scripts write their outputs under `results/`. Start the dashboard with `python dashboard.py`, then open `http://127.0.0.1:8060`. `python export_dashboard_charts.py` saves the site pie chart, KSC pie chart and KSC payload chart from the dashboard's calculations. These are chart exports, not browser screenshots.

The API script uses IBM's saved JSON response by default. Its optional `--probe-live` flag makes one request with a ten-second timeout. Live enrichment is unfinished because the API returned HTTP 522 during this project.

## Notebooks

The seven [notebooks](notebooks/) cover the same steps as the scripts, with saved results and charts. After running `download_inputs.py`, open them in Jupyter from this project. Their data paths are relative to the repository. The API enrichment and the full visual review of the maps remain incomplete, as noted in the relevant notebooks.

## Results and limits

All four classifiers correctly classify 15 of the 18 test records in the IBM protocol. The decision tree has the highest mean cross-validation score in this run. However, the protocol scales the data before splitting it and includes the retrospective `ReusedCount` field. These scores therefore do not establish how well the models would predict future launches. The course's `Class` label includes ocean and unknown outcomes; it is not a direct measure of reusable booster recovery.

The maps show four launch sites and 56 records. The distance results in `geography/` use only the acquired OpenStreetMap and Census features. They do not establish the nearest motorway or city centre. See that folder's notes for the search area and limits.

The analysis scripts have been run locally. The full set of maps has not had a complete visual review. Source credit and map attribution are in `ATTRIBUTION.md`.
