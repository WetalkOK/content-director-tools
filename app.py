import streamlit as st
from google import genai
from google.genai import types
from PIL import Image

st.set_page_config(
    page_title="UGC Flow — AI Content Director Studio",
    page_icon="✨",
    layout="wide"
)

# Styling CSS Bersih & Kontras Jelas
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700&family=Playfair+Display:ital@1&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    /* Hero Section */
    .hero-container {
        text-align: center;
        padding: 24px 10px 16px 10px;
    }
    .badge-pill {
        display: inline-flex;
        background: #EDE9FE;
        color: #5B21B6;
        padding: 6px 16px;
        border-radius: 999px;
        font-size: 13px;
        font-weight: 600;
        margin-bottom: 12px;
        border: 1px solid #DDD6FE;
    }
    .hero-title {
        font-size: 2.5rem;
        font-weight: 700;
        color: #0F172A;
        letter-spacing: -0.02em;
        line-height: 1.2;
    }
    .hero-title em {
        font-family: 'Playfair Display', serif;
        font-style: italic;
        color: #6366F1;
        font-weight: 400;
    }
    .hero-subtitle {
        font-size: 1rem;
        color: #64748B;
        max-width: 600px;
        margin: 8px auto 20px auto;
    }

    /* Tombol Utama */
    .stButton > button {
        background: linear-gradient(135deg, #111827 0%, #1F2937 100%) !important;
        color: #FFFFFF !important;
        font-weight: 600 !important;
        border-radius: 999px !important;
        padding: 12px 28px !important;
        border: none !important;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.1) !important;
        width: 100%;
        transition: all 0.2s ease;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #4F46E5 0%, #3730A3 100%) !important;
        transform: translateY(-2px);
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### ⚙️ **Studio Config**")
    api_key = st.text_input("Gemini API Key", type="password", help="Ambil dari Google AI Studio")
    st.markdown("---")
    st.markdown("""
    **Fitur Terintegrasi:**
    - ✨ Vision Multi-Modal Produk & Wajah
    - 🎯 Auto Lock Karakter & Style
    - 🎬 Preset OmniFlow 1.1 Flash
    - ⚡ 100% Free Tier API Ready
    """)

# Hero Section
st.markdown("""
<div class="hero-container">
    <div class="badge-pill">✨ The All-in-One AI Studio for Creators</div>
    <div class="hero-title">Create high-converting <em>Content & Prompts</em> in minutes</div>
    <div class="hero-subtitle">Perencana UGC produk, AI influencer, podcast, hingga video komedi absurd siap render di OmniFlow.</div>
</div>
""", unsafe_allow_html=True)

SYSTEM_DIRECTOR_INSTRUCTION = """
Kamu adalah UGC & AI Content Director profesional untuk Instagram Reels, TikTok, dan Shorts.
Pengguna memakai Flow / OmniFlow (Omni 1.1 Flash) untuk render video dengan durasi 4, 6, 8, atau 10 detik.
Format default: Vertikal 9:16, dialog bahasa Indonesia natural (12-18 kata per durasi 8 detik), prompt visual bahasa Inggris deskriptif tanpa kata klise ('cinematic', 'hyper-realistic').

FORMAT OUTPUT:
1. Konsep & Analisis Visual Aset
2. 3 Pilihan Hook Kuat
3. Script Lengkap (Bahasa Indonesia natural + jeda/ekspresi)
4. Panduan Voice Template
5. Kartu Karakter & Aset
6. Tabel Scene (Timeline, Durasi Render vs Pakai, Aksi, Sudut Kamera)
7. Prompt Gambar Tambahan (Bahasa Inggris jika perlu)
8. Blok Prompt Video OmniFlow (Bahasa Inggris per klip, siap salin)
9. Arahan Editing & 3 Hashtag Relevan
"""

col_left, col_right = st.columns([1.1, 1.3], gap="large")

with col_left:
    st.markdown("#### 🎯 **1. Mode Konten**")
    mode = st.selectbox(
        "Pilih Format Video",
        [
            "UGC Review & Jual Produk (Selling / Soft-Selling)",
            "AI Influencer / Daily Lifestyle",
            "Talking Head Storytelling / Edukasi",
            "Podcast 2 Karakter (Host & Guest)",
            "Video Lucu / Absurd Juxtaposition (Scale-Shift)",
            "Candid Street / Retro DV Camcorder (Early-2000s)"
        ]
    )

    st.markdown("#### 👤 **2. Karakter & Referensi Wajah**")
    upload_char = st.file_uploader("Upload Foto Wajah / Karakter ChatGPT", type=["jpg", "jpeg", "png"])
    if upload_char:
        st.image(upload_char, caption="Karakter Terkunci", width=160)
    char_notes = st.text_input("Nama / Ciri Karakter", placeholder="Contoh: Rania, 23 th, Sawo Matang / Kucing Knight")

    if "Produk" in mode:
        st.markdown("#### 📦 **3. Produk & USP**")
        upload_prod = st.file_uploader("Upload Foto Kemasan Asli", type=["jpg", "jpeg", "png"])
        if upload_prod:
            st.image(upload_prod, caption="Produk Terkunci", width=160)
        prod_title = st.text_input("Nama Produk", placeholder="Contoh: Brightening Serum Glow 30ml")
        prod_benefits = st.text_area("USP / Manfaat", placeholder="Contoh: Tekstur ringan, mencerahkan dalam 14 hari", height=70)
    else:
        upload_prod = None
        st.markdown("#### 💡 **3. Topik / Cerita**")
        prod_title = st.text_input("Topik Utama", placeholder="Contoh: Susahnya konsisten ngonten / Kucing ksatria ketemu naga")
        prod_benefits = ""

    st.markdown("#### 🎬 **4. Teknis & Durasi**")
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        voice_template = st.selectbox("Template Suara", [
            "UGC Natural Curhat",
            "AI Influencer Trendy",
            "Podcast Conversational",
            "Storyteller Reflektif",
            "Komedi / Absurd"
        ])
        clip_duration = st.selectbox("Durasi OmniFlow per Klip", ["4 detik", "6 detik", "8 detik", "10 detik"], index=2)
    with col_c2:
        cam_style = st.selectbox("Gaya Lensa Kamera", [
            "Smartphone Handheld 4K",
            "Early-2000s Handheld Mini-DV",
            "Podcast Studio Warm Lighting",
            "Muted Cool Dawn / Fog",
            "Clean Soft Vanity Daylight"
        ])
        extra_flow = st.text_input("Aksi Kunci", placeholder="Contoh: Kamera jatuh ke rumput")

    st.markdown("<br>", unsafe_allow_html=True)
    generate_btn = st.button("✨ Susun Paket Produksi Lengkap", type="primary")

with col_right:
    st.markdown("#### 📋 **Preview & Output Sutradara**")
    if generate_btn:
        if not api_key:
            st.error("Masukkan Gemini API Key terlebih dahulu di sidebar.")
        elif not prod_title:
            st.warning("Mohon isi nama produk atau topik utama.")
        else:
            client = genai.Client(api_key=api_key)
            prompt_text = f"""
            Buatkan paket produksi lengkap untuk:
            - Mode: {mode}
            - Nama Produk / Topik: {prod_title}
            - Manfaat / USP: {prod_benefits}
            - Karakter: {char_notes}
            - Template Suara: {voice_template}
            - Kamera: {cam_style}
            - Durasi OmniFlow: {clip_duration}
            - Aksi Kunci: {extra_flow}
            """
            payload = [prompt_text]
            if upload_char:
                payload.append(Image.open(upload_char))
                prompt_text += "\n[Karakter]: Kunci ciri wajah, kulit, dan rambut dari gambar karakter yang diunggah ke setiap prompt video."
            if upload_prod:
                payload.append(Image.open(upload_prod))
                prompt_text += "\n[Produk]: Kunci bentuk kemasan, warna tutup, dan label dari foto produk yang diunggah."

            with st.spinner("Menyusun paket produksi..."):
                try:
                    response = client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=payload,
                        config=types.GenerateContentConfig(
                            system_instruction=SYSTEM_DIRECTOR_INSTRUCTION,
                            temperature=0.7
                        )
                    )
                    st.success("Paket produksi siap!")
                    st.markdown(response.text)
                except Exception as e:
                    st.error(f"Terjadi kesalahan API: {str(e)}")
    else:
        st.info("Pilih mode di kolom kiri, unggah aset jika ada, lalu klik tombol untuk memproses.")
