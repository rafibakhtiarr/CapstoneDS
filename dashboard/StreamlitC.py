import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.patches as mpatches

# --- 1. CONFIG DASHBOARD ---
st.set_page_config(
    page_title="BinGo: Your AI Lens for a Cleaner Beach",
    page_icon="♻️",
    layout="wide"
)

# --- 2. FUNGSI LOGIKA DATA (Feature Engineering) ---
def cek_hardness(nama_sampah, category):
    nama_sampah, category = str(nama_sampah).lower(), str(category).lower()
    if category in ['metal', 'glass/ceramics', 'processed/worked wood']: return 'Hard'
    if category in ['cloth/textile', 'paper/cardboard', 'rubber']: return 'Flexible'
    barang_lunak = ['bag', 'wrapper', 'foil', 'rope', 'string', 'cloth', 'net', 'paper', 'flexible', 'sack', 'sponge', 'line', 'band', 'sheeting', 'foam', 'balloon', 'condom', 'diaper', 'towel', 'mesh']
    barang_keras = ['bottle', 'can', 'glass', 'ceramic', 'wood', 'metal', 'cap', 'lid', 'hard', 'box', 'ring', 'container', 'crate', 'pot', 'helmet', 'cartridge', 'cone', 'cd', 'telephone', 'tube', 'bucket', 'lighter', 'pen', 'comb', 'toy', 'cutlery', 'tray', 'stick', 'pallet', 'jar']
    if any(kata in nama_sampah for kata in barang_keras): return 'Hard'
    if any(kata in nama_sampah for kata in barang_lunak): return 'Flexible'
    return 'unknown'

def cek_recycle(generalname, category):
    generalname, category = str(generalname).lower(), str(category).lower()
    sampah_no = ['cigarette', 'diaper', 'nappies', 'sanitary', 'tampon', 'feces', 'medical', 'syringe', 'needle', 'condom', 'sponge', 'foam', 'tangled', 'shotgun', 'chemicals', 'unidentified', 'matches', 'brushes']
    if any(kata in generalname for kata in sampah_no) or category in ['chemicals', 'unidentified']: return 'No'
    if category in ['metal', 'glass/ceramics', 'paper/cardboard']: return 'Yes'
    plastik_ya = ['bottle', 'container', 'cap', 'lid', 'crate', 'box', 'bucket', 'jar']
    if category == 'plastic' and any(kata in generalname for kata in plastik_ya): return 'Yes'
    wood_ya = ['timber', 'pallets', 'crates', 'wood']
    if category == 'processed/worked wood' and any(kata in generalname for kata in wood_ya): return 'Yes'
    return 'No'

# --- 3. LOAD & PROCESS DATA ---
@st.cache_data
def load_data():
    data = pd.read_csv("D:/FILE VSCODE/Capstone/Data_Sampah.csv")
    data['Recyclability'] = data.apply(lambda row: cek_recycle(row['generalname'], row['category']), axis=1)
    data['Hardness'] = data.apply(lambda row: cek_hardness(row['generalname'], row['category']), axis=1)
    
    if 'EventDate' in data.columns:
        data['EventDate'] = pd.to_datetime(data['EventDate'])
        
    return data

df = load_data()

# --- 4. SIDEBAR ---
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/3299/3299935.png", width=100)
st.sidebar.title("BinGo Navigation")
page = st.sidebar.selectbox("Pilih Halaman:", ["Overview", "Material Analysis"])

st.sidebar.markdown("---")
st.sidebar.info("""
**BinGo: Your AI Lens for a Cleaner Beach:**
platform inovatif berbasis computer vision dan machine learning yang dikembangkan untuk mengidentifikasi dan mengklasifikasikan sampah di kawasan pantai secara cepat dan akurat.
""")

# --- 5. MAIN PAGE: OVERVIEW ---
if page == "Overview":
    st.title("🌊 BinGo: Your AI Lens for a Cleaner Beach")
    
    m1, m2, m3 = st.columns(3)
    with m1:
        st.metric("Total Items Found", f"{df['Jumlah_Sampah'].sum():,}")
    with m2:
        recyc_rate = (df[df['Recyclability'] == 'Yes']['Jumlah_Sampah'].sum() / df['Jumlah_Sampah'].sum()) * 100
        st.metric("Recyclability Rate", f"{recyc_rate:.1f}%")
    with m3:
        st.metric("Dominant Category", df['category'].mode()[0])

    st.markdown("---")
    st.subheader("Komposisi Kategori Material Sampah")
    
    comp_data = df.groupby('category')['Jumlah_Sampah'].sum().reset_index().sort_values('Jumlah_Sampah', ascending=True)
    custom_colors = {
        'Plastic': '#FF0000',
        'Metal': '#2B6CB0',
        'Glass/Ceramics': '#4299E1',
        'Cloth/Textile': '#63B3ED',
        'Rubber': '#90CDF4',
        'Paper/Cardboard': '#CBD5E0',
        'Processed/Worked Wood': '#E2E8F0',
        'Unidentified': '#EDF2F7'
    }
    
    fig1 = px.bar(
        comp_data, 
        x='Jumlah_Sampah', 
        y='category', 
        orientation='h', 
        color='category', 
        text='Jumlah_Sampah',
        color_discrete_sequence=px.colors.sequential.RdBu
    )
    
    fig1.update_layout(height=600, showlegend=False, yaxis={'categoryorder':'trace'})
    st.plotly_chart(fig1, use_container_width=True)

    st.markdown("---")
    st.subheader("Rasio Daur Ulang Recyclability vs Non Recyclability")
    _, cent_co, _ = st.columns([1, 2, 1])
    with cent_co:
        recyc_data = df.groupby('Recyclability')['Jumlah_Sampah'].sum().reset_index()
        fig2 = px.pie(recyc_data, values='Jumlah_Sampah', names='Recyclability', hole=0.4, color='Recyclability', color_discrete_map={'Yes': '#2ecc71', 'No': '#e74c3c'})
        st.plotly_chart(fig2, use_container_width=True)

