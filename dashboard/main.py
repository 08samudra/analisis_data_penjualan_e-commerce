# main.py
# Simpan file ini di dalam direktori 'dashboard'

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np # Untuk operasi numerik, misal nanmean
from pathlib import Path

# --- 1. Konfigurasi Halaman Streamlit ---
st.set_page_config(layout="wide", page_title="Dashboard Analisis Penjualan E-commerce", initial_sidebar_state="expanded")

# --- 2. Fungsi untuk Memuat Data (dengan cache agar lebih cepat) ---
# Folder tempat file main.py berada (dashboard)
BASE_DIR = Path(__file__).resolve().parent

# Folder datasets ada di satu level atas dashboard
DATASET_DIR = BASE_DIR.parent / "datasets"

@st.cache_data
def load_data():
    customers_df = pd.read_csv(DATASET_DIR / 'customers_dataset.csv')
    geolocation_df = pd.read_csv(DATASET_DIR / 'geolocation_dataset.csv')
    order_items_df = pd.read_csv(DATASET_DIR / 'order_items_dataset.csv')
    order_payments_df = pd.read_csv(DATASET_DIR / 'order_payments_dataset.csv')
    order_reviews_df = pd.read_csv(DATASET_DIR / 'order_reviews_dataset.csv')
    orders_df = pd.read_csv(DATASET_DIR / 'orders_dataset.csv')
    product_category_name_translation_df = pd.read_csv(DATASET_DIR / 'product_category_name_translation.csv')
    products_df = pd.read_csv(DATASET_DIR / 'products_dataset.csv')
    sellers_df = pd.read_csv(DATASET_DIR / 'sellers_dataset.csv')

    return customers_df, geolocation_df, order_items_df, order_payments_df, \
           order_reviews_df, orders_df, product_category_name_translation_df, \
           products_df, sellers_df

# Contoh pemanggilan
customers_df, geolocation_df, order_items_df, order_payments_df, \
order_reviews_df, orders_df, product_category_name_translation_df, \
products_df, sellers_df = load_data()

# --- 3. Fungsi untuk Pembersihan dan Pra-pemrosesan Data ---
@st.cache_data
def clean_and_prepare_data(orders_df, products_df, product_category_name_translation_df):
    """
    Melakukan pembersihan data dan penggabungan kategori produk
    untuk analisis.
    """
    # orders_df: Mengubah kolom tanggal menjadi tipe datetime
    date_columns_orders = [
        'order_purchase_timestamp',
        'order_approved_at',
        'order_delivered_carrier_date',
        'order_delivered_customer_date',
        'order_estimated_delivery_date'
    ]
    for col in date_columns_orders:
        orders_df[col] = pd.to_datetime(orders_df[col], errors='coerce')

    # products_df: Mengisi nilai hilang pada kolom numerik & kategori
    products_df['product_category_name'].fillna('unknown_category', inplace=True)
    numerical_product_cols_to_fill = [
        'product_name_lenght', 'product_description_lenght', 'product_photos_qty',
        'product_weight_g', 'product_length_cm', 'product_height_cm', 'product_width_cm'
    ]
    for col in numerical_product_cols_to_fill:
        if col in products_df.columns and products_df[col].isnull().any():
            median_val = products_df[col].median()
            products_df[col].fillna(median_val, inplace=True)

    # Gabungkan produk dengan terjemahan kategori
    products_df_translated = pd.merge(
        products_df,
        product_category_name_translation_df,
        on='product_category_name',
        how='left'
    )
    # Gunakan nama kategori bahasa Inggris untuk tampilan, jika tidak ada, pakai yang asli
    products_df_translated['product_category_name_display'] = products_df_translated['product_category_name_english'].fillna(
        products_df_translated['product_category_name']
    )

    return orders_df, products_df_translated

# --- 4. Memuat dan Membersihkan Data ---
customers_df, geolocation_df, order_items_df, order_payments_df, \
order_reviews_df, orders_df, product_category_name_translation_df, \
products_df, sellers_df = load_data()

orders_df_cleaned, products_df_cleaned = clean_and_prepare_data(orders_df, products_df, product_category_name_translation_df)


