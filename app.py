import streamlit as st
from google import genai
from google.genai import types
from PIL import Image

# 1. Konfigurasi Halaman Dasar
st.set_page_config(
    page_title="UGC Flow — AI Content Director Studio",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Styling Modern (CSS Custom ala Clean SaaS Landing Page)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:ital,wght@0,400;0,600;0,700;1,400;1,600&family=Playfair+Display:ital@1&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    /* Background Utama */
    .stApp {
        background: radial-gradient(circle at 50% 0%, #F5F3FF 0%, #FAFAFA 50%, #FFFFFF 100%);
        color: #111827;
    }

    /* Hero Banner Header */
    .hero-container {
        text-align: center;
        padding: 30px 10px 20px 10px;
    }
    .badge-pill {
        display: inline-flex;
        align-items: center;
        background: #EDE9FE;
        color: #5B21B6;
        padding: 6px 16px;
        border-radius: 999px;
        font-size: 13px;
        font-weight: 600;
        margin-bottom: 16px;
        border: 1px solid #DDD6FE;
    }
    .hero-title {
        font-size: 2.8rem;
        font-weight: 700;
        letter-spacing: -0.03em;
        color: #0F172A;
        line-height: 1.2;
        margin-bottom: 8px;
    }
    .hero-title em {
        font-family: 'Playfair Display', serif;
        font-style: italic;
        color: #6366F1;
        font-weight: 400;
    }
    .hero-subtitle {
        font-size: 1.05rem;
        color: #64748B;
        max-width: 650px;
        margin: 0 auto 25px auto;
    }

    /* Card Styling */
    div[data-testid="stVerticalBlock"] > div.element-container:has(.studio-card-start) + div {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.04), 0 8px 10px -6px rgba(0, 0, 0, 0.02);
    }

    /* Tombol Utama (Pill Button ala SaaS) */
    .stButton > button {
        background: linear-gradient(135deg, #111827 0%, #1F2937 100%) !important;
        color: #FFFFFF !important;
        font-weight: 600 !important;
        border-radius: 999px !important;
        padding: 12px 28px !important;
        border: none !important;
        font-size: 15px !important;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.15) !important;
        transition: all 0.2s ease !important;
        width: 100%;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(99, 102, 241, 0.3) !important;
        background: linear-gradient(135deg, #4F46E5 0%, #3730A3 100%) !important;
    }

    /* Input Field & Selectbox */
    .stTextInput input, .stTextArea textarea, .stSelectbox [data-baseweb="select"] {
        border-radius: 12px !important;
        border: 1px solid #E2E8F0 !important;
        background-color: #F8FAFC !important;
        font-size: 14px !important;
        color: #0F172A !important;
    }
    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: #6366F1 !important;
        box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.15) !important;
        background-color: #FFFFFF !important;
    }

    /* Uploader */
    div[data-testid="stFileUploader"] {
        background: #F8FAFC;
        border: 1.5px dashed #CBD5E1;
        border-radius: 14px;
        padding: 12px;
    }

    /* Sidebar Clean */
    section[data-testid="stSidebar"] {
        background-color: #FFFFFF;
        border-right: 1px solid #F1F5F9;
    }
</style>
""", unsafe_allow_html=True)

# 3. Sidebar: Kunci API & Konfigurasi
with st.sidebar:
    st.markdown("### ⚙️ **Studio Config**")
    api_key = st.text_input("Gemini API Key", type="password", help="Dapatkan kunci gratis dari Google AI Studio")
    st.markdown("---")
    st.markdown("""
    **Fitur Terintegrasi:**
    - ✨ Vision Multi-Modal Produk & Wajah
    - 🎯 Auto Lock Karakter & Style
    - 🎬 Preset OmniFlow / Flow 1.1 Flash
    - ⚡ 100% Free Tier API Ready
    """)

# 4. Hero Section Modern ala Contoh Gambar
st.markdown("""
<div class="hero-container">
    <div class="badge-pill">✨ The All-in-One AI Studio for Creators</div>
    <div class="hero-title">Create high-converting <em>Content & Prompts</em> in minutes</div>
    <div class="hero-subtitle">Perencana UGC produk, AI influencer, podcast, hingga video komedi absurd siap render di OmniFlow.</div>
