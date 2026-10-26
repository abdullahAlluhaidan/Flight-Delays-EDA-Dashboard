"""Flight Delay Dashboard - Final Project, Unit 3.

Run with:  streamlit run app.py
"""
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="Flight Delay Dashboard", page_icon="✈️", layout="wide")

# ---------------------------------------------------------------- constants
DATA_PATH = Path(__file__).parent / "data" / "flights_eda_cleaned.csv"
LATE_MINUTES = 15  # a flight is "late" if it arrives more than 15 min after schedule

# Validated categorical colours (fixed order) + one neutral for grid lines.
BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
STATUS_COLORS = {"Completed": BLUE, "Cancelled": ORANGE, "Diverted": AQUA}
GRID = "rgba(128,128,128,0.20)"

SHORT_NAMES = {
    "Southwest Airlines Co.": "Southwest",
    "Delta Air Lines Inc.": "Delta",
    "American Airlines Inc.": "American",
    "SkyWest Airlines Inc.": "SkyWest",
    "United Air Lines Inc.": "United",
    "Republic Airline": "Republic",
    "Envoy Air": "Envoy Air",
    "Endeavor Air Inc.": "Endeavor Air",
    "JetBlue Airways": "JetBlue",
    "PSA Airlines Inc.": "PSA",
    "Alaska Airlines Inc.": "Alaska",
    "Spirit Air Lines": "Spirit",
    "Mesa Airlines Inc.": "Mesa",
    "Frontier Airlines Inc.": "Frontier",
    "Allegiant Air": "Allegiant",
    "Hawaiian Airlines Inc.": "Hawaiian",
    "Horizon Air": "Horizon Air",
    "ExpressJet Airlines LLC d/b/a aha!": "ExpressJet",
}


