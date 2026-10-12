import streamlit as st
from google import genai
from google.genai import types
from PIL import Image

st.set_page_config(
    page_title="AI & UGC Director Studio Pro",
    page_icon="🎬",
    layout="wide"
)

st.sidebar.title("⚙️ Pengaturan Studio")
api_key = st.sidebar.text_input("Gemini API Key", type="password", help="Ambil dari Google AI Studio")

SYSTEM_DIRECTOR_INSTRUCTION = """
Kamu adalah UGC & AI Content Director profesional untuk Instagram Reels, TikTok, dan Shorts.
Pengguna memakai alur kerja: ChatGPT/Gemini untuk perencanaan/referensi karakter, dan Flow/OmniFlow (Omni 1.1 Flash) untuk render video dengan opsi durasi per klip: 4, 6, 8, atau 10 detik.
Format default: 9:16 vertikal, naskah percakapan bahasa Indonesia natural (12-18 kata per durasi 8 detik), prompt visual bahasa Inggris deskriptif tanpa kata klise ('cinematic', 'hyper-realistic', 'photorealistic').

PRINSIP KUNCI:
- UGC Review: Suasana sehari-hari, natural handheld smartphone, interaksi fisik tangan dengan kemasan produk, pencahayaan alami jendela, tekstur kulit nyata.
- Karakter: Pisahkan identitas tetap (tulang wajah, mata, warna kulit) dari pakaian, rambut, ekspresi, dan lokasi.
- Voice/Audio: Berikan arahan nada suara, tempo bicara, dan jeda napas yang jelas.
- Prompt OmniFlow: Harus mandiri per klip, mencakup setting, aksi tangan, arah tatapan, pencahayaan, dialog persis bahasa Indonesia, dan transisi akhir.
"""

st.title("🎬 AI & UGC Director Studio Pro")
st.caption("Perencana Konten Terpadu: Pembuat Karakter, Analisis Produk, Script, Voice Template, & Prompt OmniFlow")

# Navigasi Tab
tab_karakter, tab_konten = st.tabs(["👤 1. Character Studio (Buat Karakter)", "📦 2. Production Planner (UGC / Video Lengkap)"])

# ==========================================
# TAB 1: CHARACTER STUDIO
# ==========================================
with tab_karakter:
    st.subheader("Rancang Kartu Karakter & Prompt Character Sheet")
    st.write("Gunakan tab ini untuk mendesain karakter konsisten dari nol sebelum membuat video.")
    
    col_c1, col_c2 = st.columns([1, 1])
    with col_c1:
        c_name = st.text_input("Nama / ID Karakter", placeholder="Contoh: Rania / Maya / Alex")
        c_gender_age = st.text_input("Gender & Perkiraan Usia", placeholder="Contoh: Wanita Asia Tenggara, 23 tahun")
        c_face = st.text_input("Ciri Wajah & Rambut", placeholder="Contoh: Wajah oval, kulit sawo matang bersih, rambut hitam sebahu bergelombang")
        c_vibe = st.selectbox("Vibe & Gaya Utama", [
            "Kasual Santai Mahasiswi / Gen-Z",
            "Profesional Muda Elegan",
            "Candid Alami Rumahan / Piyama Santai",
            "Streetwear Retro / Y2K",
            "Fantasi / Unik"
        ])
        c_voice = st.selectbox("Profil Suara (Voice Template)", [
            "Ceria, Ramah, Nada Sedang-Tinggi (Cocok untuk UGC Skincare/Beauty)",
            "Santai, Percakapan Sehari-hari, Nada Natural (Cocok untuk Vlog/TikTok)",
            "Tenang, Berwibawa, Nada Rendah (Cocok untuk Podcast/Edukasi)",
            "Ekspresif, Cepat, Antusias (Cocok untuk Review Kuliner/Promo)",
            "Mellow, Hangat, Intim (Cocok untuk Storytelling)"
        ])
        btn_char = st.button("✨ Buat Kartu Karakter & Multi-Angle Sheet", type="primary")

    with col_c2:
        if btn_char:
            if not api_key:
                st.error("Masukkan Gemini API Key di sidebar.")
            else:
                client = genai.Client(api_key=api_key)
                prompt_char = f"""
                Rancang Kartu Karakter Lengkap dan Prompt Image Multi-Angle Character Sheet untuk:
                - Nama: {c_name}
                - Usia & Gender: {c_gender_age}
                - Ciri Fisik: {c_face}
                - Vibe: {c_vibe}
                - Profil Suara: {c_voice}

                Keluarkan format:
                1. Kartu Karakter (ID, Identitas Tetap Wajah/Kulit, Variabel yang Boleh Berganti, Voice Template & Pace Guideline).
                2. Prompt Character Sheet 9-Grid (Bahasa Inggris) untuk digenerate di ChatGPT/Midjourney/Flow mencakup: frontal, 3/4 view, profile side, close-up ekspresi, waist-up, dengan pencahayaan studio netral agar wajah terkunci konsisten.
                """
                with st.spinner("Merancang karakter..."):
                    try:
                        res_char = client.models.generate_content(
                            model="gemini-2.5-flash",
                            contents=prompt_char,
                            config=types.GenerateContentConfig(system_instruction=SYSTEM_DIRECTOR_INSTRUCTION)
                        )
                        st.markdown(res_char.text)
                    except Exception as e:
                        st.error(f"Error: {e}")