# --- 6. MAIN PAGE: MATERIAL ANALYSIS ---
elif page == "Material Analysis":
    st.title("🔍 In-depth Material Analysis")
    
    # --- 1. Recyclability Rate per Kategori ---
    st.subheader("Recyclability Rate per Kategori Material Sampah")
    pivot1 = df.groupby('category').agg(TotalSampah=('Jumlah_Sampah', 'sum')).reset_index()
    recyc_yes = df[df['Recyclability'] == 'Yes'].groupby('category')['Jumlah_Sampah'].sum().reset_index()
    pivot1 = pivot1.merge(recyc_yes, on='category', how='left').fillna(0)
    pivot1['%Recyclability'] = (pivot1['Jumlah_Sampah'] / pivot1['TotalSampah']) * 100
    pivot1 = pivot1.set_index('category')
    
    pivot1_sorted = pivot1.sort_values(by='%Recyclability', ascending=True)
    def get_color(val):
        if val >= 70: return '#60b589'
        elif val >= 50: return '#eec365'
        elif val >= 30: return '#e08a5b'
        else: return '#cd5a5a'
    
    colors = [get_color(v) for v in pivot1_sorted['%Recyclability']]
    fig_rate, ax = plt.subplots(figsize=(12, 8))
    ax.barh(pivot1_sorted.index, [100] * len(pivot1_sorted), color="#ecebeb", height=0.6)
    ax.barh(pivot1_sorted.index, pivot1_sorted['%Recyclability'], color=colors, height=0.6)

    for i, (pct, total) in enumerate(zip(pivot1_sorted['%Recyclability'], pivot1_sorted['TotalSampah'])):
        ax.text(pct + 1.5, i, f"{int(pct)}%", color=colors[i], va='center', fontweight='bold')
        ax.text(98.5, i, f"{int(total):,} t", color="#656565", va='center', ha='right')

    legend_elements = [
        mpatches.Patch(color="#60b589", label='Mudah didaur ulang (≥70%)'),
        mpatches.Patch(color='#eec365', label='Dapat didaur ulang (50-69%)'),
        mpatches.Patch(color='#e08a5b', label='Perlu penanganan khusus (30-49%)'),
        mpatches.Patch(color='#cd5a5a', label='Sulit didaur ulang (<30%)')
    ]
    ax.legend(handles=legend_elements, loc='lower right')
    st.pyplot(fig_rate)

    st.markdown("---")

    # --- 2. Visualisasi Hardness (FIXED PROPORSI VOLUME) ---
    st.subheader("Probabilitas Daur Ulang Berdasarkan Kekerasan Material")
    
    # Perbaikan: menggunakan sum() dari Jumlah_Sampah agar proporsinya sama persis dengan Gambar 13
    hardness_analysis = df.groupby(['Hardness', 'Recyclability'])['Jumlah_Sampah'].sum().unstack().fillna(0)
    
    cols = [c for c in ['No', 'Yes'] if c in hardness_analysis.columns]
    hardness_pct = hardness_analysis[cols].div(hardness_analysis[cols].sum(axis=1), axis=0)*100
    
    fig_mat, ax2 = plt.subplots(figsize=(10, 6))
    warna_chart = ['#e74c3c', '#2ecc71'] if len(cols) == 2 else ['#3498db']
    hardness_pct.plot(kind='bar', stacked=True, color=warna_chart, ax=ax2, edgecolor='black', linewidth=1)
    ax2.set_xticklabels(ax2.get_xticklabels(), rotation=0)

    for p in ax2.patches:
        h = p.get_height()
        if h > 5:
            ax2.text(p.get_x() + p.get_width()/2, p.get_y() + h/2, f'{h:.1f}%', ha='center', va='center', color='white', fontweight='bold')
    st.pyplot(fig_mat)

    st.markdown("---")

    # --- 3. Top 10 Jenis Sampah Non-Recyclable ---
    st.subheader("10 Jenis Sampah yang Paling Banyak Tidak Bisa Didaur Ulang")
    fig_non, ax3 = plt.subplots(figsize=(10, 6))
    non_recyc = df[df['Recyclability'] == 'No']['generalname'].value_counts().nlargest(10)
    sns.barplot(x=non_recyc.values, y=non_recyc.index, color="skyblue", ax=ax3)
    ax3.set_xlabel('Jumlah Temuan')
    ax3.set_ylabel('Nama Jenis Sampah')
    st.pyplot(fig_non)

    st.markdown("---")

    # --- 4. LINE CHART (Tren Sampah Plastik) ---
    st.subheader("Tren Sampah Plastik Tahun 2013-2021")
    fig_line, ax4 = plt.subplots(figsize=(10, 6))
    
    plastic_per_year = (
        df[df['category'] == 'Plastic']
        .groupby(df['EventDate'].dt.year)['Jumlah_Sampah']
        .sum()
    )
    
    plastic_per_year.plot(marker='o', ax=ax4)
    ax4.set_xlabel('Year')
    ax4.set_ylabel('Total Sampah Plastik')
    ax4.grid(True, linestyle='--', alpha=0.7)
    
    st.pyplot(fig_line)

# --- 7. FOOTER ---
st.markdown("---")
st.caption("BinGo: Your AI Lens for a Cleaner Beach Dashboard | Created by CC26-PSU157 - 2026")