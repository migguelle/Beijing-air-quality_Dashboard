import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

st.set_page_config(
    page_title="Beijing Air Quality Dashboard (2013–2017)",
    page_icon="🌫️",
    layout="wide"
)

sns.set_theme(style="whitegrid")


@st.cache_data
def load_data():
    data_path = os.path.join(os.path.dirname(__file__), "main_data.csv")
    df = pd.read_csv(data_path)
    df["date"] = pd.to_datetime(df["date"])
    return df


df = load_data()

# ==================== SIDEBAR FILTERS ====================
with st.sidebar:
    st.title("🌫️ Air Quality Filter")
    st.caption("Beijing Multi-Site Air Quality (2013–2017)")

    min_date = df["date"].min().date()
    max_date = df["date"].max().date()
    date_range = st.date_input(
        label="Rentang Tanggal",
        min_value=min_date,
        max_value=max_date,
        value=(min_date, max_date)
    )

    all_stations = sorted(df["station"].unique().tolist())
    selected_stations = st.multiselect(
        label="Pilih Stasiun Pemantauan",
        options=all_stations,
        default=all_stations
    )

    pollutant = st.selectbox(
        label="Pilih Polutan Utama",
        options=["PM2.5", "PM10", "SO2", "NO2", "CO", "O3"],
        index=0
    )

    st.markdown("---")
    st.caption("Dibuat oleh: Ezra Migguelle Budi Dharma")

# Validasi input filter
if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date, end_date = min_date, max_date

if not selected_stations:
    st.warning("Silakan pilih minimal 1 stasiun pemantauan di sidebar.")
    st.stop()

filtered_df = df[
    (df["date"].dt.date >= start_date)
    & (df["date"].dt.date <= end_date)
    & (df["station"].isin(selected_stations))
].copy()

if filtered_df.empty:
    st.warning("Tidak ada data untuk rentang tanggal dan stasiun yang dipilih.")
    st.stop()

# ==================== HEADER & KPI METRICS ====================
st.title("🌫️ Dashboard Analisis Kualitas Udara Beijing (2013–2017)")
st.markdown(
    f"Menampilkan ringkasan kualitas udara dari **{len(selected_stations)} stasiun** "
    f"pada periode **{start_date.strftime('%d %b %Y')}** hingga **{end_date.strftime('%d %b %Y')}**."
)

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric(f"Rata-rata {pollutant}", f"{filtered_df[pollutant].mean():.2f} µg/m³")
with col2:
    st.metric(f"Median {pollutant}", f"{filtered_df[pollutant].median():.2f} µg/m³")
with col3:
    worst_station = filtered_df.groupby("station")[pollutant].mean().idxmax()
    worst_val = filtered_df.groupby("station")[pollutant].mean().max()
    st.metric("Stasiun Tertinggi", worst_station, f"{worst_val:.1f} µg/m³", delta_color="inverse")
with col4:
    unhealthy_pct = (
        filtered_df["aqi_category"]
        .isin(["Unhealthy", "Very Unhealthy", "Hazardous"])
        .mean()
        * 100
    )
    st.metric("Hari Unhealthy–Hazardous (PM2.5)", f"{unhealthy_pct:.1f}%")

st.markdown("---")

# ==================== TABS VISUALISASI ====================
tab1, tab2, tab3 = st.tabs([
    "📈 Tren & Perbandingan Stasiun",
    "🌦️ Faktor Cuaca & Pola Musiman",
    "🩺 Kategori AQI (Analisis Lanjutan)"
])

with tab1:
    st.subheader(f"Tren Bulanan Rata-rata {pollutant}")
    monthly_df = (
        filtered_df.set_index("date")[[pollutant]]
        .resample("MS")
        .mean()
        .dropna()
    )
    fig1, ax1 = plt.subplots(figsize=(12, 4.2))
    ax1.plot(monthly_df.index, monthly_df[pollutant], marker="o", markersize=4, linewidth=2.2, color="#C0392B")
    ax1.set_title(f"Tren Rata-rata Bulanan {pollutant}", fontsize=12, fontweight="bold")
    ax1.set_xlabel("Periode")
    ax1.set_ylabel(f"Rata-rata {pollutant} (µg/m³)")
    ax1.spines["top"].set_visible(False)
    ax1.spines["right"].set_visible(False)
    plt.tight_layout()
    st.pyplot(fig1)
    plt.close(fig1)

    st.subheader(f"Perbandingan Rata-rata {pollutant} Antar Stasiun")
    station_avg = filtered_df.groupby("station")[pollutant].mean().sort_values(ascending=True)
    bar_colors = []
    for st_name in station_avg.index:
        if st_name == station_avg.index[-1]:
            bar_colors.append("#C0392B")
        elif st_name == station_avg.index[0]:
            bar_colors.append("#1E8449")
        else:
            bar_colors.append("#BDC3C7")

    fig2, ax2 = plt.subplots(figsize=(11, 5))
    bars = ax2.barh(station_avg.index, station_avg.values, color=bar_colors)
    for bar in bars:
        w = bar.get_width()
        ax2.text(w + (station_avg.max() * 0.01), bar.get_y() + bar.get_height() / 2, f"{w:.2f}", va="center", fontsize=9)
    ax2.set_title(f"Rata-rata {pollutant} per Stasiun (Merah = Tertinggi, Hijau = Terendah)", fontsize=12, fontweight="bold")
    ax2.set_xlabel(f"Rata-rata {pollutant} (µg/m³)")
    ax2.set_ylabel("Stasiun")
    ax2.set_xlim(0, station_avg.max() * 1.12)
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_visible(False)
    plt.tight_layout()
    st.pyplot(fig2)
    plt.close(fig2)