# --- 5. Judul Dashboard Utama ---
st.title("📊 Dashboard Analisis Data E-commerce (2017-2018)")
st.markdown("""
    Dashboard ini menyediakan wawasan mendalam mengenai kinerja pengiriman,
    masalah pembatalan pesanan, dan kontribusi pendapatan dari berbagai kategori produk
    di platform E-commerce selama tahun 2017 dan 2018.
""")

# --- 6. Sidebar untuk Navigasi atau Filter Global ---
st.sidebar.title("Navigasi & Filter")
analysis_selection = st.sidebar.radio(
    "Pilih Area Analisis:",
    [
        "1. Durasi Pengiriman",
        "2. Pesanan Bermasalah (Dibatalkan/Tidak Tersedia)",
        "3. Pendapatan Kategori Produk"
    ]
)
st.sidebar.markdown("---")
st.sidebar.header("Tentang Dashboard")
st.sidebar.info(
    "Data diambil dari dataset penjualan E-commerce pada tahun 2017 dan 2018. "
    "Dibuat untuk membantu stakeholder membuat keputusan bisnis yang lebih baik."
)
st.sidebar.header("Kontak")
st.sidebar.write("Jika ada pertanyaan, silakan hubungi tim analis data.")

# --- Bagian Konten Dashboard Berdasarkan Pilihan ---

if analysis_selection == "1. Durasi Pengiriman":
    st.header("1. Rata-rata Waktu Pengiriman Pesanan")
    st.markdown("""
        Menganalisis rata-rata waktu yang dibutuhkan untuk pengiriman pesanan
        hingga sampai ke tangan pelanggan pada tahun 2017 dan 2018.
    """)

    # Filter Tahun
    selected_years_q1 = st.multiselect(
        "Pilih Tahun Analisis:",
        options=[2017, 2018],
        default=[2017, 2018],
        help="Pilih tahun untuk melihat rata-rata durasi pengiriman."
    )

    if not selected_years_q1:
        st.warning("Mohon pilih setidaknya satu tahun untuk analisis durasi pengiriman.")
    else:
        # Filter pesanan dengan status 'delivered' dan tahun yang dipilih
        delivered_orders_filtered = orders_df_cleaned[
            (orders_df_cleaned['order_status'] == 'delivered') &
            (orders_df_cleaned['order_purchase_timestamp'].dt.year.isin(selected_years_q1)) &
            (orders_df_cleaned['order_delivered_customer_date'].notna()) &
            (orders_df_cleaned['order_purchase_timestamp'].notna())
        ].copy()

        # Hitung durasi pengiriman dalam hari
        delivered_orders_filtered['delivery_duration_days'] = (
            delivered_orders_filtered['order_delivered_customer_date'] -
            delivered_orders_filtered['order_purchase_timestamp']
        ).dt.days

        # Hapus nilai negatif (jika ada, menunjukkan data salah)
        delivered_orders_filtered = delivered_orders_filtered[delivered_orders_filtered['delivery_duration_days'] >= 0]

        if delivered_orders_filtered.empty:
            st.info("Tidak ada data pengiriman 'delivered' untuk tahun yang dipilih.")
        else:
            # Hitung rata-rata durasi pengiriman
            average_delivery_time = delivered_orders_filtered['delivery_duration_days'].mean()
            max_delivery_time = delivered_orders_filtered['delivery_duration_days'].max()
            min_delivery_time = delivered_orders_filtered['delivery_duration_days'].min()

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(label="Rata-rata Durasi Pengiriman", value=f"{average_delivery_time:.2f} hari")
            with col2:
                st.metric(label="Durasi Tercepat", value=f"{min_delivery_time:.0f} hari")
            with col3:
                st.metric(label="Durasi Terlama", value=f"{max_delivery_time:.0f} hari")

            st.subheader("Distribusi Durasi Pengiriman")
            # Mengadaptasi tampilan histogram dari seaborn ke plotly
            fig_hist = px.histogram(
                delivered_orders_filtered,
                x='delivery_duration_days',
                nbins=50, # Jumlah bins disesuaikan
                title='Distribusi Durasi Pengiriman Pesanan',
                labels={'delivery_duration_days': 'Durasi Pengiriman (hari)', 'count': 'Jumlah Pesanan'},
                color_discrete_sequence=['skyblue'] # Warna biru muda
            )
            fig_hist.update_traces(marker_line_color='black', marker_line_width=1) # Menambahkan garis tepi hitam
            fig_hist.add_vline(x=average_delivery_time, line_dash="dash", line_color="red", annotation_text=f"Rata-rata: {average_delivery_time:.2f} hari")
            fig_hist.update_layout(bargap=0.1)
            st.plotly_chart(fig_hist, use_container_width=True)

            st.subheader("Durasi Pengiriman terhadap Waktu Pemesanan")
            # Menambahkan scatter plot yang diminta user
            fig_scatter = px.scatter(
                delivered_orders_filtered,
                x='order_purchase_timestamp',
                y='delivery_duration_days',
                title='Durasi Pengiriman terhadap Waktu Pemesanan',
                labels={'order_purchase_timestamp': 'Tanggal Pemesanan', 'delivery_duration_days': 'Durasi Pengiriman (hari)'},
                opacity=0.3, # Sesuaikan alpha
                color_discrete_sequence=['teal'] # Warna teal
            )
            fig_scatter.update_traces(marker=dict(size=5, line=dict(width=1, color='White'))) # Ukuran dan garis tepi
            st.plotly_chart(fig_scatter, use_container_width=True)

            st.markdown(f"""
    <div style='font-size: 1.1em; text-align: justify;'>
        <p><strong>Kesimpulan:</strong></p>
        <ol>
            Rata-rata waktu pengiriman pesanan yang berhasil dikirim pada 2017–2018 adalah 12,07 hari, dengan 75% pesanan tiba dalam 15 hari atau kurang.</li>
            Namun, terdapat kasus ekstrem hingga 209 hari, menunjukkan adanya ketidakkonsistenan logistik pada sebagian kecil pesanan.</li>
        </ol>
        <p><strong>Saran/Rekomendasi:</strong></p>
        <ol>
            Saran agar perusahaan membangun sistem monitoring pengiriman yang akurat dan real-time yang dapat membantu perusahaan mendeteksi keterlambatan lebih cepat.</li>
            Hal ini memungkinkan tim logistik untuk segera mengambil tindakan korektif sebelum masalah membesar.</li>
        </ol>
    </div>
""", unsafe_allow_html=True)