# -------------------------------------------------------------------- data
@st.cache_data
def load_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH, parse_dates=["FL_DATE"])
    df["Airline"] = df["AIRLINE"].map(SHORT_NAMES).fillna(df["AIRLINE"])
    df["Year"] = df["FL_DATE"].dt.year
    df["Month"] = df["FL_DATE"].dt.to_period("M").dt.to_timestamp()
    df["Dep Hour"] = (df["CRS_DEP_TIME"] // 100).replace(24, 0)
    df["Late"] = df["ARR_DELAY"] > LATE_MINUTES  # missing delay -> False
    return df


df = load_data()
all_airlines = sorted(df["Airline"].unique())
years = sorted(df["Year"].unique().tolist())
dist_min = int(df["DISTANCE"].min() // 10 * 10)
dist_max = int(-(-df["DISTANCE"].max() // 10) * 10)

# ----------------------------------------------------------------- sidebar
st.sidebar.title("✈️ Flight Delays")

st.sidebar.header("About the dataset")
st.sidebar.markdown(
    f"""
A sample of **{len(df):,} U.S. domestic flights** from
**{df['FL_DATE'].min():%b %Y}** to **{df['FL_DATE'].max():%b %Y}**,
covering **{df['Airline'].nunique()} airlines**.

Each row is one scheduled flight: date, airline, scheduled departure time,
distance, taxi times, departure/arrival delay (minutes) and whether it was
cancelled or diverted.

- **Late** = arrived more than **{LATE_MINUTES} min** after schedule.
- Cancelled and diverted flights have **no arrival delay**, so they are
  left out of delay statistics.
"""
)

st.sidebar.header("Filters")
selected_airlines = st.sidebar.multiselect("Airlines", all_airlines, default=all_airlines)
selected_year = st.sidebar.selectbox("Year", ["All years"] + years)
dist_range = st.sidebar.slider(
    "Flight distance (miles)", dist_min, dist_max, (dist_min, dist_max), step=10
)
hour_range = st.sidebar.slider("Scheduled departure hour (0-23)", 0, 23, (0, 23))

mask = (
    df["Airline"].isin(selected_airlines)
    & df["DISTANCE"].between(*dist_range)
    & df["Dep Hour"].between(*hour_range)
)
if selected_year != "All years":
    mask &= df["Year"] == selected_year
flt = df[mask]

st.sidebar.caption(f"{len(flt):,} of {len(df):,} flights match the filters.")

# ------------------------------------------------------------------- title
st.title("Flight Delay Dashboard")
st.caption(
    "Explore how often flights are late or cancelled, and which airlines, hours and "
    "months are most affected. Use the sidebar filters to change every number and chart."
)

if flt.empty or flt["Flight Status"].eq("Completed").sum() < 30:
    st.warning("Too few flights match these filters. Widen the filters in the sidebar.")
    st.stop()

comp = flt[flt["Flight Status"] == "Completed"]

# ------------------------------------------------------------------ helpers
def style(fig: go.Figure, height: int = 340, legend: bool = False) -> go.Figure:
    fig.update_layout(
        height=height,
        margin=dict(l=8, r=8, t=8, b=8),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(size=13),
        showlegend=legend,
        legend=dict(orientation="h", yanchor="bottom", y=1.0, xanchor="left", x=0),
        hoverlabel=dict(font_size=13),
    )
    fig.update_xaxes(showgrid=False, zeroline=False)
    fig.update_yaxes(gridcolor=GRID, zeroline=False)
    return fig


def delta_vs_all(value: float, baseline: float, unit: str = "pts"):
    diff = value - baseline
    return None if abs(diff) < 0.05 else f"{diff:+.1f} {unit} vs all flights"


# --------------------------------------------------------------------- KPIs
base_comp = df[df["Flight Status"] == "Completed"]
late_pct = comp["Late"].mean() * 100
base_late_pct = base_comp["Late"].mean() * 100
cancel_pct = (flt["CANCELLED"] == 1).mean() * 100
base_cancel_pct = (df["CANCELLED"] == 1).mean() * 100

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Flights in selection", f"{len(flt):,}")
k2.metric(
    "Late arrivals (> 15 min)",
    f"{late_pct:.1f}%",
    delta_vs_all(late_pct, base_late_pct),
    delta_color="inverse",
    help="Share of completed flights that arrived more than 15 minutes late.",
)
k3.metric(
    "Cancelled",
    f"{cancel_pct:.2f}%",
    delta_vs_all(cancel_pct, base_cancel_pct),
    delta_color="inverse",
)
k4.metric("Median arrival delay", f"{comp['ARR_DELAY'].median():.0f} min",
          help="Negative = arrived early. The median is not pulled up by extreme delays.")
k5.metric("Mean arrival delay", f"{comp['ARR_DELAY'].mean():.1f} min",
          help="The mean is pulled up by a small number of very long delays.")

# -------------------------------------------------- data preview + statistics
st.header("Data preview & summary statistics")
tab_preview, tab_stats, tab_missing = st.tabs(["Data preview", "Summary statistics", "Missing values"])

with tab_preview:
    preview = flt[["FL_DATE", "AIRLINE", "CRS_DEP_TIME", "DEP_DELAY", "TAXI_OUT", "TAXI_IN",
                   "ARR_DELAY", "CANCELLED", "DIVERTED", "DISTANCE", "Flight Status"]].head(10).copy()
    preview["FL_DATE"] = preview["FL_DATE"].dt.strftime("%Y-%m-%d")
    st.dataframe(preview, hide_index=True, width="stretch")
    st.caption(f"First 10 of {len(flt):,} rows in the selection (full cleaned file: "
               f"{df.shape[0]:,} rows x 11 columns).")

with tab_stats:
    num_cols = ["DEP_DELAY", "TAXI_OUT", "TAXI_IN", "ARR_DELAY", "DISTANCE"]
    stats = flt[num_cols].describe().T.round(2)
    stats["count"] = stats["count"].astype(int)
    st.dataframe(stats, width="stretch")
    st.caption("Delays and taxi times are in minutes; distance is in miles.")

with tab_missing:
    miss = flt.isnull().sum()
    miss = miss[miss > 0].to_frame("Missing values")
    miss["Share of rows (%)"] = (miss["Missing values"] / len(flt) * 100).round(2)
    st.dataframe(miss, width="stretch")
    st.caption("Missing delays belong to cancelled or diverted flights. "
               "They are kept blank, not filled with zero.")

# ---------------------------------------------------------- visualizations
st.header("Interactive visualizations")

# ---- row 1: status + delay distribution
c1, c2 = st.columns(2)

with c1:
    st.subheader("Flight status")
    counts = flt["Flight Status"].value_counts().reindex(["Completed", "Cancelled", "Diverted"]).fillna(0)
    fig = go.Figure(go.Bar(
        y=counts.index[::-1], x=counts.values[::-1], orientation="h",
        marker_color=[STATUS_COLORS[s] for s in counts.index[::-1]],
        text=[f"{n:,.0f} ({n / counts.sum() * 100:.1f}%)" for n in counts.values[::-1]],
        textposition="outside", cliponaxis=False,
        hovertemplate="%{y}: %{x:,} flights<extra></extra>",
    ))
    fig.update_xaxes(range=[0, counts.max() * 1.35], showticklabels=False)
    fig.update_yaxes(showgrid=False)
    st.plotly_chart(style(fig), key="status")
    st.caption("Almost every flight was completed; cancellations and diversions are rare.")

with c2:
    st.subheader("Arrival delay distribution")
    vals = comp["ARR_DELAY"].dropna().clip(-59, 180)
    edges = np.arange(-59.5, 181, 5)  # edge at 15.5 splits "<= 15" from "> 15" min
    hist, _ = np.histogram(vals, bins=edges)
    left = edges[:-1]
    centers = left + 2.5
    labels = [f"{int(lo + 0.5)} to {int(lo + 4.5)} min" for lo in left]
    on_time = left < LATE_MINUTES
    fig = go.Figure()
    fig.add_bar(x=centers[on_time], y=hist[on_time], name="15 min late or less (or early)",
                marker_color=BLUE, customdata=np.array(labels)[on_time],
                hovertemplate="%{customdata}: %{y:,} flights<extra></extra>")
    fig.add_bar(x=centers[~on_time], y=hist[~on_time], name="More than 15 min late",
                marker_color=ORANGE, customdata=np.array(labels)[~on_time],
                hovertemplate="%{customdata}: %{y:,} flights<extra></extra>")
    fig.add_vline(x=comp["ARR_DELAY"].median(), line_dash="dot", line_width=1.5, line_color="gray",
                  annotation_text=f"median {comp['ARR_DELAY'].median():.0f} min",
                  annotation_position="top right")
    fig.update_layout(barmode="overlay", bargap=0.06)
    fig.update_xaxes(title="Arrival delay (minutes)")
    fig.update_yaxes(title="Flights")
    st.plotly_chart(style(fig, legend=True), key="hist")
    st.caption("Most flights land early. A long right tail of big delays pulls the mean above the median. "
               "Delays beyond 180 min are grouped in the last bar.")

# ---- row 2: airlines + departure hour
c3, c4 = st.columns(2)

with c3:
    st.subheader("Airline comparison")
    metric = st.selectbox(
        "Measure",
        ["Late arrivals (% > 15 min)", "Mean arrival delay (min)",
         "Median arrival delay (min)", "Cancellation rate (%)"],
        label_visibility="collapsed",
    )
    if metric.startswith("Cancellation"):
        grp = flt.groupby("Airline")["CANCELLED"].agg(["mean", "size"])
        grp["value"] = grp["mean"] * 100
    elif metric.startswith("Late"):
        grp = comp.groupby("Airline")["Late"].agg(["mean", "size"])
        grp["value"] = grp["mean"] * 100
    elif metric.startswith("Mean"):
        grp = comp.groupby("Airline")["ARR_DELAY"].agg(["mean", "size"])
        grp["value"] = grp["mean"]
    else:
        grp = comp.groupby("Airline")["ARR_DELAY"].agg(["median", "size"])
        grp["value"] = grp["median"]
    grp = grp[grp["size"] >= 30].sort_values("value")
    if grp.empty:
        st.info("Not enough flights per airline to compare. Widen the sidebar filters.")
    else:
        fig = go.Figure(go.Bar(
            y=grp.index, x=grp["value"], orientation="h", marker_color=BLUE,
            text=[f"{v:.1f}" for v in grp["value"]], textposition="outside", cliponaxis=False,
            customdata=grp["size"],
            hovertemplate="%{y}: %{x:.1f}<br>%{customdata:,} flights<extra></extra>",
        ))
        lo = min(0, grp["value"].min() * 1.3)
        fig.update_xaxes(range=[lo, grp["value"].max() * 1.18], title=metric)
        fig.update_yaxes(showgrid=False, dtick=1)
        st.plotly_chart(style(fig, height=470), key="airline")
        st.caption("Airlines with fewer than 30 flights in the selection are hidden.")

with c4:
    st.subheader("Late arrivals by departure hour")
    by_hour = comp.groupby("Dep Hour")["Late"].agg(["mean", "size"])
    by_hour = by_hour[by_hour["size"] >= 100]
    fig = go.Figure(go.Bar(
        x=by_hour.index, y=by_hour["mean"] * 100, marker_color=BLUE,
        customdata=by_hour["size"],
        hovertemplate="Departures scheduled %{x}:00-%{x}:59<br>%{y:.1f}% late "
                      "(%{customdata:,} flights)<extra></extra>",
    ))
    fig.add_hline(y=late_pct, line_dash="dot", line_width=1.5, line_color="gray")
    fig.update_xaxes(title="Scheduled departure hour (24h clock)", dtick=1)
    fig.update_yaxes(title="Late arrivals (%)", rangemode="tozero")
    st.plotly_chart(style(fig, height=470), key="hour")
    st.caption(f"Delays build up through the day. Dotted line = average ({late_pct:.1f}%). "
               "Hours with fewer than 100 flights are hidden.")

# ---- row 3: monthly trend + boxplot
c5, c6 = st.columns(2)

with c5:
    st.subheader("Late arrivals by month")
    by_month = comp.groupby("Month")["Late"].agg(["mean", "size"])
    by_month = by_month[by_month["size"] >= 30]
    fig = go.Figure(go.Scatter(
        x=by_month.index, y=by_month["mean"] * 100, mode="lines", line=dict(color=BLUE, width=2),
        customdata=by_month["size"],
        hovertemplate="%{x|%b %Y}: %{y:.1f}% late (%{customdata:,} flights)<extra></extra>",
    ))
    fig.update_yaxes(title="Late arrivals (%)", rangemode="tozero")
    fig.update_xaxes(title=None)
    st.plotly_chart(style(fig), key="month")
    st.caption("The selected sample shows a dip around spring 2020 and generally rising late rates afterward. "
               "It does not represent nationwide flight counts.")

with c6:
    st.subheader("Arrival delay spread - 5 busiest airlines")
    top5 = comp["Airline"].value_counts().head(5).index
    rows = []
    for name in top5:
        v = comp.loc[comp["Airline"] == name, "ARR_DELAY"].dropna()
        q1, med, q3 = v.quantile([0.25, 0.5, 0.75])
        iqr = q3 - q1
        rows.append(dict(name=name, q1=q1, med=med, q3=q3,
                         lo=v[v >= q1 - 1.5 * iqr].min(), hi=v[v <= q3 + 1.5 * iqr].max()))
    bx = pd.DataFrame(rows)
    fig = go.Figure(go.Box(
        x=bx["name"], q1=bx["q1"], median=bx["med"], q3=bx["q3"],
        lowerfence=bx["lo"], upperfence=bx["hi"],
        marker_color=BLUE, line=dict(color=BLUE, width=2), fillcolor="rgba(42,120,214,0.25)",
    ))
    fig.add_hline(y=0, line_width=1, line_color="gray")
    fig.update_yaxes(title="Arrival delay (minutes)")
    st.plotly_chart(style(fig), key="box")
    st.caption("Box = middle 50% of flights, line = median, whiskers = 1.5 x IQR. "
               "Outliers are hidden here.")

# ---- row 4: scatter + heatmap
c7, c8 = st.columns(2)

with c7:
    st.subheader("Departure delay vs arrival delay")
    pair = comp[["DEP_DELAY", "ARR_DELAY", "Airline"]].dropna()
    sample = pair.sample(n=min(3000, len(pair)), random_state=42)
    slope, intercept = np.polyfit(pair["DEP_DELAY"], pair["ARR_DELAY"], 1)
    xs = np.array([-30, 180])
    fig = go.Figure()
    fig.add_scatter(x=sample["DEP_DELAY"], y=sample["ARR_DELAY"], mode="markers",
                    name="Flights (random sample of 3,000)",
                    marker=dict(color=BLUE, size=6, opacity=0.35),
                    customdata=sample["Airline"],
                    hovertemplate="%{customdata}<br>Departure %{x} min, arrival %{y} min<extra></extra>")
    fig.add_scatter(x=xs, y=slope * xs + intercept, mode="lines", name="Best-fit line",
                    line=dict(color=ORANGE, width=2), hoverinfo="skip")
    fig.update_xaxes(title="Departure delay (minutes)", range=[-30, 180])
    fig.update_yaxes(title="Arrival delay (minutes)", range=[-60, 200])
    st.plotly_chart(style(fig, legend=True), key="scatter")
    st.caption("Flights that leave late arrive late. Axes are zoomed to the main cloud of points.")

with c8:
    st.subheader("Correlation heatmap")
    cols = ["DEP_DELAY", "TAXI_OUT", "TAXI_IN", "ARR_DELAY", "DISTANCE"]
    names = ["Departure delay", "Taxi out", "Taxi in", "Arrival delay", "Distance"]
    corr = comp[cols].corr().round(2)
    fig = go.Figure(go.Heatmap(
        z=corr.values, x=names, y=names, zmin=-1, zmax=1,
        colorscale=[[0, "#e34948"], [0.5, "#f0efec"], [1, "#2a78d6"]],
        text=corr.values, texttemplate="%{text:.2f}",
        colorbar=dict(thickness=12, title=dict(text="r")),
        hovertemplate="%{y} vs %{x}: %{z:.2f}<extra></extra>",
    ))
    fig.update_yaxes(autorange="reversed", showgrid=False)
    fig.update_xaxes(showgrid=False)
    st.plotly_chart(style(fig), key="heat")
    st.caption("Blue = move together, red = move in opposite directions, grey = no linear link.")

# ------------------------------------------------------------------ insights
st.header("Insights")
st.caption("The first three boxes recalculate from your filters. The last box describes the full dataset.")

i1, i2, i3 = st.columns(3)

with i1:
    with st.container(border=True):
        st.markdown("#### Patterns")
        al = comp.groupby("Airline")["Late"].agg(["mean", "size"])
        al = al[al["size"] >= 200]
        hr = comp.groupby("Dep Hour")["Late"].agg(["mean", "size"])
        hr = hr[hr["size"] >= 200]
        mo = comp.groupby(comp["FL_DATE"].dt.month_name())["Late"].agg(["mean", "size"])
        mo = mo[mo["size"] >= 200]
        lines = []
        if len(al) >= 2:
            lines.append(f"- **{al['mean'].idxmax()}** has the highest late rate "
                         f"({al['mean'].max() * 100:.1f}%); **{al['mean'].idxmin()}** the lowest "
                         f"({al['mean'].min() * 100:.1f}%).")
        if len(hr) >= 2:
            lines.append(f"- Late rate is highest for flights scheduled around **{hr['mean'].idxmax()}:00** "
                         f"({hr['mean'].max() * 100:.1f}%) and lowest around "
                         f"**{hr['mean'].idxmin()}:00** ({hr['mean'].min() * 100:.1f}%).")
        if len(mo) >= 2:
            lines.append(f"- **{mo['mean'].idxmax()}** is the worst month "
                         f"({mo['mean'].max() * 100:.1f}% late) and **{mo['mean'].idxmin()}** the best "
                         f"({mo['mean'].min() * 100:.1f}%).")
        st.markdown("\n".join(lines) or "Widen the filters to see patterns.")

with i2:
    with st.container(border=True):
        st.markdown("#### Relationships")
        r_dep = comp["DEP_DELAY"].corr(comp["ARR_DELAY"])
        r_dist = comp["DISTANCE"].corr(comp["ARR_DELAY"])
        r_taxi = comp["TAXI_OUT"].corr(comp["ARR_DELAY"])
        late_dep = comp[comp["DEP_DELAY"] > LATE_MINUTES]
        late_dep_share = f"{late_dep['Late'].mean() * 100:.0f}%" if len(late_dep) else "N/A"
        st.markdown(
            f"- Departure delay and arrival delay move almost together (**r = {r_dep:.2f}**).\n"
            f"- Of flights that left more than 15 min late, "
            f"**{late_dep_share}** also arrived late.\n"
            f"- Distance has almost no link to arrival delay (**r = {r_dist:.2f}**); "
            f"taxi-out time has a weak one (**r = {r_taxi:.2f}**)."
        )

with i3:
    with st.container(border=True):
        st.markdown("#### Outliers")
        long = comp[comp["ARR_DELAY"] > 180]
        st.markdown(
            f"- **{len(long):,}** completed flights ({len(long) / len(comp) * 100:.1f}%) arrived "
            f"more than 3 hours late; the longest delay is **{comp['ARR_DELAY'].max():,.0f} min**.\n"
            f"- Mean delay is **{comp['ARR_DELAY'].mean():.1f} min** but the median is "
            f"**{comp['ARR_DELAY'].median():.0f} min**: a few extreme delays pull the mean up.\n"
            f"- Extreme values were kept because they may be real flights."
        )

with st.container(border=True):
    st.markdown("#### Key takeaways (full dataset)")
    st.markdown(
        "- **17.6%** of completed flights arrived more than 15 minutes late, yet the typical flight "
        "landed **7 minutes early**.\n"
        "- **Delays build through the day:** 7.6% late for 5 am departures vs about 25% for 8-9 pm departures.\n"
        "- **Airlines differ a lot:** JetBlue, Frontier and Allegiant are late about 25-26% of the time; "
        "Delta and Endeavor Air about 12-13%.\n"
        "- **2020 was unusual:** the fewest late arrivals (9.2%) but the most cancellations (5.9%). "
        "Late arrivals then rose every year to 22.5% in 2023.\n"
        "- **Limits:** this is a 100,000-flight sample, and correlations here do not prove cause and effect."
    )

st.caption("Final Project - Unit 3 | Abdullah Alluhaidan | Data: cleaned flight sample (see README) | Built with Streamlit and Plotly")
