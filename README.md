# Flight Delays EDA & Dashboard

**Abdullah Alluhaidan**  
Final Project – Unit 3

## About the Project

For this project, I explored flight delay data to understand when flights are more likely to arrive late and how delays differ between airlines. I used Python for the exploratory data analysis (EDA) and Streamlit to present the results in an interactive dashboard.

The dataset contains 100,000 U.S. domestic flight records from 2019 to 2023, covering 18 airlines.

## Questions I Looked At

- How many flights arrive late or get cancelled?
- Do some airlines have higher delay rates than others?
- Does the time of day make a difference?
- How closely are departure and arrival delays related?

## Main Findings

- Most completed flights were not more than 15 minutes late.
- Late arrivals were more common for flights scheduled later in the day.
- Delay rates varied across airlines.
- Flights that departed late were also more likely to arrive late.

These findings describe patterns in this sample, not necessarily the causes of delays.

## Dashboard

The Streamlit dashboard lets you filter flights by airline, year, distance and departure time. It also shows flight statistics, interactive charts, a data preview and a summary of the results.

## How to Run It

Open a terminal in the project folder and run:

`python -m pip install -r requirements.txt`

`python -m streamlit run app.py`

Then open the local address shown in the terminal (usually `http://localhost:8501`).

## Project Files

- `app.py` – Streamlit dashboard
- `flights_eda_colab.ipynb` – EDA notebook
- `data/flights_eda_cleaned.csv` – Dataset used in the analysis and dashboard
- `assets/` – Charts and dashboard screenshots
- `Flight_EDA_Presentation.pptx` – Presentation slides
- `requirements.txt` – Python libraries needed to run the app

**Data note:** The repository includes the cleaned sample used in the dashboard, not the original raw dataset. Cancelled and diverted flights are excluded from calculations that require a valid arrival delay.