elif analysis_selection == "2. Pesanan Bermasalah (Dibatalkan/Tidak Tersedia)":
    st.header("2. Analisis Pesanan Dibatalkan atau Tidak Tersedia")
    st.markdown("""
        Menganalisis berapa banyak pesanan yang dibatalkan atau tidak tersedia pada tahun 2018,
        dan apakah ada jenis produk atau penjual tertentu yang sering mengalami masalah ini.
    """)

    st.info("Analisis ini secara default fokus pada data tahun 2018, sesuai dengan pertanyaan bisnis.")

    # Filter pesanan tahun 2018 dengan status 'canceled' atau 'unavailable'
    problematic_orders_2018 = orders_df_cleaned[
        (orders_df_cleaned['order_purchase_timestamp'].dt.year == 2018) &
        (orders_df_cleaned['order_status'].isin(['canceled', 'unavailable']))
    ].copy()

    total_problematic_orders = problematic_orders_2018.shape[0]
    st.metric(label="Jumlah Pesanan Dibatalkan/Tidak Tersedia (2018)", value=f"{total_problematic_orders} pesanan")

    # Gabungkan data untuk mendapatkan informasi produk dan penjual
    problematic_orders_merged = pd.merge(
        problematic_orders_2018,
        order_items_df,
        on='order_id',
        how='inner'
    )

    # Gabungkan dengan products_df_cleaned untuk mendapatkan kategori produk (yang sudah diterjemahkan)
    problematic_orders_merged = pd.merge(
        problematic_orders_merged,
        products_df_cleaned[['product_id', 'product_category_name_display']],
        on='product_id',
        how='left'
    )

    if problematic_orders_merged.empty:
        st.info("Tidak ada pesanan dibatalkan/tidak tersedia yang ditemukan pada tahun 2018.")
    else:
        st.subheader("Kategori Produk Teratas dengan Pesanan Bermasalah")
        top_n_categories = st.slider("Tampilkan Top N Kategori:", min_value=5, max_value=20, value=10, step=1, key='q2_cat_slider')
        top_problem_categories = problematic_orders_merged['product_category_name_display'].value_counts().head(top_n_categories)

        if not top_problem_categories.empty:
            fig_cat = px.bar(
                x=top_problem_categories.values,
                y=top_problem_categories.index,
                orientation='h',
                title=f'{top_n_categories} Kategori Produk Teratas dengan Pesanan Dibatalkan/Tidak Tersedia (2018)',
                labels={'x': 'Jumlah Pesanan', 'y': 'Kategori Produk'},
                color=top_problem_categories.values, # Memberi warna berdasarkan jumlah
                color_continuous_scale=px.colors.sequential.Viridis
            )
            fig_cat.update_yaxes(categoryorder='total ascending')
            st.plotly_chart(fig_cat, use_container_width=True)
        else:
            st.info("Tidak ada data kategori produk untuk pesanan bermasalah.")


        st.subheader("Penjual Teratas dengan Pesanan Bermasalah")
        top_n_sellers = st.slider("Tampilkan Top N Penjual:", min_value=5, max_value=20, value=10, step=1, key='q2_seller_slider')
        top_problem_sellers = problematic_orders_merged['seller_id'].value_counts().head(top_n_sellers)

        if not top_problem_sellers.empty:
            fig_seller = px.bar(
                x=top_problem_sellers.values,
                y=top_problem_sellers.index,
                orientation='h',
                title=f'{top_n_sellers} Penjual Teratas dengan Pesanan Dibatalkan/Tidak Tersedia (2018)',
                labels={'x': 'Jumlah Pesanan', 'y': 'ID Penjual'},
                color=top_problem_sellers.values, # Memberi warna berdasarkan jumlah
                color_continuous_scale=px.colors.sequential.Magma
            )
            fig_seller.update_yaxes(categoryorder='total ascending')
            st.plotly_chart(fig_seller, use_container_width=True)
        else:
            st.info("Tidak ada data penjual untuk pesanan bermasalah.")

        st.markdown(f"""
    <div style='font-size: 1.1em; text-align: justify;'>
        <p><strong>Kesimpulan:</strong></p>
        <ol>
            Pada tahun 2018, total 479 pesanan memiliki status canceled atau unavailable. Kategori produk yang paling sering muncul dalam pesanan bermasalah ini adalah 
            beleza_saude (kesehatan & kecantikan) dengan 27 pesanan, utilidades_domesticas (perkakas rumah tangga) dengan 26 pesanan, dan informatica_acessorios 
            (komputer & aksesori) dengan 25 pesanan. Sementara itu, beberapa penjual tertentu, seperti cc419e0650a3c5ba77189a1882b7556a (9 pesanan bermasalah) dan 
            81783131d2a97c8d44d406a4be81b5d9 (6 pesanan bermasalah), menunjukkan tingkat masalah yang lebih tinggi. Masalah ini bisa disebabkan oleh ketidaktersediaan stok, 
            masalah kualitas, atau kendala operasional penjual.</li>
        </ol>
        <p><strong>Saran/Rekomendasi:</strong></p>
        <ol>
            Saran agar semua penjual memiliki sistem inventaris yang terintegrasi dan diperbarui secara real-time untuk menghindari penjualan barang yang tidak tersedia. 
            Audit berkala juga dapat membantu menjaga keakuratan stok dan mencegah pesanan dibatalkan karena kehabisan barang.</li>
        </ol>
    </div>
""", unsafe_allow_html=True)


