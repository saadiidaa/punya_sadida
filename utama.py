import os
import pandas as pd
import streamlit as st

# ==========================================
# 1. KONFIGURASI HALAMAN & INJEKSI CSS TOTAL
# ==========================================
st.set_page_config(page_title="Katalog Kebab Premium", layout="wide")

# Suntikan CSS Tingkat Tinggi untuk Bypass Struktur Div Streamlit
st.markdown(
    """
    <style>
    /* --- Efek Animasi & Sudut Halus untuk Pop-Up Dialog --- */
    div[role="dialog"] {
        animation: fadeIn 0.3s ease-in-out;
        border-radius: 15px !important;
        box-shadow: 0px 10px 30px rgba(0, 0, 0, 0.3) !important;
    }
    @keyframes fadeIn {
        from { opacity: 0; transform: scale(0.95); }
        to { opacity: 1; transform: scale(1); }
    }

    /* --- MEMAKSA FLOATING BAR BANTAI PEMBUNGKUS STREAMLIT --- */
    /* Menghilangkan batasan overflow pada container bawaan Streamlit */
    .stApp, .main, .block-container, .stMainZone {
        overflow: visible !important;
    }

    /* Tembak pembungkus elemen Streamlit yang menampung class floating-cart */
    div.stElementContainer:has(div.floating-cart-wrapper) {
        position: fixed !important;
        bottom: 0px !important;
        left: 0px !important;
        width: 100vw !important;
        z-index: 999999 !important;
        background-color: transparent !important;
    }

    /* Styling Bar Putih Keranjang agar Full-Width & Nempel di Layar Terbawah */
    .floating-cart-wrapper {
        background-color: #ffffff !important;
        padding: 15px 40px !important;
        border-top: 2px solid #eaeaea !important;
        box-shadow: 0px -10px 35px rgba(0, 0, 0, 0.12) !important;
        width: 100vw !important;
        box-sizing: border-box !important;
    }
    
    /* Berikan jarak extra di bawah katalog agar item paling bawah tidak ketutup bar keranjang */
    .main .block-container {
        padding-bottom: 180px !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Inisialisasi Session State Keranjang Belanja
if "keranjang" not in st.session_state:
    st.session_state.keranjang = {}


# ==========================================
# 2. FUNGSI POP-UP MODAL (ST.DIALOG)
# ==========================================
@st.dialog("🛒 Detail Pemesanan Menu")
def tampilkan_popup_menu(row):
    nama_foto = str(row["foto"]).strip()
    col_img, col_txt = st.columns([1, 1.5])

    with col_img:
        if os.path.exists(nama_foto):
            st.image(nama_foto, use_container_width=True)

    with col_txt:
        st.subheader(row["nama"])
        st.markdown(f"### **Rp {row['harga']:,}**")
        st.markdown(f"**Status:** {row['status']}")

    st.write("---")
    notes = st.text_input(
        "Tambahkan catatan (misal: pedas, tanpa bawang):", key="popup_notes"
    )

    if st.button("📥 Masukkan ke Keranjang", use_container_width=True):
        nama_item = row["nama"]
        harga_item = int(row["harga"])

        if nama_item in st.session_state.keranjang:
            st.session_state.keranjang[nama_item]["qty"] += 1
            if notes:
                st.session_state.keranjang[nama_item]["notes"] += f"; {notes}"
        else:
            st.session_state.keranjang[nama_item] = {
                "harga": harga_item,
                "qty": 1,
                "notes": notes if notes else "-",
            }

        st.toast(f"✅ {nama_item} ditambahkan!", icon="🛒")
        st.rerun()


@st.dialog("💳 Ringkasan Keranjang & Pembayaran")
def tampilkan_popup_checkout():
    if not st.session_state.keranjang:
        st.warning("Keranjang Anda kosong.")
        return

    total_belanja = 0
    teks_wa = "Halo, saya ingin memesan Kebab:\n\n"

    for nama_item, info in list(st.session_state.keranjang.items()):
        subtotal = info["harga"] * info["qty"]
        total_belanja += subtotal

        teks_wa += f"- *{nama_item}* x{info['qty']}\n"
        teks_wa += f"  Catatan: {info['notes']}\n"
        teks_wa += f"  Subtotal: Rp {subtotal:,}\n\n"

        col_list, col_btn = st.columns([3, 1.5])

        with col_list:
            st.markdown(f"**{nama_item}** ({info['qty']}x)")
            st.caption(f"Catatan: {info['notes']} | Rp {subtotal:,}")

        with col_btn:
            btn_min, btn_plus = st.columns(2)
            with btn_min:
                if st.button("➖", key=f"pop_min_{nama_item}"):
                    st.session_state.keranjang[nama_item]["qty"] -= 1
                    if st.session_state.keranjang[nama_item]["qty"] <= 0:
                        del st.session_state.keranjang[nama_item]
                    st.rerun()
            with btn_plus:
                if st.button("➕", key=f"pop_plus_{nama_item}"):
                    st.session_state.keranjang[nama_item]["qty"] += 1
                    st.rerun()
        st.write("---")

    teks_wa += f"*Total Pembayaran: Rp {total_belanja:,}*"
    st.markdown(f"### **Total: Rp {total_belanja:,}**")

    no_hp = "6281234567890"  # Ganti dengan nomor WhatsApp Toko Anda
    link_wa = f"https://wa.me/{no_hp}?text={teks_wa.replace(' ', '%20').replace('\n', '%0A')}"

    st.link_button(
        "🚀 Lanjut Pembayaran di Whatsapp", link_wa, use_container_width=True
    )


# ==========================================
# 3. HALAMAN UTAMA (KATALOG MENU)
# ==========================================
if os.path.exists("anggrekku.jpg"):
    st.image("anggrekku.jpg", use_container_width=True)

st.title("🥙 Menu Kebab Lezat Berdasarkan Kategori")
st.divider()

try:
    if os.path.exists("data_anggrek1.csv"):
        df = pd.read_csv("data_anggrek1.csv").dropna(subset=["foto"])
        daftar_kategori = df["kategori"].unique()

        for kat in daftar_kategori:
            st.header(f"🔥 Kebab Kategori {kat.capitalize()}")
            data_per_kat = df[df["kategori"] == kat]

            cols = st.columns(4)

            for index, row in data_per_kat.reset_index().iterrows():
                nama_foto = str(row["foto"]).strip()
                col_index = index % 4

                with cols[col_index]:
                    if os.path.exists(nama_foto):
                        st.image(nama_foto, use_container_width=True)
                        st.subheader(row["nama"])
                        st.markdown(f"### **Rp {row['harga']:,}**")

                        if st.button(f"🛒 Order di Sini", key=f"btn_{row['nama']}"):
                            tampilkan_popup_menu(row)
                    else:
                        st.warning(f"Foto '{nama_foto}' tidak ditemukan")
            st.divider()
    else:
        st.error("File data 'data_anggrek1.csv' tidak ditemukan!")
except Exception as e:
    st.error(f"Terjadi kesalahan: {e}")


# ==========================================
# 4. STICKY FLOATING BOTTOM BAR
# ==========================================
if st.session_state.keranjang:
    total_item = sum([item["qty"] for item in st.session_state.keranjang.values()])

    # Mulai pembungkus kustom HTML
    st.markdown('<div class="floating-cart-wrapper">', unsafe_allow_html=True)

    col_bag1, col_bag2 = st.columns([3, 1])
    with col_bag1:
        st.markdown(f"### 🛒 Keranjang Belanja Anda ({total_item} item)")
        st.caption("Menu pilihan Anda siap untuk dicheckout.")

    with col_bag2:
        st.write("")  # Penyeimbang ruang vertikal button
        if st.button("💳 Bayar Sekarang", use_container_width=True, type="primary"):
            tampilkan_popup_checkout()

    # Tutup pembungkus kustom HTML
    st.markdown("</div>", unsafe_allow_html=True)
else:
    # Tampilkan Footer hak cipta normal jika keranjang belanja kosong
    st.caption("© 2026 Toko Kebab Premium Digital - Semua Hak Dilindungi")