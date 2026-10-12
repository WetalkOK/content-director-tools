import streamlit as st
from google import genai
from google.genai import types
from PIL import Image

st.set_page_config(
    page_title="AI Studio All-in-One Director Suite",
    page_icon="🎬",
    layout="wide"
)

# Sidebar: Pengaturan Kunci API & Model
st.sidebar.title("⚙️ Konfigurasi Studio")
api_key = st.sidebar.text_input("Gemini API Key", type="password", help="Dapatkan gratis di Google AI Studio")

SYSTEM_DIRECTOR_INSTRUCTION = """
Kamu adalah UGC & AI Content Director profesional untuk Instagram Reels, TikTok, dan Shorts.
Pengguna memakai alur produksi nyata:
- Gambar referensi/karakter dibuat di ChatGPT / diunggah dari foto nyata.
- Video dirender menggunakan OmniFlow / Flow (Omni 1.1 Flash) dengan pilihan durasi per klip: 4, 6, 8, atau 10 detik.
- Format default: Vertikal 9:16, naskah percakapan bahasa Indonesia natural (patokan klip 8 detik: 12-18 kata), dan prompt visual deskriptif bahasa Inggris tanpa istilah klise ('cinematic', 'hyper-realistic', 'photorealistic').

PRINSIP KUNCI SESUAI MODE:
1. UGC Produk / Commercial: Suasana nyata, kamera HP (natural handheld smartphone), interaksi fisik tangan memegang produk, kontak bayangan, reaksi pemakaian spontan.
2. AI Influencer / Talking Head: Karakter konsisten, tatapan mata hidup, gerak mikro natural, ekspresi tidak kaku, pencahayaan realistis, tekstur kulit berpori alami.
3. Podcast / Obrolan 2 Karakter: Format reverse-shot / two-shot (Host & Tamu), mikrofon podcast, pencahayaan warm ambient studio, gestur mendengarkan aktif.
4. Video Lucu / Absurd Juxtaposition: Kontras situasi ekstrem (misal ksatria/hewan menggemaskan memegang kopi modern), transisi skala mendadak (selfie POV drop to wide angle).
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

st.title("🎬 AI Studio All-in-One Director Suite")
st.caption("Director Studio Lengkap: Dukung Upload Foto Karakter/Wajah, Foto Produk, Voice Template, & Prompt OmniFlow")

# Pemilihan Mode Konten
mode = st.selectbox(
    "Pilih Mode Konten",
    [
        "UGC Review & Jual Produk (Selling / Soft-Selling)",
        "AI Influencer / Daily Lifestyle",
        "Talking Head Storytelling / Edukasi",
        "Podcast 2 Karakter (Host & Guest)",
        "Video Lucu / Absurd Juxtaposition (Scale-Shift)",
        "Candid Street / Retro DV Camcorder (Early-2000s)"
    ]
)

st.write("---")

col_left, col_right = st.columns([1, 1])

with col_left:
    st.subheader("1. Karakter & Referensi Wajah")
    upload_char = st.file_uploader(
        "Upload Foto Karakter / Wajah Sendiri / Hasil ChatGPT",
        type=["jpg", "jpeg", "png"],
        help="Upload foto wajah Anda atau karakter yang sudah dibuat di ChatGPT agar Gemini mengunci ciri fisiknya."
    )
    if upload_char:
        st.image(upload_char, caption="Karakter Terkunci", width=180)
        
    char_notes = st.text_input(
        "Nama / Catatan Karakter Tambahan",
        placeholder="Contoh: Rania (23 th, Sawo Matang) / Sir Meow Kucing Ksatria"
    )

    # Bagian Produk (Hanya tampil jika mode butuh produk, atau opsional)
    st.subheader("2. Detail Produk (Khusus UGC / Jual Produk)")
    if "Produk" in mode:
        upload_prod = st.file_uploader(
            "Upload Foto Produk / Kemasan Asli",
            type=["jpg", "jpeg", "png"],
            help="Foto kemasan asli agar bentuk botol, warna, dan label dibaca presisi oleh AI."
        )
        if upload_prod:
            st.image(upload_prod, caption="Produk Terkunci", width=180)
            
        prod_title = st.text_input("Nama Produk", placeholder="Contoh: Brightening Serum Glow 30ml")
        prod_benefits = st.text_area("Manfaat Utama / Keunggulan (USP)", placeholder="Contoh: Tekstur cair cepat meresap, pudarkan bekas jerawat, wangi segar", height=70)
    else:
        upload_prod = None
        prod_title = st.text_input("Topik / Ide Cerita Utama", placeholder="Contoh: Curhat susahnya bikin konten / Obrolan rahasia bisnis / Kucing ketemu naga")
        prod_benefits = ""

    st.subheader("3. Suara, Kamera & Durasi")
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        voice_template = st.selectbox("Template Suara (Voice Profile)", [
            "UGC Natural Curhat (Santai, akrab, jeda napas alami)",
            "AI Influencer Trendy (Ceria, nada sedang-tinggi, artikulasi bersih)",
            "Podcast Conversational (Santai, interaktif, tawa kecil, bersahut-sahutan)",
            "Storyteller Reflektif / Dalam (Tempo sedang-lambat, berbobot)",
            "Komedi / Absurd (Ekspresif, timing punchline jelas)"
        ])
        clip_duration = st.selectbox("Durasi Render OmniFlow per Klip", ["4 detik", "6 detik", "8 detik", "10 detik"], index=2)
        
    with col_s2:
        cam_style = st.selectbox("Gaya Visual Kamera", [
            "Smartphone Handheld Natural 4K (UGC Vibe)",
            "Early-2000s Handheld Mini-DV (Low contrast, grainy)",
            "Podcast Studio Cinematic Warm Lighting",
            "Muted Cool Dawn / Atmospheric Fog (Epic Juxtaposition)",
            "Clean Soft Vanity Daylight"
        ])
        
    extra_instructions = st.text_area(
        "Alur Khusus / Catatan Tambahan Sutradara",
        placeholder="Contoh: Mulai dengan selfie kaget, lalu jatuh ke tanah, atau adegan host melempar candaan ke narasumber.",
        height=80
    )
    
    submit_btn = st.button("🚀 Susun Paket Produksi Lengkap", type="primary", use_container_width=True)

with col_right:
    st.subheader("Hasil Rencana Produksi & Prompt OmniFlow")
    
    if submit_btn:
        if not api_key:
            st.error("Masukkan Gemini API Key di sidebar terlebih dahulu.")
        elif ("Produk" in mode and not prod_title):
            st.warning("Mohon isi nama produk.")
        elif ("Produk" not in mode and not prod_title):
            st.warning("Mohon isi topik atau ide cerita utama.")
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
            - Instruksi Tambahan: {extra_instructions}
            """
            
            payload = [prompt_text]
            
            if upload_char:
                img_char = Image.open(upload_char)
                payload.append(img_char)
                prompt_text += "\n[PENTING]: Gunakan gambar karakter/wajah yang diunggah untuk mendeskripsikan ciri wajah, rambut, kulit, dan bentuk tubuh secara konsisten ke dalam setiap prompt video."
                
            if upload_prod:
                img_prod = Image.open(upload_prod)
                payload.append(img_prod)
                prompt_text += "\n[PENTING]: Gunakan gambar produk yang diunggah untuk mendeskripsikan bentuk kemasan, warna tutup, dan label secara akurat di prompt video dan cara talent memegangnya."
                
            with st.spinner("Sutradara sedang menganalisis visual dan menyusun paket produksi..."):
                try:
                    response = client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=payload,
                        config=types.GenerateContentConfig(
                            system_instruction=SYSTEM_DIRECTOR_INSTRUCTION,
                            temperature=0.7
