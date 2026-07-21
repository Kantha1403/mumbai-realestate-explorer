
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os
import pickle
import numpy as np

st.set_page_config(
    page_title="Mumbai Real Estate Explorer",
    layout="wide"
)

@st.cache_data(ttl=0)
def load_data():
    base = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(base, "mumbai_realestate_master.csv")
    df = pd.read_csv(csv_path)
    df_area = df.dropna(subset=["area_sqft"]).copy()
    df_area["price_per_sqft"] = (df_area["price"] / df_area["area_sqft"]).round(0)
    return df, df_area

@st.cache_resource
def load_model(_df):
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.preprocessing import LabelEncoder
    import numpy as np

    model_data = _df.dropna(subset=["bhk", "area_sqft", "locality", "city", "price"]).copy()
    p99 = model_data["price"].quantile(0.99)
    model_data = model_data[model_data["price"] <= p99]

    le_locality = LabelEncoder()
    le_city = LabelEncoder()
    model_data["locality_encoded"] = le_locality.fit_transform(model_data["locality"])
    model_data["city_encoded"]     = le_city.fit_transform(model_data["city"])

    X = model_data[["bhk", "area_sqft", "locality_encoded", "city_encoded"]]
    y = model_data["price"]

    model = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
    model.fit(X, y)

    return model, le_locality, le_city

df, df_area = load_data()
model, le_locality, le_city = load_model(df)

st.title("Mumbai & Navi Mumbai Real Estate Explorer")
st.caption("Data scraped from MagicBricks — 1,859 listings across Mumbai & Navi Mumbai")
st.markdown("---")

# ── Filters ───────────────────────────────────────────────
col1, col2, col3 = st.columns(3)

with col1:
    city_filter = st.selectbox("Select City", ["Both", "Mumbai", "Navi Mumbai"])

with col2:
    if city_filter == "Both":
        available_localities = sorted(df["locality"].unique())
    else:
        available_localities = sorted(df[df["city"] == city_filter]["locality"].unique())
    locality = st.selectbox("Select Locality", ["All"] + available_localities)

with col3:
    bhk_filter = st.multiselect("BHK Type", options=[1, 2, 3, 4, 5], default=[1, 2, 3])

col4, col5 = st.columns(2)

with col4:
    price_min = int(df["price"].min() / 100000)
    price_max = 1000
    price_range = st.slider(
        "Budget Range (Rs Lakhs)",
        min_value=price_min,
        max_value=price_max,
        value=(price_min, price_max),
        step=5
    )

with col5:
    possession_filter = st.selectbox(
        "Possession Status",
        ["All", "Ready to Move", "Under Construction"]
    )

# ── Apply filters ─────────────────────────────────────────
filtered = df.copy()
filtered_area = df_area.copy()

if city_filter != "Both":
    filtered = filtered[filtered["city"] == city_filter]
    filtered_area = filtered_area[filtered_area["city"] == city_filter]

if locality != "All":
    filtered = filtered[filtered["locality"] == locality]
    filtered_area = filtered_area[filtered_area["locality"] == locality]

if bhk_filter:
    filtered = filtered[filtered["bhk"].isin(bhk_filter)]
    filtered_area = filtered_area[filtered_area["bhk"].isin(bhk_filter)]

filtered = filtered[
    (filtered["price"] >= price_range[0] * 100000) &
    (filtered["price"] <= price_range[1] * 100000)
]
filtered_area = filtered_area[
    (filtered_area["price"] >= price_range[0] * 100000) &
    (filtered_area["price"] <= price_range[1] * 100000)
]

if possession_filter != "All":
    filtered = filtered[filtered["possession_status"] == possession_filter]
    filtered_area = filtered_area[filtered_area["possession_status"] == possession_filter]

st.markdown("---")

if len(filtered) == 0:
    st.warning("No listings found for selected filters.")
