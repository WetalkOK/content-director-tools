import streamlit as st
from google import genai
from google.genai import types
from PIL import Image

st.set_page_config(
    page_title="OmniStudio Pro — AI Content Director",
    page_icon="🎬",
    layout="wide"
)

# Custom Styling Dashboard Modern
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    .stApp {
        background-color: #FAFAFA;
        color: #0F172A;
    }

    .header-box {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 24px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.04);
    }
    
    .badge {
        display: inline-block;
        background: #EEF2FF;
        color: #4F46E5;
        font-size: 12px;
        font-weight: 700;
        padding: 4px 12px;
        border-radius: 999px;
        margin-bottom: 8px;
    }

    .section-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 18px;
        margin-bottom: 16px;
    }

    .stButton > button {
        background: #0F172A !important;
        color: #FFFFFF !important;
        font-weight: 600 !important;
        border-radius: 10px !important;
        padding: 12px 24px !important;
        width: 100%;
        border: none !important;
        transition: 0.2s;
    }
    .stButton > button:hover {
        background: #4F46E5 !important;
        transform: translateY(-1px);
    }
</style>
""", unsafe_allow_html=True)

# Sidebar Konfigurasi
with st.sidebar:
    st.markdown("### ⚙️ **Konfigurasi Studio**")
    api_key = st.text_input("Gemini API Key", type="password", help="Masukkan API Key dari Google AI Studio")
    st.markdown("---")
    st.markdown("**Standar Video:**\n- Rasio Vertikal: 9:16\n- Engine: Flow / OmniFlow 1.1 Flash\n- Dialog: Bahasa Indonesia Alami\n- Visual Prompt: Bahasa Inggris Deskriptif")

# Header Platform
st.markdown("""
<div class="header-box">
    <span class="badge">PRO DIRECTOR SUITE</span>
    <h2 style="margin: 0; font-size: 1.8rem; font-weight: 700; color: #0F172A;">AI Video Production & Storyboard Director</h2>
    <p style="margin: 6px 0 0 0; color: #64748B; font-size: 0.95rem;">Rancang alur lengkap, analisis aset fisik, script natural, dan prompt video siap eksekusi di OmniFlow.</p>
</div>
""", unsafe_allow_html=True)

SYSTEM_DIRECTOR_INSTRUCTION = """
Kamu adalah AI & UGC Content Director profesional kelas industri untuk konten vertikal (Instagram Reels, TikTok, YouTube Shorts).
Pengguna menggunakan alur kerja produksi nyata dengan model render OmniFlow / Flow (Omni 1.1 Flash) berdurasi 4, 6, 8, atau 10 detik per klip.

STANDAR TEKNIS PRODUKSI:
1. Format & Bahasa:
   - Format visual default 9:16 vertikal.
   - Dialog/naskah dalam bahasa Indonesia percakapan yang natural dan tidak kaku (patokan klip 8 detik: 12-18 kata per dialog agar lip-sync dan tempo realistis).
   - Seluruh prompt visual gambar dan video wajib menggunakan bahasa Inggris deskriptif, konkret, dan bebas kata klise (JANGAN gunakan kata: 'cinematic', 'hyper-realistic', 'ultra-detailed', 'masterpiece').

2. ATURAN KHUSUS TIAP MODE:
   - UGC Review & Produk: Pencahayaan ruangan alami, kamera genggam HP tanpa gimbal, tekstur kulit nyata, interaksi tangan memegang fisik produk, bayangan kontak yang logis.
   - AI Influencer / Lifestyle: Karakter konsisten, tatapan mata hidup, mikro ekspresi, pencahayaan lembut siang hari atau lampu kamar estetik.
   - Podcast 2 Orang: Format reverse-shot / two-shot (Host & Tamu), mikrofon profesional, lampu hangat ambient studio, ekspresi mendengarkan yang responsif.
   - Video Lucu / Absurd: Juxtaposition kontras (misal ksatria/hewan menggemaskan minum es kopi modern), transisi skala cepat (selfie drop to wide view).
   - Candid Street / Mini-DV: Tampilan handycam awal 2000-an, slight digital noise, soft contrast, goyangan kamera tangan santai, interaksi lingkungan sekitar.
   - Drama Pendek Vertikal (C-Drama Style): Sudut kamera dramatis (low angle, close-up tatapan mata tajam), pencahayaan kontras tinggi / moody, gestur tubuh dominan, dialog lugas bertensi tinggi, hook plot-twist dalam 3 detik pertama.

