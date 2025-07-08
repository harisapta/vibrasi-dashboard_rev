
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import time
import os

st.set_page_config(layout="wide")

# Konfigurasi
THRESHOLD = 0.04  # Batas aman getaran
REFRESH_INTERVAL = 60  # Detik (untuk auto-refresh)

# Sidebar navigation
st.sidebar.title("🧭 Navigasi")
page = st.sidebar.radio("Pilih Halaman:", ["📊 Monitoring", "🔮 Prediksi", "⬆️ Upload Data"])

# Load default data
@st.cache_data(ttl=REFRESH_INTERVAL)
def load_data():
    try:
        df_hist = pd.read_csv("historis_vibrasi_simulasi.csv")
        df_hist["Timestamp"] = pd.to_datetime(df_hist["Timestamp"])
    except:
        df_hist = pd.DataFrame()

    try:
        df_pred = pd.read_csv("forecast_vibrasi_7hari.csv")
        df_pred["ds"] = pd.to_datetime(df_pred["ds"])
    except:
        df_pred = pd.DataFrame()

    return df_hist, df_pred

hist_df, forecast_df = load_data()

# ------------------
# PAGE: Monitoring
# ------------------
if page == "📊 Monitoring":
    st.title("📊 Monitoring Vibrasi Historis")

    if hist_df.empty:
        st.error("Data historis tidak ditemukan.")
    else:
        fig, ax = plt.subplots(figsize=(12, 4))
        ax.plot(hist_df["Timestamp"], hist_df["Acceleration RMS (g)"], label="Vibrasi RMS")
        ax.axhline(THRESHOLD, color='r', linestyle='--', label='Ambang Batas')
        ax.set_xlabel("Waktu")
        ax.set_ylabel("Vibrasi (g)")
        ax.legend()
        st.pyplot(fig)

# ------------------
# PAGE: Prediksi
# ------------------
elif page == "🔮 Prediksi":
    st.title("🔮 Prediksi Vibrasi 7 Hari ke Depan")

    if forecast_df.empty:
        st.error("Data prediksi tidak ditemukan.")
    else:
        fig2, ax2 = plt.subplots(figsize=(12, 4))
        ax2.plot(forecast_df["ds"], forecast_df["yhat"], label="Prediksi")
        ax2.fill_between(forecast_df["ds"], forecast_df["yhat_lower"], forecast_df["yhat_upper"], alpha=0.3, label="Confidence Interval")
        ax2.axhline(THRESHOLD, color='r', linestyle='--', label='Ambang Batas')
        ax2.set_xlabel("Waktu")
        ax2.set_ylabel("Vibrasi (g)")
        ax2.legend()
        st.pyplot(fig2)

        alert_df = forecast_df[forecast_df["yhat"] > THRESHOLD][["ds", "yhat"]]
        if not alert_df.empty:
            st.warning(f"⚠️ {len(alert_df)} jam ke depan diprediksi melebihi batas vibrasi!")
            st.dataframe(alert_df.rename(columns={"ds": "Waktu", "yhat": "Prediksi Vibrasi (g)"}))
        else:
            st.success("✅ Semua prediksi berada di bawah ambang batas.")

# ------------------
# PAGE: Upload Data
# ------------------
elif page == "⬆️ Upload Data":
    st.title("⬆️ Upload Data CSV Baru")

    uploaded_hist = st.file_uploader("Unggah File Historis (historis_vibrasi_simulasi.csv)", type="csv", key="hist")
    if uploaded_hist:
        with open("historis_vibrasi_simulasi.csv", "wb") as f:
            f.write(uploaded_hist.read())
        st.success("✅ File historis berhasil diunggah. Silakan buka halaman Monitoring.")

    uploaded_pred = st.file_uploader("Unggah File Prediksi (forecast_vibrasi_7hari.csv)", type="csv", key="pred")
    if uploaded_pred:
        with open("forecast_vibrasi_7hari.csv", "wb") as f:
            f.write(uploaded_pred.read())
        st.success("✅ File prediksi berhasil diunggah. Silakan buka halaman Prediksi.")

    st.info("📌 Nama file harus sesuai agar dikenali sistem.")
