import streamlit as st
from google import genai
from google.genai import types

st.set_page_config(
    page_title="AI Studio All-in-One Director",
    page_icon="🎬",
    layout="wide"
)

# Sidebar: Pengaturan Kunci API & Model
st.sidebar.title("⚙️ Konfigurasi")
api_key = st.sidebar.text_input("Gemini API Key", type="password", help="Dapatkan gratis di Google AI Studio")

SYSTEM_DIRECTOR_INSTRUCTION = """
Kamu adalah AI Content Director profesional untuk Reels, TikTok, dan Shorts.
Pengguna membuat video menggunakan OmniFlow / Flow dengan model Omni 1.1 Flash (pilihan durasi per klip: 4, 6, 8, atau 10 detik).
Format default: Rasio vertikal 9:16, naskah percakapan bahasa Indonesia natural (12-18 kata per durasi 8 detik), dan prompt visual deskriptif bahasa Inggris tanpa istilah klise seperti 'cinematic', 'hyper-realistic', atau 'masterpiece'.

Prinsip Teknis Setiap Mode:
1. UGC Produk: Tekankan pencahayaan natural ala smartphone, tekstur kulit nyata, interaksi fisik memegang kemasan, kontak bayangan, dan reaksi pemakaian spontan.
2. Podcast: Format two-shot / reverse-shot antara Host dan Tamu, gestur mendengarkan alami, mikrofon profesional, lampu hangat ambient, dan dialog saling merespons.
3. Video Lucu / Absurd: Terapkan teknik 'juxtaposition' (misal: ksatria/hewan lucu memegang kopi, kontras situasi) dan transisi skala mendadak (selfie drop to wide).
4. Talking Head / Candid Street: Estetika lensa DV camcorder awal 2000-an, goyangan tangan alami (handheld shake), kebisingan digital lembut, dan gestur kasual tidak selalu kaku menatap lensa.

Format Wajib Output:
1. Konsep & Asumsi Produksi
2. 3 Pilihan Hook Kuat
3. Script Lengkap (Bahasa Indonesia dengan penanda jeda dan ekspresi)
4. Kartu Karakter & Properti (Identitas tetap vs variabel yang bisa berganti)
5. Tabel Scene (Timeline, Durasi Render/Pakai, Aksi/Interaksi, Sudut Kamera)
6. Prompt Gambar Referensi / Character Sheet (Bahasa Inggris)
7. Blok Prompt Video OmniFlow (Bahasa Inggris, mandiri tiap klip, format raw block agar mudah disalin)
8. Catatan Editing, SFX, dan 3 Hashtag Relevan
"""

st.title("🎬 All-in-One Content Director Studio")
st.caption("Generator Naskah, Storyboard, dan Prompt OmniFlow untuk UGC, Podcast, Komedi, & Talking Head")

# Layout Form Input
with st.container():
    col_mode, col_dur, col_cam = st.columns([2, 1, 1])
    
    with col_mode:
        mode = st.selectbox(
            "Pilih Mode Konten",
            [
                "UGC Review & Demonstrasi Produk",
                "Podcast / Obrolan 2 Karakter",
                "Video Komedi / Absurd Juxtaposition",
                "Talking Head / Candid Street (DV Style)"
            ]
        )
    
    with col_dur:
        clip_duration = st.selectbox("Durasi Render OmniFlow", ["4 detik", "6 detik", "8 detik", "10 detik"], index=2)
        
    with col_cam:
        visual_style = st.selectbox(
            "Gaya Kamera & Tekstur",
            [
                "Smartphone Natural 4K",
                "Early-2000s DV Camcorder (Grain & Handheld)",
                "Soft Overcast Dawn / Muted Cool",
                "Studio Podcast Warm Ambient"
            ]
        )

st.write("---")

col_left, col_right = st.columns([1, 1])

with col_left:
    st.subheader("Detail Brief")
    topic = st.text_input("Topik Utama / Nama Produk", placeholder="Contoh: Sabun Cuci Muka, Kucing Ksatria Minum Boba, Obrolan Finansial")
    audience = st.text_input("Target Audiens", placeholder="Contoh: Gen Z, Pekerja Kantoran, Pecinta Kucing")
    
    char_desc = st.text_area(
        "Deskripsi Karakter Utama",
        placeholder="Contoh: Pria 25 tahun kasual / Cewek rambut ponytail kaos abu / Kucing British Shorthair berarmor",
        height=90
    )
    
    extra_context = st.text_area(
        "Instruksi Khusus / Alur Cerita",
        placeholder="Contoh: Awali dengan selfie dekat lalu kamera jatuh ke tanah, beri efek suara ketawa spontan, produk botol kaca dipegang tangan kiri.",
        height=100
    )
    
    submit_btn = st.button("🚀 Susun Paket Produksi", type="primary", use_container_width=True)

with col_right:
    st.subheader("Hasil Rencana & Prompt Produksi")
    
    if submit_btn:
        if not api_key:
            st.error("Masukkan Gemini API Key di sidebar terlebih dahulu.")
        elif not topic:
            st.warning("Mohon isi topik utama atau nama produk.")
        else:
            client = genai.Client(api_key=api_key)
            user_prompt = f"""
            Buatkan paket produksi lengkap untuk:
            - Mode: {mode}
            - Gaya Kamera & Tekstur: {visual_style}
            - Durasi Klip Render: {clip_duration}
            - Topik/Produk: {topic}
            - Target Audiens: {audience}
            - Karakter: {char_desc}
            - Instruksi Tambahan: {extra_context}
            """
            
            with st.spinner("Sutradara sedang merancang storyboard, script, dan prompt..."):
                try:
                    response = client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=user_prompt,
                        config=types.GenerateContentConfig(
                            system_instruction=SYSTEM_DIRECTOR_INSTRUCTION,
                            temperature=0.7,
                        )
                    )
                    st.markdown(response.text)
                except Exception as e:
                    st.error(f"Terjadi kesalahan saat memproses API: {str(e)}")