else:
    # ── KPIs ──────────────────────────────────────────────
    m1, m2, m3, m4, m5, m6 = st.columns(6)

    with m1:
        st.metric("Total Listings", len(filtered))
    with m2:
        st.metric("Median Price", f"Rs {filtered['price'].median()/100000:.0f}L")
    with m3:
        st.metric("Cheapest", f"Rs {filtered['price'].min()/100000:.0f}L")
    with m4:
        st.metric("Most Expensive", f"Rs {filtered['price'].max()/100000:.0f}L")
    with m5:
        if len(filtered_area) > 0:
            avg_ppsf = filtered_area["price_per_sqft"].mean()
            st.metric("Avg Price/Sqft", f"Rs {avg_ppsf:,.0f}")
        else:
            st.metric("Avg Price/Sqft", "N/A")
    with m6:
        most_common_bhk = int(filtered["bhk"].mode()[0])
        st.metric("Most Common BHK", f"{most_common_bhk} BHK")

    st.markdown("---")

    # ── Charts ────────────────────────────────────────────
    left, right = st.columns(2)

    with left:
        st.subheader("Price by BHK Type")
        bhk_prices = filtered.groupby("bhk")["price"].median() / 100000
        bhk_prices = bhk_prices.reset_index()
        bhk_prices.columns = ["BHK", "Median Price (Lakhs)"]

        fig1, ax1 = plt.subplots(figsize=(6, 4))
        ax1.bar(
            bhk_prices["BHK"].astype(str) + " BHK",
            bhk_prices["Median Price (Lakhs)"],
            color="steelblue"
        )
        ax1.set_ylabel("Median Price (Rs Lakhs)")
        ax1.set_title("Median Price by BHK")
        plt.tight_layout()
        st.pyplot(fig1)
        plt.close()

    with right:
        st.subheader("Price Distribution")
        price_data = filtered["price"] / 100000
        cap = price_range[1]
        capped = price_data[price_data <= cap]
        excluded = len(price_data) - len(capped)

        fig2, ax2 = plt.subplots(figsize=(6, 4))
        ax2.hist(capped, bins=30, color="steelblue", edgecolor="white")
        ax2.set_xlabel("Price (Rs Lakhs)")
        ax2.set_ylabel("Number of Listings")
        ax2.set_title("Price Distribution")
        if excluded > 0:
            ax2.text(0.98, 0.95, f"{excluded} listings above Rs {cap}L not shown",
                     transform=ax2.transAxes, ha="right", va="top",
                     fontsize=7, color="gray")
        plt.tight_layout()
        st.pyplot(fig2)
        plt.close()

    st.markdown("---")

    # ── Price per sqft table ──────────────────────────────
    st.subheader("Price per Sq Ft by Locality")

    if len(filtered_area) == 0:
        st.info("Area data not available for this selection.")
    else:
        ppsf = filtered_area.groupby("locality")["price_per_sqft"].agg(
            Listings="count",
            Avg_Rs_sqft="mean",
            Median_Rs_sqft="median"
        ).round(0).reset_index()
        ppsf = ppsf.sort_values("Median_Rs_sqft")
        ppsf.columns = ["Locality", "Listings", "Avg Rs/sqft", "Median Rs/sqft"]
        st.dataframe(ppsf, use_container_width=True, hide_index=True)

    st.markdown("---")

    # ── Nearby facilities ─────────────────────────────────
    if locality != "All":
        st.subheader("Nearby Facilities")
        f1, f2, f3 = st.columns(3)

        railway_col = "nearest_railway/metro_station" if "nearest_railway/metro_station" in filtered.columns else "nearest_railway"

        with f1:
            st.markdown("**Railway/Metro Stations**")
            stations = filtered[railway_col].dropna().unique()
            if len(stations) > 0:
                seen = set()
                for s in stations:
                    clean = s.split("|")[0].strip()
                    if clean not in seen:
                        st.write(f"- {clean}")
                        seen.add(clean)
                        if len(seen) == 3:
                            break
            else:
                st.write("No data available")

        with f2:
            st.markdown("**Hospitals**")
            hospitals = filtered["nearest_hospital"].dropna().unique()
            if len(hospitals) > 0:
                seen = set()
                for h in hospitals:
                    clean = h.split("|")[0].strip()
                    if clean not in seen:
                        st.write(f"- {clean}")
                        seen.add(clean)
                        if len(seen) == 3:
                            break
            else:
                st.write("No data available")

        with f3:
            st.markdown("**Supermarkets**")
            markets = filtered["nearest_market"].dropna().unique()
            if len(markets) > 0:
                seen = set()
                for m in markets:
                    clean = m.split("|")[0].strip()
                    if clean not in seen:
                        st.write(f"- {clean}")
                        seen.add(clean)
                        if len(seen) == 3:
                            break
            else:
                st.write("No data available")

        st.markdown("---")

    # ── Top developers ────────────────────────────────────
    st.subheader("Top Developers")
    top_devs = filtered["developer"].value_counts().head(8).reset_index()
    top_devs.columns = ["Developer", "Listings"]
    st.dataframe(top_devs, use_container_width=True, hide_index=True)

    st.markdown("---")

    # ── All listings ──────────────────────────────────────
    st.subheader("All Listings")
    railway_col = "nearest_railway/metro_station" if "nearest_railway/metro_station" in filtered.columns else "nearest_railway"
    display_cols = ["bhk", "price_fmt", "locality", "city",
                    "developer", "possession", "possession_status", railway_col]
    display_df = filtered[display_cols].copy()
    display_df[railway_col] = display_df[railway_col].str.split("|").str[0].str.strip()
    st.dataframe(
        display_df.rename(columns={
            "bhk"              : "BHK",
            "price_fmt"        : "Price",
            "locality"         : "Locality",
            "city"             : "City",
            "developer"        : "Developer",
            "possession"       : "Possession Date",
            "possession_status": "Status",
            railway_col        : "Nearest Station"
        }),
        use_container_width=True,
        hide_index=True
    )