# ==========================================
# TAB 2: PRODUCTION PLANNER (UGC & KONTEN)
# ==========================================
with tab_konten:
    st.subheader("Perencanaan Konten & Eksekusi Video")
    
    col_p1, col_p2 = st.columns([1, 1])
    
    with col_p1:
        prod_mode = st.selectbox(
            "Tipe Konten",
            [
                "UGC Review & Demonstrasi Produk (Selling/Soft-Selling)",
                "Talking Head Storytelling / Edukasi",
                "Podcast 2 Karakter (Host & Guest)",
                "Candid Street / Retro Camcorder DV (Early-2000s)",
                "Video Komedi / Juxtaposition Lucu"
            ]
        )
        
        # Upload Produk
        st.markdown("##### 📸 Referensi Produk (Opsional)")
        uploaded_product = st.file_uploader("Upload Foto Kemasan/Bentuk Produk", type=["jpg", "jpeg", "png"])
        if uploaded_product:
            st.image(uploaded_product, caption="Foto Produk Terunggah", width=200)
            
        prod_name = st.text_input("Nama Produk / Topik Utama", placeholder="Contoh: Brightening Serum Glow 30ml / Kopi Susu Botol")
        prod_usp = st.text_area("Manfaat Utama / USP / Poin Penting", placeholder="Contoh: Tekstur ringan tidak lengket, mencerahkan noda hitam dalam 14 hari, wangi lavender menenangkan", height=70)
        
        st.markdown("##### 👤 Karakter & Suara")
        char_ref = st.text_input("Karakter yang Digunakan", placeholder="Contoh: Rania (23 th, Sawo Matang, Ponytail) atau deskripsi singkat")
        voice_style = st.selectbox("Template Suara untuk Scene Ini", [
            "UGC Natural (Santai, seperti curhat ke teman, jeda napas terasa)",
            "Excited Reviewer (Semangat, cepat di hook, artikulasi jelas)",
            "Podcast Conversational (Interaktif, saling timpal, sesekali tawa kecil)",
            "Storyteller Reflektif (Tempo lambat-sedang, penekanan emosi)"
        ])
        
        st.markdown("##### 🎥 Teknis Kamera & Durasi")
        col_sub1, col_sub2 = st.columns(2)
        with col_sub1:
            clip_dur = st.selectbox("Durasi Render OmniFlow", ["4 detik", "6 detik", "8 detik", "10 detik"], index=2)
        with col_sub2:
            cam_style = st.selectbox("Gaya Visual Kamera", [
                "Smartphone Selfie Camera 4K (Natural lighting)",
                "Early-2000s Handheld Mini-DV (Low contrast, digital noise)",
                "Soft Daylight Window (Clean bedroom/vanity)",
                "Cinematic Podcast Studio (Warm ambient, low depth-of-field)"
            ])
            
        extra_story = st.text_area("Alur Cerita Tambahan / Catatan Khusus", placeholder="Contoh: Hook mulai dari muka kusam di cermin, lalu klip kedua apply serum di pipi, klip ketiga senyum puas.", height=70)
        
        btn_prod = st.button("🚀 Susun Paket Produksi Lengkap", type="primary", use_container_width=True)
        
    with col_p2:
        st.subheader("Hasil Rencana Produksi & Prompt OmniFlow")
        if btn_prod:
            if not api_key:
                st.error("Masukkan Gemini API Key di sidebar.")
            elif not prod_name:
                st.warning("Mohon isi nama produk atau topik utama.")
            else:
                client = genai.Client(api_key=api_key)
                
                req_text = f"""
                Buatkan paket produksi lengkap untuk:
                - Mode: {prod_mode}
                - Nama Produk/Topik: {prod_name}
                - Manfaat/USP: {prod_usp}
                - Karakter: {char_ref}
                - Template Suara & Tempo: {voice_style}
                - Durasi Render OmniFlow per Klip: {clip_dur} (Patokan dialog naskah: 12-18 kata per 8 detik)
                - Gaya Visual: {cam_style}
                - Catatan Alur: {extra_story}

                Keluarkan dalam format lengkap:
                1. Konsep & Analisis Visual Produk (Detailkan bagaimana botol/produk dipegang agar logis).
                2. 3 Pilihan Hook Menarik & Script Lengkap (Bahasa Indonesia natural, lengkapi tanda jeda [pause] dan ekspresi).
                3. Panduan Voiceover (Tone, speed/BPM, intonasi).
                4. Tabel Scene Produksi (Scene ID, Timeline, Durasi Render vs Pakai, Aksi & Kontak Produk, Sudut Kamera).
                5. Prompt Gambar Referensi Produk & Karakter (Bahasa Inggris).
                6. Blok Prompt Video OmniFlow (Bahasa Inggris mandiri per klip, siap salin, sertakan aksi fisik detail, arah pandang, dialog Indonesia, dan pencahayaan).
                7. Arahan Editing, Rekomendasi Sound/BGM, dan 3 Hashtag Relevan.
                """
                
                contents_payload = [req_text]
                if uploaded_product:
                    img = Image.open(uploaded_product)
                    contents_payload.append(img)
                    req_text += "\nCatatan: Analisis gambar produk terlampir agar detail bentuk fisik botol, warna tutup, dan label kemasan presisi di prompt video."

                with st.spinner("Sutradara sedang menyusun naskah dan prompt visual..."):
                    try:
                        res_prod = client.models.generate_content(
                            model="gemini-2.5-flash",
                            contents=contents_payload,
                            config=types.GenerateContentConfig(
                                system_instruction=SYSTEM_DIRECTOR_INSTRUCTION,
                                temperature=0.7
                            )
                        )
                        st.markdown(res_prod.text)
                    except Exception as e:
                        st.error(f"Terjadi kesalahan: {e}")