3. PEMROSESAN GAMBAR (MULTIMODAL):
   - Jika ada foto karakter: Ekstrak bentuk wajah, mata, gaya rambut, dan warna kulit secara rinci agar deskripsi karakter terkunci sama di setiap klip.
   - Jika ada foto produk: Ekstrak bentuk botol/kemasan, warna penutup, dan detail label agar interaksi fisik talent dengan produk terasa realistis.

FORMAT OUTPUT WAJIB:
1. Konsep & Analisis Visual Aset (Karakter & Produk)
2. 3 Pilihan Hook Pembuka (Variasi hook rasa ingin tahu, hook visual, dan hook emosional)
3. Script Lengkap & Dialog (Bahasa Indonesia alami, sertakan tanda jeda [pause], intonasi nada bicara, dan ekspresi wajah)
4. Panduan Voice Profile (Tone suara, tempo bicara/BPM, panduan intonasi)
5. Kartu Karakter & Aset (Identitas tetap vs variabel yang bisa berubah)
6. Tabel Storyboard Produksi (Scene ID, Timeline, Durasi Render vs Pakai, Aksi & Kontak Fisik, Sudut Kamera)
7. Prompt Gambar Karakter Sheet / Referensi (Bahasa Inggris)
8. Blok Prompt Video OmniFlow (Bahasa Inggris mandiri tiap klip, siap salin, cantumkan latar, gerakan tangan, arah mata, dialog Indonesia, pencahayaan, dan transisi akhir)
9. Arahan Editing Akhir, Rekomendasi Sound/SFX, dan 3 Hashtag Relevan
"""

col_left, col_right = st.columns([1.1, 1.3], gap="large")

with col_left:
    st.markdown("#### 🎯 **1. Mode & Format Video**")
    mode = st.selectbox(
        "Pilih Format Konten",
        [
            "UGC Review & Demonstrasi Produk (Selling)",
            "AI Influencer / Daily Vlog & Lifestyle",
            "Talking Head Edukasi / Storytelling",
            "Podcast 2 Karakter (Host & Guest Interaktif)",
            "Video Lucu / Absurd Juxtaposition (Scale Shift)",
            "Candid Street / Retro Mini-DV (Early-2000s)",
            "Drama Pendek Vertikal / C-Drama (High Tension & Plot Twist)"
        ]
    )

    st.markdown("#### 👤 **2. Karakter & Referensi Wajah**")
    upload_char = st.file_uploader(
        "Upload Foto Karakter Utama / Wajah Sendiri",
        type=["jpg", "jpeg", "png"],
        help="Upload foto wajah Anda atau karakter ChatGPT agar AI mengunci ciri fisiknya."
    )
    if upload_char:
        st.image(upload_char, caption="Karakter Utama Terkunci", width=160)
        
    char_notes = st.text_input("Detail Ciri Karakter Utama", placeholder="Contoh: Rania, 23 tahun, kulit sawo matang, rambut ikal sebahu")

    # Karakter Tambahan khusus mode Podcast dan Drama
    if mode in ["Podcast 2 Karakter (Host & Guest Interaktif)", "Drama Pendek Vertikal / C-Drama (High Tension & Plot Twist)"]:
        upload_char_2 = st.file_uploader("Upload Foto Karakter Kedua (Lawan Main / Tamu)", type=["jpg", "jpeg", "png"])
        if upload_char_2:
            st.image(upload_char_2, caption="Karakter Kedua Terkunci", width=160)
        char_notes_2 = st.text_input("Detail Ciri Karakter Kedua", placeholder="Contoh: Dion, 28 tahun, jas formal / kemeja santai")
    else:
        upload_char_2 = None
        char_notes_2 = ""

    # Bagian Produk atau Topik
    if "Produk" in mode:
        st.markdown("#### 📦 **3. Referensi & Manfaat Produk**")
        upload_prod = st.file_uploader("Upload Foto Produk Fisik", type=["jpg", "jpeg", "png"])
        if upload_prod:
            st.image(upload_prod, caption="Kemasan Produk Terkunci", width=160)
        prod_title = st.text_input("Nama Produk", placeholder="Contoh: Brightening Serum Glow 30ml")
        prod_benefits = st.text_area("USP & Manfaat Produk", placeholder="Contoh: Tekstur ringan meresap cepat, memudarkan noda hitam dalam 14 hari", height=70)
    else:
        upload_prod = None
        st.markdown("#### 💡 **3. Alur Cerita & Topik Utama**")
        prod_title = st.text_input("Premis Cerita / Topik Pembahasan", placeholder="Contoh: Pewaris kaya yang menyamar / Obrolan rahasia bisnis / Kucing ksatria")
        prod_benefits = st.text_area("Poin Konflik / Pesan Utama", placeholder="Contoh: Dipermalukan di pesta lalu terbongkar status aslinya / Trik menabung realistis", height=70)

    st.markdown("#### 🎬 **4. Teknis Sutradara & Voice**")
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        voice_template = st.selectbox("Template Suara", [
            "UGC Kasual Curhat (Santai, jeda napas terasa)",
            "AI Influencer Trendy (Ceria, artikulasi renyah)",
            "Podcast Dialog Alami (Santai, saling menimpali)",
            "Drama / Teaterikal (Tegang, tegas, berbisik dingin)",
            "Storyteller Reflektif (Tenang, bertempo sedang)",
            "Komedi / Sarkastik (Ekspresif, jeda punchline)"
        ])
        clip_duration = st.selectbox("Durasi OmniFlow per Klip", ["4 detik", "6 detik", "8 detik", "10 detik"], index=2)
    with col_c2:
        cam_style = st.selectbox("Gaya Kamera & Lighting", [
            "Smartphone Handheld 4K (Natural Daylight)",
            "Early-2000s Handheld Mini-DV (Grainy Low-Contrast)",
            "C-Drama Cinematic Contrast (Dramatic Low Angle & Moody)",
            "Studio Podcast Warm Ambient",
            "Muted Cool Dawn / Atmospheric Fog"
        ])
        extra_flow = st.text_input("Aksi Kunci Khusus", placeholder="Contoh: Zoom mendadak ke tatapan mata / Jatuhkan ponsel ke lantai")

    st.markdown("<br>", unsafe_allow_html=True)
    generate_btn = st.button("🚀 Rancang Paket Produksi Lengkap", type="primary")

with col_right:
    st.markdown("#### 📋 **Storyboard & Prompt Siap Render**")
    
    if generate_btn:
        if not api_key:
            st.error("Masukkan Gemini API Key terlebih dahulu di sidebar sebelah kiri.")
        elif not prod_title:
            st.warning("Mohon isi nama produk atau premis cerita utama.")
        else:
            client = genai.Client(api_key=api_key)
            
            prompt_text = f"""
            Buatkan paket produksi lengkap untuk:
            - Mode Produksi: {mode}
            - Nama Produk / Premis Utama: {prod_title}
            - Manfaat / Poin Konflik: {prod_benefits}
            - Ciri Karakter Utama: {char_notes}
            - Ciri Karakter Kedua: {char_notes_2}
            - Profil Template Suara: {voice_template}
            - Gaya Kamera & Pencahayaan: {cam_style}
            - Pilihan Durasi Render OmniFlow: {clip_duration}
            - Aksi Kunci Tambahan: {extra_flow}
            """
            
            payload = [prompt_text]
            
            if upload_char:
                payload.append(Image.open(upload_char))
                prompt_text += "\n[Aset Karakter 1]: Kunci ciri wajah, proporsi, kulit, dan rambut dari gambar ini ke setiap prompt video."
                
            if upload_char_2:
                payload.append(Image.open(upload_char_2))
                prompt_text += "\n[Aset Karakter 2]: Kunci ciri fisik lawan main dari gambar ini ke prompt adegan terkait."
                
            if upload_prod:
                payload.append(Image.open(upload_prod))
                prompt_text += "\n[Aset Produk]: Kunci bentuk fisik botol/kemasan, label, dan warna tutup dari foto produk ini ke prompt adegan interaksi produk."
                
            with st.spinner("Sutradara sedang menyusun storyboard, dialog, dan prompt video..."):
                try:
                    response = client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=payload,
                        config=types.GenerateContentConfig(
                            system_instruction=SYSTEM_DIRECTOR_INSTRUCTION,
                            temperature=0.7
                        )
                    )
                    st.success("Paket produksi berhasil disusun!")
                    st.markdown(response.text)
                except Exception as e:
                    st.error(f"Terjadi kesalahan saat memproses API: {str(e)}")
    else:
        st.info("Pilih mode konten di panel kiri, isi data singkat, lalu klik tombol untuk menghasilkan naskah dan prompt OmniFlow.")
