import streamlit as st
import pandas as pd
from datetime import date
import plotly.express as px

# Nama file Excel yang akan langsung dibaca
FILE_EXCEL = "data_akreditasi.xlsx"

# Mengatur judul halaman dan layout
st.set_page_config(page_title="Status Akreditasi Program Studi", layout="wide")

# --- Bagian Header dan Logo ---
col1, col2 = st.columns([1, 4])

with col1:
    # Ganti URL ini dengan URL logo universitas Anda
    st.image("https://upload.wikimedia.org/wikipedia/id/thumb/b/bc/Logo_Universitas_Sriwijaya.svg/1008px-Logo_Universitas_Sriwijaya.svg.png?20240818010951", width=150)

with col2:
    st.title("Sistem Informasi Pemantauan Akreditasi")
    st.write("Aplikasi ini digunakan untuk memantau status akreditasi program studi di lingkungan Universitas Sriwijaya")
    st.markdown("---")

# --- Bagian Pembacaan File Excel ---
try:
    # Langsung membaca data dari file Excel
    df = pd.read_excel(FILE_EXCEL)

    # Mengubah kolom 'Tanggal Kedaluwarsa' menjadi format datetime
    df['Tanggal Kedaluwarsa'] = pd.to_datetime(df['Tanggal Kedaluwarsa'], errors='coerce')

    # Menghitung sisa hari
    today = date.today()
    df['Sisa Hari'] = (pd.to_datetime(df['Tanggal Kedaluwarsa']) - pd.to_datetime(today)).dt.days

    # --- Tambahan: Ringkasan Tabel Kedaluwarsa ---
    st.header("Ringkasan Status Kedaluwarsa")

    # Mengelompokkan data berdasarkan sisa hari
    expired_count = len(df[df['Sisa Hari'] < 30])
    next_30_days_count = len(df[(df['Sisa Hari'] >= 30) & (df['Sisa Hari'] <= 180)])
    next_180_days_count = len(df[(df['Sisa Hari'] > 180) & (df['Sisa Hari'] <= 360)])
    next_360_days_count = len(df[(df['Sisa Hari'] > 360) & (df['Sisa Hari'] <= 720)])

    summary_data = {
        'Rentang Waktu': ['Hampir Kedaluwarsa', '30-180 Hari', '181-360 Hari', '361-720 Hari'],
        'Jumlah Prodi': [expired_count, next_30_days_count, next_180_days_count, next_360_days_count]
    }

    summary_df = pd.DataFrame(summary_data)

    st.dataframe(summary_df, hide_index=True)
    st.markdown("---")

    # Fungsi untuk styling baris
    def row_color(row):
        days_left = row['Sisa Hari']
        if days_left <= 30:
            return ['background-color: #737373']*len(row)  # Abu-abu
        elif days_left <= 180:
            return ['background-color: #ffC0CB']*len(row)  # Merah Muda
        elif days_left <= 360:
            return ['background-color: #ffff00']*len(row)  # Kuning
        else:
            return ['']*len(row)

    #styled_df = df.style.map(get_color, subset=['Sisa Hari'])

    # --- Tata Letak dengan Kolom ---
    st.header("Ringkasan dan Detail Akreditasi")

    # Kolom untuk grafik dan tabel
    col_chart, col_table = st.columns([1, 2])

    with col_chart:
        st.subheader("Ringkasan Status")
        # Grafik batang untuk status akreditasi
        studi_by_akreditasi = df['Status Akreditasi'].value_counts().reset_index()
        studi_by_akreditasi.columns = ['Status Akreditasi', 'Jumlah Program Studi']
        fig_akreditasi = px.bar(studi_by_akreditasi, x='Status Akreditasi', y='Jumlah Program Studi', title='Jumlah Prodi per Status Akreditasi')
        st.plotly_chart(fig_akreditasi, use_container_width=True)

    with col_table:
        st.subheader("Data Akreditasi")
        # Buat DataFrame baru untuk ditampilkan
        df_display = df[['Nama Program Studi', 'Status Akreditasi', 'Tanggal Kedaluwarsa', 'Sisa Hari']].copy()

        # Fitur Pencarian
        search_query = st.text_input("Cari Program Studi:", "")

        if search_query:
            filtered_df = df_display[df_display['Nama Program Studi'].str.contains(search_query, case=False, na=False)]
            st.dataframe(filtered_df, use_container_width=True)
        else:
            st.dataframe(df_display.style.apply(row_color, axis=1), use_container_width=True)

except FileNotFoundError:
    st.error(f"File '{FILE_EXCEL}' tidak ditemukan di folder yang sama. Pastikan file Excel Anda ada di sana.")
except Exception as e:
    st.error(f"Terjadi kesalahan saat membaca file: {e}. Pastikan file Excel Anda memiliki kolom: 'Nama Program Studi', 'Status Akreditasi', 'Tanggal Kedaluwarsa'")