elif analysis_selection == "3. Pendapatan Kategori Produk":
    st.header("3. Pendapatan Kategori Produk Teratas per Kuartal")
    st.markdown("""
        Menganalisis lima kategori produk teratas yang menjadi penyumbang pendapatan terbesar
        perusahaan secara konsisten setiap tiga bulan (kuartal) di tahun 2017 dan 2018.
    """)

    # Gabungkan dataset yang relevan untuk analisis pendapatan
    orders_payments_df = pd.merge(orders_df_cleaned, order_payments_df, on='order_id', how='inner')
    orders_payments_items_df = pd.merge(orders_payments_df, order_items_df, on='order_id', how='inner')
    full_data_df_q3 = pd.merge(orders_payments_items_df,
                                products_df_cleaned[['product_id', 'product_category_name_display']], # Menggunakan kolom display
                                on='product_id',
                                how='left')

    # Filter data untuk tahun 2017 dan 2018
    filtered_data_q3 = full_data_df_q3[full_data_df_q3['order_purchase_timestamp'].dt.year.isin([2017, 2018])].copy()

    # Ekstrak tahun dan kuartal
    filtered_data_q3['year'] = filtered_data_q3['order_purchase_timestamp'].dt.year
    filtered_data_q3['quarter'] = filtered_data_q3['order_purchase_timestamp'].dt.quarter
    filtered_data_q3['quarter_label'] = filtered_data_q3['year'].astype(str) + '-Q' + filtered_data_q3['quarter'].astype(str)

    # Hitung total pendapatan per kategori produk per kuartal
    revenue_by_category_quarter = filtered_data_q3.groupby(['year', 'quarter', 'quarter_label', 'product_category_name_display'])['payment_value'].sum().reset_index()

    # Cari 5 kategori teratas untuk setiap kuartal
    top_categories_per_quarter = revenue_by_category_quarter.groupby(['year', 'quarter']).apply(
        lambda x: x.nlargest(5, 'payment_value')
    ).reset_index(drop=True)

    # Temukan kategori yang konsisten di top 5
    consistent_categories = set()
    first_quarter_processed = False

    for (year, quarter), group in top_categories_per_quarter.groupby(['year', 'quarter']):
        current_top_5 = set(group['product_category_name_display'].unique())
        if not first_quarter_processed:
            consistent_categories = current_top_5
            first_quarter_processed = True
        else:
            consistent_categories.intersection_update(current_top_5)

    consistent_categories_list = list(consistent_categories)

    if consistent_categories_list:
        st.subheader(f"Kategori Produk yang Konsisten Masuk Top 5 Pendapatan (2017-2018)")
        st.write("Kategori berikut secara konsisten menjadi penyumbang pendapatan terbesar setiap kuartal:")
        for cat in consistent_categories_list:
            st.write(f"- **{cat.title()}**") # Gunakan title() untuk tampilan lebih rapi

        plot_data = revenue_by_category_quarter[
            revenue_by_category_quarter['product_category_name_display'].isin(consistent_categories_list)
        ].copy()
        plot_data = plot_data.sort_values(by=['year', 'quarter'])

        fig_consistent = px.line(
            plot_data,
            x='quarter_label',
            y='payment_value',
            color='product_category_name_display', # Gunakan kolom display untuk legenda
            markers=True,
            title='Pendapatan Kategori Produk Konsisten Top 5 per Kuartal (2017-2018)',
            labels={'payment_value': 'Total Pendapatan (R$)', 'quarter_label': 'Kuartal', 'product_category_name_display': 'Kategori Produk'},
            hover_name='product_category_name_display',
            height=600
        )
        fig_consistent.update_layout(xaxis_title="Kuartal", yaxis_title="Total Pendapatan (R$)", legend_title="Kategori Produk")
        fig_consistent.update_xaxes(tickangle=45)
        st.plotly_chart(fig_consistent, use_container_width=True)

        st.markdown(f"""
    <div style='font-size: 1.1em; text-align: justify;'>
        <p><strong>Kesimpulan:</strong></p>
        <ol>
            Analisis kuartal pada tahun 2017 dan 2018 mengungkapkan bahwa hanya dua kategori produk yang secara konsisten masuk dalam 5 besar 
            penyumbang pendapatan terbesar setiap kuartal: yaitu moveis_decoracao (furnitur & dekorasi) dan cama_mesa_banho 
            (tempat tidur, meja, & kamar mandi). Kedua kategori ini menunjukkan performa yang stabil dan kuat sepanjang periode analisis, 
            menjadikannya sumber pendapatan utama perusahaan. Meskipun kategori lain seperti informatica_acessorios dan beleza_saude 
            juga sering muncul di Top 5, tetapi tidak menunjukkan konsistensi di setiap kuartal.</li>
        </ol>
        <p><strong>Saran/Rekomendasi:</strong></p>
        <ol>
            Saran agar melakukan analisis lebih lanjut pada kategori lain yang sesekali masuk Top 5 (misalnya, informatica_acessorios, 
            beleza_saude, esporte_lazer). Dengan memahami tren musiman dan faktor pendorong spesifik yang menyebabkan lonjakan 
            pendapatan, perusahaan dapat mengembangkan kampanye pemasaran yang lebih strategis dan efektif.</li>
        </ol>
    </div>
""", unsafe_allow_html=True)

    else:
        st.subheader("Tidak Ada Kategori Produk yang Konsisten Masuk Top 5 Pendapatan di Setiap Kuartal.")
        top_5_overall = filtered_data_q3.groupby('product_category_name_display')['payment_value'].sum().nlargest(5)
        st.write("Ini menunjukkan dinamika pasar atau variasi preferensi pelanggan yang cukup tinggi antar kuartal.")
        st.write("Namun, secara keseluruhan untuk periode 2017-2018, 5 kategori dengan pendapatan tertinggi adalah:")
        for category, value in top_5_overall.items():
            st.write(f"- **{category.title()}**: R$ {value:,.2f}")

        plot_data = filtered_data_q3[filtered_data_q3['product_category_name_display'].isin(top_5_overall.index.tE-commerce())].copy()
        plot_data_agg = plot_data.groupby(['quarter_label', 'product_category_name_display'])['payment_value'].sum().reset_index()
        plot_data_agg = plot_data_agg.sort_values(by='quarter_label')

        fig_global_top5 = px.line(
            plot_data_agg,
            x='quarter_label',
            y='payment_value',
            color='product_category_name_display',
            markers=True,
            title='Pendapatan 5 Kategori Produk Teratas Global per Kuartal (2017-2018)',
            labels={'payment_value': 'Total Pendapatan (R$)', 'quarter_label': 'Kuartal', 'product_category_name_display': 'Kategori Produk'},
            hover_name='product_category_name_display',
            height=600
        )
        fig_global_top5.update_layout(xaxis_title="Kuartal", yaxis_title="Total Pendapatan (R$)", legend_title="Kategori Produk")
        fig_global_top5.update_xaxes(tickangle=45)
        st.plotly_chart(fig_global_top5, use_container_width=True)

        st.markdown("""
            <p style='font-size: 1.1em;'>
            Kesimpulan:
            Tidak ada kategori produk yang secara konsisten masuk dalam 5 besar di setiap kuartal sepanjang tahun 2017 dan 2018. Hal ini mengindikasikan dinamika pasar atau variasi preferensi pelanggan yang cukup tinggi antar kuartal. Namun, secara keseluruhan untuk periode 2017-2018, kami telah mengidentifikasi 5 kategori dengan pendapatan tertinggi secara agregat, yang trennya ditunjukkan pada grafik di atas.
            </p>
            <p style='font-size: 1.1em;'>
            Saran/Rekomendasi:
            <ol style='font-size: 1.1em;'>
                <li><b>Analisis Tren Fluktuatif:</b> Lakukan analisis lebih lanjut untuk memahami penyebab fluktuasi kategori-kategori ini. Apakah ada efek musiman yang kuat, promosi spesifik, atau perubahan tren konsumen yang mempengaruhi performa mereka di kuartal tertentu?</li>
                <li><b>Strategi Pemasaran Fleksibel:</b> Kembangkan strategi pemasaran yang lebih adaptif dan responsif terhadap perubahan tren pasar kuartalan. Ini bisa melibatkan kampanye promosi yang ditargetkan pada kategori tertentu di waktu-waktu puncak mereka.</li>
                <li><b>Diversifikasi Portofolio:</b> Meskipun tidak ada "bintang" yang konsisten, keberadaan beberapa kategori yang silih berganti masuk Top 5 menunjukkan peluang untuk diversifikasi portofolio produk. Investasikan pada beberapa kategori yang menjanjikan untuk mengurangi ketergantungan pada satu atau dua pilar pendapatan utama.</li>
            </ol>
            </p>
        """, unsafe_allow_html=True)


# --- Footer Dashboard (Opsional) ---
st.markdown(
    """
    <style>
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: #f0f2f6;
        color: grey;
        text-align: center;
        padding: 10px;
        font-size: 0.9em;
    }
    </style>
    <div class="footer">
        Dibuat dengan Streamlit & Data E-commerce | © 2025 Yoga Samudra
    </div>
    """,
    unsafe_allow_html=True
)