with tab2:
    c1, c2 = st.columns(2)
    with c1:
        st.subheader(f"Rata-rata {pollutant} per Musim")
        season_order = ["Winter", "Autumn", "Spring", "Summer"]
        season_avg = (
            filtered_df.groupby("season")[pollutant]
            .mean()
            .reindex([s for s in season_order if s in filtered_df["season"].unique()])
        )
        s_colors = ["#C0392B" if v == season_avg.max() else "#95A5A6" for v in season_avg.values]
        fig3, ax3 = plt.subplots(figsize=(6.5, 4.5))
        bars3 = ax3.bar(season_avg.index, season_avg.values, color=s_colors)
        for bar in bars3:
            h = bar.get_height()
            ax3.text(bar.get_x() + bar.get_width() / 2, h + (season_avg.max() * 0.02), f"{h:.1f}", ha="center", fontweight="bold")
        ax3.set_title(f"Perbandingan {pollutant} Berdasarkan Musim", fontsize=11.5, fontweight="bold")
        ax3.set_ylabel(f"Rata-rata {pollutant} (µg/m³)")
        ax3.set_ylim(0, season_avg.max() * 1.15)
        ax3.spines["top"].set_visible(False)
        ax3.spines["right"].set_visible(False)
        plt.tight_layout()
        st.pyplot(fig3)
        plt.close(fig3)

    with c2:
        st.subheader("Korelasi Polutan & Faktor Meteorologi")
        corr_cols = ["PM2.5", "PM10", "CO", "NO2", "SO2", "O3", "WSPM", "TEMP", "PRES", "RAIN"]
        corr_mat = filtered_df[corr_cols].corr()
        mask = np.triu(np.ones_like(corr_mat, dtype=bool))
        fig4, ax4 = plt.subplots(figsize=(6.5, 4.5))
        sns.heatmap(corr_mat, mask=mask, annot=True, fmt=".2f", cmap="RdBu_r", center=0, vmin=-1, vmax=1, ax=ax4, annot_kws={"size": 8})
        ax4.set_title("Matriks Korelasi", fontsize=11.5, fontweight="bold")
        plt.tight_layout()
        st.pyplot(fig4)
        plt.close(fig4)

with tab3:
    st.subheader("Distribusi Kategori Kualitas Udara (Standar US EPA PM2.5)")
    aqi_order = ["Good", "Moderate", "Unhealthy (Sensitive)", "Unhealthy", "Very Unhealthy", "Hazardous"]
    aqi_counts = filtered_df["aqi_category"].value_counts(normalize=True).reindex(aqi_order).fillna(0) * 100
    aqi_colors = ["#2ECC71", "#F1C40F", "#E67E22", "#E74C3C", "#8E44AD", "#4A235A"]

    fig5, ax5 = plt.subplots(figsize=(10, 4.5))
    bars5 = ax5.bar(aqi_counts.index, aqi_counts.values, color=aqi_colors)
    for bar in bars5:
        h = bar.get_height()
        ax5.text(bar.get_x() + bar.get_width() / 2, h + 0.8, f"{h:.1f}%", ha="center", fontsize=9.5, fontweight="bold")
    ax5.set_title("Persentase Hari Berdasarkan Kategori AQI PM2.5", fontsize=12, fontweight="bold")
    ax5.set_ylabel("Persentase Hari (%)")
    ax5.set_ylim(0, max(aqi_counts.max() + 8, 10))
    ax5.spines["top"].set_visible(False)
    ax5.spines["right"].set_visible(False)
    plt.xticks(rotation=15)
    plt.tight_layout()
    st.pyplot(fig5)
    plt.close(fig5)

    with st.expander("Lihat Tabel Ringkasan Data Harian"):
        st.dataframe(filtered_df.head(100), use_container_width=True)