</div>
""", unsafe_allow_html=True)

SYSTEM_DIRECTOR_INSTRUCTION = """
Kamu adalah UGC & AI Content Director profesional untuk Instagram Reels, TikTok, dan Shorts.
Pengguna memakai alur produksi nyata:
- Gambar referensi/karakter dibuat di ChatGPT atau diunggah dari foto nyata.
- Video dirender menggunakan OmniFlow / Flow (Omni 1.1 Flash) dengan opsi durasi per klip: 4, 6, 8, atau 10 detik.
- Format default: Vertikal 9:16, naskah percakapan bahasa Indonesia natural (patokan klip 8 detik: 12-18 kata), dan prompt visual deskriptif bahasa Inggris tanpa istilah klise ('cinematic', 'hyper-realistic', 'photorealistic').

PRINSIP KUNCI:
1. UGC Produk / Commercial: Suasana nyata, kamera HP (natural handheld smartphone), interaksi fisik tangan memegang produk, kontak bayangan, reaksi pemakaian spontan.
2. AI Influencer / Talking Head: Karakter konsisten, tatapan mata hidup, gerak mikro natural, ekspresi tidak kaku, pencahayaan realistis, tekstur kulit berpori alami.
3. Podcast 2 Karakter: Format reverse-shot / two-shot (Host & Tamu), mikrofon podcast, pencahayaan studio hangat, gestur mendengarkan aktif.
4. Video Komedi / Absurd: Juxtaposition kontras situasi (misal ksatria/hewan menggemaskan memegang kopi modern), transisi skala mendadak (selfie POV drop to wide angle).
5. Candid Street / Retro DV Camcorder: Estetika handycam awal 2000-an, slight motion blur, digital noise, soft contrast, aktivitas kasual tanpa memaksakan melihat ke kamera terus-menerus.

JIKA ADA GAMBAR TERUNGGAH:
- Analisis gambar karakter (wajah, rambut, bentuk tubuh, warna kulit) dan kuncilah ciri-ciri tersebut secara deskriptif di setiap prompt OmniFlow.
- Analisis gambar produk (bentuk kemasan, warna botol/tutup, label) dan pastikan produk dipegang atau ditaruh dengan logis.