st.markdown("---")

# ── Price Prediction ──────────────────────────────────────
st.subheader("Price Prediction")
st.caption("Estimate apartment price based on your requirements")

p1, p2, p3, p4 = st.columns(4)

with p1:
    pred_city = st.selectbox("City", ["Navi Mumbai", "Mumbai"], key="pred_city")

with p2:
    pred_localities = sorted(df[df["city"] == pred_city]["locality"].unique())
    pred_locality = st.selectbox("Locality", pred_localities, key="pred_locality")

with p3:
    pred_bhk = st.selectbox("BHK", [1, 2, 3, 4, 5], index=1, key="pred_bhk")

with p4:
    pred_area = st.number_input("Area (sq ft)", min_value=200, max_value=6000,
                                 value=900, step=50, key="pred_area")

if st.button("Predict Price"):
    try:
        loc_enc  = le_locality.transform([pred_locality])[0]
        city_enc = le_city.transform([pred_city])[0]

        input_df = pd.DataFrame([[pred_bhk, pred_area, loc_enc, city_enc]],
                                  columns=["bhk", "area_sqft",
                                           "locality_encoded", "city_encoded"])

        predicted_price = model.predict(input_df)[0]
        predicted_lakhs = predicted_price / 100000

        def format_price(lakhs):
            if lakhs >= 100:
                return f"Rs {lakhs/100:.2f} Cr"
            else:
                return f"Rs {lakhs:.1f} L"

        st.success(f"Model Estimate: {format_price(predicted_lakhs)}")

        # Show comparable listings
        comparable = df[
            (df["locality"] == pred_locality) &
            (df["bhk"] == pred_bhk)
        ]["price"].dropna()

        if len(comparable) > 0:
            st.caption(
                f"Actual market data — {len(comparable)} similar listings in {pred_locality}: "
                f"Median {format_price(comparable.median()/100000)}, "
                f"Range {format_price(comparable.min()/100000)} — {format_price(comparable.max()/100000)}"
            )
    except Exception as e:
        st.error(f"Could not predict: {str(e)}")
