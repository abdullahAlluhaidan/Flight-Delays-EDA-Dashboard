# Flight Delays — EDA and Streamlit Dashboard

**Presented by: Abdullah Alluhaidan**  
Final Project · Unit 3 · Individual Data Exploration & Dashboard Development

This is a combined project: it retains the original EDA notebook and the cleaned flight data, replaces the old basic dashboard with the newer interactive Streamlit dashboard, and includes the updated seven-slide presentation with dashboard screenshots.

## Run the dashboard

From the project folder:

```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Streamlit normally opens at http://localhost:8501. If you use Windows and `python` does not work, try `py` instead.

## Files

- `app.py` — **new** interactive dashboard from `flights_dashboard.zip`.
- `.streamlit/config.toml` — **new** dashboard theme.
- `data/flights_eda_cleaned.csv` — original cleaned, deduplicated data; unchanged (100,000 rows × 11 columns).
- `flights_eda_colab.ipynb` — EDA notebook; loading updated to use the included cleaned data, because the raw 32-column CSV was not supplied.
- `Flight_EDA_Presentation.pptx` — updated 7-slide PowerPoint, now credited to **Abdullah Alluhaidan**. Merges the old EDA flight outcomes/cleaning context with the newer interactive-dashboard presentation.
- `presentation_speaking_notes.md` — speaker notes for the PowerPoint.
- `assets/` — real EDA visuals and dashboard screenshots used in the slides.
- `requirements.txt` — merged dependencies for the notebook and dashboard.

## What's new in the dashboard

- Dataset description and **four sidebar filters**: airlines, year, distance and departure hour.
- **Five summary KPI cards**: selected flights, late arrivals, cancellations, mean and median arrival delay.
- Data preview, descriptive-statistics table, and missing-value summary.
- **Eight interactive charts**: flight status, arrival-delay histogram, airline comparison, delay by departure hour, monthly trend, five-airline box plot, departure-vs-arrival scatter and correlation heatmap.
- Dynamic insights about patterns, correlations and outliers.

## Notebook

For local Jupyter, open `flights_eda_colab.ipynb` from this folder; the notebook reads `data/flights_eda_cleaned.csv` and produces `flights_eda_cleaned_from_notebook.csv` without overwriting the original. In Google Colab, first upload `data/flights_eda_cleaned.csv` to Colab as `flights_eda_cleaned.csv`; the notebook searches the local directory as a fallback. Use **Run all**.

The included data is already cleaned. Because the original **32-column raw file is not supplied**, the notebook can validate and re-export the supplied 11-column sample but cannot reproduce the raw-file column removal or independently verify duplicate removal from the raw source.

## Data and methodological notes

- 100,000 U.S. domestic flight records from January 2019 to August 2023; 18 airlines.
- 97,164 completed; 2,649 cancelled; 187 diverted.
- A **late arrival** is one more than 15 minutes behind schedule, among completed flights.
- Cancelled/diverted flights have no valid arrival-delay result; blank values are **not** replaced with zero.
- The dataset's original download URL was not supplied; add a verified dataset source link if you have one.
- Findings describe a sample; association is not evidence of causation.

## Presentation

The deck follows the required 7-slide order and is designed for 5–7 minutes:
Title & Name → Dataset Overview → Problem Definition → EDA Results → Dashboard Demo → Final Insights → Conclusion.

The dashboard images are embedded in the presentation, so no live server is required for displaying the slides. For a live demonstration, open Streamlit and use its sidebar filters.

## Remaining submission steps

A full standalone PDF analysis report and a GitHub repository link were required by the course assignment but are **not** created or published by this merge. To submit the full assignment, prepare the report and upload the project yourself.