FORMAT WAJIB OUTPUT:
1. Konsep & Analisis Visual Aset (Karakter & Produk)
2. 3 Pilihan Hook Kuat
3. Script Lengkap (Bahasa Indonesia natural, lengkap tanda jeda [pause] dan ekspresi)
4. Panduan Voice Template (Tone suara, speed bicara, intonasi)
5. Kartu Karakter & Aset (Identitas tetap vs variabel yang bisa berganti)
6. Tabel Scene (Timeline, Durasi Render vs Pakai, Aksi & Kontak Objek, Sudut Kamera)
7. Prompt Gambar Tambahan / Character Sheet (Bahasa Inggris jika perlu)
8. Blok Prompt Video OmniFlow (Bahasa Inggris mandiri per klip, siap salin, mencakup setting, aksi fisik, tatapan, dialog Indonesia, pencahayaan)
9. Arahan Editing, Sound/BGM, dan 3 Hashtag Relevan
"""

# 5. Grid Kolom Studio
col_left, col_right = st.columns([1.1, 1.3], gap="large")

with col_left:
    st.markdown("#### 🎯 **1. Mode & Gaya Konten**")
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
    upload_char = st.file_uploader(
        "Upload Foto Wajah / Karakter ChatGPT",
        type=["jpg", "jpeg", "png"],
        help="Upload foto wajah Anda atau karakter ChatGPT agar AI mengunci ciri fisiknya."
    )
    if upload_char:
        st.image(upload_char, caption="Karakter Terkunci", width=160)
        
    char_notes = st.text_input("Nama / Detail Ciri Karakter", placeholder="Contoh: Rania, 23 th, Sawo Matang / Kucing Knight")

    # Bagian Produk (Disesuaikan dengan mode)
    if "Produk" in mode:
        st.markdown("#### 📦 **3. Referensi & Manfaat Produk**")
        upload_prod = st.file_uploader("Upload Foto Kemasan Asli", type=["jpg", "jpeg", "png"])
        if upload_prod:
            st.image(upload_prod, caption="Produk Terkunci", width=160)
        prod_title = st.text_input("Nama Produk", placeholder="Contoh: Brightening Serum Glow 30ml")
        prod_benefits = st.text_area("USP / Poin Keunggulan", placeholder="Contoh: Tekstur ringan meresap cepat, mencerahkan dalam 14 hari", height=70)
    else:
        upload_prod = None
        st.markdown("#### 💡 **3. Ide Cerita / Topik Pembahasan**")
        prod_title = st.text_input("Topik Utama", placeholder="Contoh: Curhat susahnya konsisten ngonten / Kucing ksatria ketemu naga")
        prod_benefits = ""

    st.markdown("#### 🎬 **4. Teknis Produksi & Voice**")
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        voice_template = st.selectbox("Template Suara", [
            "UGC Natural Curhat (Santai, jeda napas alami)",
            "AI Influencer Trendy (Ceria, artikulasi bersih)",
            "Podcast Conversational (Interaktif, ada tawa kecil)",
            "Storyteller Reflektif (Tempo sedang, emosional)",
            "Komedi / Absurd (Ekspresif, timing punchline rapi)"
        ])
        clip_duration = st.selectbox("Durasi OmniFlow per Klip", ["4 detik", "6 detik", "8 detik", "10 detik"], index=2)
    with col_c2:
        cam_style = st.selectbox("Gaya Lensa Kamera", [
            "Smartphone Handheld 4K (Natural lighting)",
            "Early-2000s Handheld Mini-DV (Low contrast)",
            "Podcast Studio Warm Lighting",
            "Muted Cool Dawn / Fog (Epic Scale)",
            "Clean Soft Vanity Daylight"
        ])
        extra_flow = st.text_input("Aksi Kunci", placeholder="Contoh: Drop kamera ke rumput / Menoleh ke belakang")

    st.markdown("<br>", unsafe_allow_html=True)
    generate_btn = st.button("✨ Susun Paket Produksi Lengkap", type="primary")

with col_right:
    st.markdown("#### 📋 **Preview & Output Sutradara**")
    
    if generate_btn:
        if not api_key:
            st.error("Masukkan Gemini API Key terlebih dahulu di sidebar sebelah kiri.")
        elif not prod_title:
            st.warning("Mohon isi nama produk atau topik utama.")
        else:
            client = genai.Client(api_key=api_key)
            
            prompt_text = f"""
            Buatkan paket produksi lengkap untuk:
            - Mode: {mode}
            - Nama Produk / Topik Utama: {prod_title}
            - Manfaat / Poin Kunci: {prod_benefits}
            - Catatan Karakter: {char_notes}
            - Template Suara: {voice_template}
            - Gaya Visual Kamera: {cam_style}
            - Durasi Render OmniFlow: {clip_duration} (Dialog naskah: 12-18 kata per durasi 8 detik)
            - Aksi Kunci / Tambahan: {extra_flow}
            """
            
            payload = [prompt_text]
            
            if upload_char:
                img_char = Image.open(upload_char)
                payload.append(img_char)
                prompt_text += "\n[PENTING]: Gunakan foto karakter yang diunggah untuk mendeskripsikan struktur wajah, warna kulit, dan rambut secara presisi ke dalam setiap prompt video."
                
            if upload_prod:
                img_prod = Image.open(upload_prod)
                payload.append(img_prod)
                prompt_text += "\n[PENTING]: Gunakan gambar produk yang diunggah agar kemasan fisik, warna tutup, dan logonya akurat di prompt video saat dipegang karakter."
                
            with st.spinner("Merancang script, storyboard, dan prompt OmniFlow..."):
                try:
                    response = client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=payload,
                        config=types.GenerateContentConfig(
                            system_instruction=SYSTEM_DIRECTOR_INSTRUCTION,
                            temperature=0.7
                        )
                    )
                    st.success("Paket produksi siap dieksekusi!")
                    st.markdown(response.text)
                except Exception as e:
                    st.error(f"Terjadi kesalahan API: {str(e)}")
    else:
        st.info("Pilih mode konten di kolom kiri, unggah aset jika ada, lalu klik tombol untuk menyusun seluruh paket produksi.")
