import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os

st.set_page_config(
    page_title="Mumbai Real Estate Explorer",
    layout="wide"
)

@st.cache_data(ttl=0)
def load_data():
    csv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mumbai_realestate_master.csv")
    df = pd.read_csv(csv_path)
    df_area = df.dropna(subset=["area_sqft"]).copy()
    df_area["price_per_sqft"] = (df_area["price"] / df_area["area_sqft"]).round(0)
    return df, df_area

df, df_area = load_data()

st.title("Mumbai & Navi Mumbai Real Estate Explorer")
st.caption("Data scraped from MagicBricks — 1,859 listings across Mumbai & Navi Mumbai")
st.markdown("---")

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

st.markdown("---")

if len(filtered) == 0:
    st.warning("No listings found for selected filters.")
else:
    m1, m2, m3, m4 = st.columns(4)

    with m1:
        st.metric("Total Listings", len(filtered))
    with m2:
        st.metric("Median Price", f"Rs {filtered['price'].median()/100000:.0f}L")
    with m3:
        st.metric("Cheapest", f"Rs {filtered['price'].min()/100000:.0f}L")
    with m4:
        st.metric("Most Expensive", f"Rs {filtered['price'].max()/100000:.0f}L")

    st.markdown("---")

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
        cap = 1000
        capped = price_data[price_data <= cap]
        excluded = len(price_data) - len(capped)

        fig2, ax2 = plt.subplots(figsize=(6, 4))
        ax2.hist(capped, bins=30, color="steelblue", edgecolor="white")
        ax2.set_xlabel("Price (Rs Lakhs)")
        ax2.set_ylabel("Number of Listings")
        ax2.set_title(f"Price Distribution (below Rs {cap}L)")
        if excluded > 0:
            ax2.text(0.98, 0.95, f"{excluded} listings above Rs {cap}L not shown",
                     transform=ax2.transAxes, ha="right", va="top",
                     fontsize=7, color="gray")
        plt.tight_layout()
        st.pyplot(fig2)
        plt.close()

    st.markdown("---")

    st.subheader("Price per Sq Ft by Locality")

    if len(filtered_area) == 0:
        st.info("Area data not available for this selection. Price per sq ft cannot be calculated.")
    else:
        ppsf = filtered_area.groupby("locality")["price_per_sqft"].agg(
            Listings="count",
            Avg_Rs_sqft="mean",
            Median_Rs_sqft="median"
        ).round(0).reset_index()

        ppsf = ppsf.sort_values("Median_Rs_sqft")
        ppsf.columns = ["Locality", "Listings", "Avg Rs/sqft", "Median Rs/sqft"]

        st.dataframe(
            ppsf,
            use_container_width=True,
            hide_index=True
        )

    st.markdown("---")

    if locality != "All":
        st.subheader("Nearby Facilities")

        f1, f2, f3 = st.columns(3)

        with f1:
            st.markdown("**Railway Stations**")
            stations = filtered["nearest_railway"].dropna().unique()
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

    st.subheader("Top Developers")
    top_devs = filtered["developer"].value_counts().head(8).reset_index()
    top_devs.columns = ["Developer", "Listings"]
    st.dataframe(top_devs, use_container_width=True, hide_index=True)

    st.markdown("---")

    st.subheader("All Listings")
    display_cols = ["bhk", "price_fmt", "locality", "city",
                    "developer", "possession", "nearest_railway"]
    display_df = filtered[display_cols].copy()
    display_df["nearest_railway"] = display_df["nearest_railway"].str.split("|").str[0].str.strip()
    st.dataframe(
        display_df.rename(columns={
            "bhk"            : "BHK",
            "price_fmt"      : "Price",
            "locality"       : "Locality",
            "city"           : "City",
            "developer"      : "Developer",
            "possession"     : "Possession",
            "nearest_railway": "Nearest Station"
        }),
        use_container_width=True,
        hide_index=True
    )
