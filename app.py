import streamlit as st
from google import genai
from google.genai import types
from PIL import Image
import json

st.set_page_config(
    page_title="OmniStudio Pro — AI Content Director",
    page_icon="🎬",
    layout="wide"
)

# Inisialisasi Session State untuk Character Vault & Random Generator
if "character_vault" not in st.session_state:
    st.session_state.character_vault = {}

if "auto_brief" not in st.session_state:
    st.session_state.auto_brief = {
        "title": "",
        "notes": "",
        "action": ""
    }

# Custom Styling
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
    .stButton > button {
        background: #0F172A !important;
        color: #FFFFFF !important;
        font-weight: 600 !important;
        border-radius: 10px !important;
        padding: 10px 20px !important;
        border: none !important;
        transition: 0.2s;
    }
    .stButton > button:hover {
        background: #4F46E5 !important;
        transform: translateY(-1px);
    }
</style>
""", unsafe_allow_html=True)

# Sidebar Konfigurasi & Character Vault
with st.sidebar:
    st.markdown("### ⚙️ **Konfigurasi Studio**")
    api_key = st.text_input("Gemini API Key", type="password", help="Masukkan API Key dari Google AI Studio")
    
    st.markdown("---")
    st.markdown("### 👤 **Character Vault**")
    st.caption("Simpan karakter di sini agar tidak perlu upload ulang.")
    
    new_char_name = st.text_input("Nama Karakter Baru", placeholder="Misal: Rania / Sir Meow")
    new_char_desc = st.text_area("Deskripsi Fisik Singkat", placeholder="Misal: Cewek 23th sawo matang ponytail / Kucing berarmor", height=60)
    new_char_file = st.file_uploader("Upload Foto Karakter", type=["jpg", "jpeg", "png"], key="vault_uploader")
    
    if st.button("💾 Simpan Karakter ke Vault"):
        if new_char_name and new_char_file:
            st.session_state.character_vault[new_char_name] = {
                "image": Image.open(new_char_file),
                "desc": new_char_desc
            }
            st.success(f"Karakter '{new_char_name}' berhasil disimpan!")
        else:
            st.warning("Mohon isi nama dan unggah fotonya.")
            
    if st.session_state.character_vault:
        st.write("---")
        st.markdown("**Karakter Tersimpan:**")
        for cname in list(st.session_state.character_vault.keys()):
            col_k1, col_k2 = st.columns([3, 1])
            col_k1.write(f"• {cname}")
            if col_k2.button("Hapus", key=f"del_{cname}"):
                del st.session_state.character_vault[cname]
                st.rerun()

# Header Platform
st.markdown("""
<div class="header-box">
    <span class="badge">PRO DIRECTOR SUITE</span>
    <h2 style="margin: 0; font-size: 1.8rem; font-weight: 700; color: #0F172A;">AI Video Production & Storyboard Director</h2>
    <p style="margin: 6px 0 0 0; color: #64748B; font-size: 0.95rem;">Simpan karakter tetap di vault, buat ide instan 1-klik, dan susun prompt OmniFlow tanpa ribet.</p>
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
    st.markdown("#### 🎯 **1. Mode Konten & Opsi Otomatis**")
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

    # Fitur Otomatisasi 1-Klik jika Pengguna Malas Mengetik
    col_auto1, col_auto2 = st.columns([2, 1])
    with col_auto1:
        st.caption("Malas mikir atau ngetik? Klik tombol di sebelah kanan 👉")
    with col_auto2:
        if st.button("⚡ Buat Ide Otomatis"):
            if not api_key:
                st.error("Isi API Key di sidebar dulu.")
            else:
                client = genai.Client(api_key=api_key)
                prompt_auto = f"""
                Kamu adalah ideator konten viral. Buatkan SATU ide cerita/brief singkat untuk mode '{mode}'.
                Balas HANYA dalam format JSON persis seperti ini:
                {{
                    "title": "Nama produk atau topik yang menarik",
                    "notes": "Poin keunggulan / konflik utama yang kuat",
                    "action": "Aksi visual kunci atau transisi kamera yang unik"
                }}
                """
                try:
                    res_auto = client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=prompt_auto,
                        config=types.GenerateContentConfig(response_mime_type="application/json")
                    )
                    data = json.loads(res_auto.text)
                    st.session_state.auto_brief["title"] = data.get("title", "")
                    st.session_state.auto_brief["notes"] = data.get("notes", "")
                    st.session_state.auto_brief["action"] = data.get("action", "")
                    st.rerun()
                except Exception as e:
                    st.error(f"Gagal generate otomatis: {e}")

    st.markdown("#### 👤 **2. Pilih / Pasang Karakter**")
    vault_keys = list(st.session_state.character_vault.keys())
    selected_vault = st.selectbox("Pilih dari Vault Karakter (Opsional)", ["-- Upload Manual Baru --"] + vault_keys)

    active_char_img = None
    if selected_vault != "-- Upload Manual Baru --":
        active_char_img = st.session_state.character_vault[selected_vault]["image"]
        st.image(active_char_img, caption=f"Karakter Terpilih: {selected_vault}", width=150)
        char_notes = st.text_input("Ciri Karakter", value=st.session_state.character_vault[selected_vault]["desc"])
    else:
        upload_char = st.file_uploader("Upload Foto Karakter Baru", type=["jpg", "jpeg", "png"])
        if upload_char:
            active_char_img = Image.open(upload_char)
            st.image(active_char_img, caption="Karakter Baru Terkunci", width=150)
        char_notes = st.text_input("Ciri Karakter Baru", placeholder="Contoh: Rania, 23th sawo matang ponytail")

    # Bagian Detail Cerita / Produk
    st.markdown("#### 💡 **3. Detail Konten / Produk**")
    if "Produk" in mode:
        upload_prod = st.file_uploader("Upload Foto Kemasan Produk (Opsional)", type=["jpg", "jpeg", "png"])
        if upload_prod:
            st.image(upload_prod, caption="Kemasan Terkunci", width=150)
        prod_title = st.text_input(
            "Nama Produk",
            value=st.session_state.auto_brief["title"],
            placeholder="Contoh: Brightening Serum Glow 30ml"
        )
        prod_benefits = st.text_area(
            "USP & Poin Keunggulan",
            value=st.session_state.auto_brief["notes"],
            placeholder="Contoh: Tekstur ringan meresap cepat, memudarkan noda hitam",
            height=70
        )
    else:
        upload_prod = None
        prod_title = st.text_input(
            "Topik / Premis Cerita",
            value=st.session_state.auto_brief["title"],
            placeholder="Contoh: Pewaris kaya yang menyamar / Curhat ngonten"
        )
        prod_benefits = st.text_area(
            "Konflik / Pesan Inti",
            value=st.session_state.auto_brief["notes"],
            placeholder="Contoh: Dipermalukan di pesta lalu status aslinya terbongkar",
            height=70
        )

    st.markdown("#### 🎬 **4. Teknis & Suara**")
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        voice_template = st.selectbox("Template Suara", [
            "UGC Kasual Curhat (Santai, jeda napas alami)",
            "AI Influencer Trendy (Ceria, artikulasi renyah)",
            "Podcast Dialog Alami (Santai, interaktif)",
            "Drama / Teaterikal (Tegang, tegas, berbisik dingin)",
            "Storyteller Reflektif (Tenang, bertempo sedang)",
            "Komedi / Sarkastik (Ekspresif, jeda punchline)"
        ])
        clip_duration = st.selectbox("Durasi OmniFlow", ["4 detik", "6 detik", "8 detik", "10 detik"], index=2)
    with col_c2:
        cam_style = st.selectbox("Gaya Kamera", [
            "Smartphone Handheld 4K (Natural Daylight)",
            "Early-2000s Handheld Mini-DV (Grainy Low-Contrast)",
            "C-Drama Cinematic Contrast (Dramatic Low Angle & Moody)",
            "Studio Podcast Warm Ambient",
            "Muted Cool Dawn / Atmospheric Fog"
        ])
        extra_flow = st.text_input(
            "Aksi Kunci",
            value=st.session_state.auto_brief["action"],
            placeholder="Contoh: Kamera jatuh ke tanah / Zoom tatapan tajam"
        )

    st.markdown("<br>", unsafe_allow_html=True)
    generate_btn = st.button("🚀 Rancang Paket Produksi Lengkap", type="primary")

with col_right:
    st.markdown("#### 📋 **Storyboard & Prompt Siap Render**")
    if generate_btn:
        if not api_key:
            st.error("Masukkan Gemini API Key terlebih dahulu di sidebar.")
        elif not prod_title:
            st.warning("Mohon isi nama produk atau premis cerita (atau klik 'Buat Ide Otomatis').")
        else:
            client = genai.Client(api_key=api_key)
            prompt_text = f"""
            Buatkan paket produksi lengkap untuk:
            - Mode Produksi: {mode}
            - Nama Produk / Premis Utama: {prod_title}
            - Manfaat / Konflik: {prod_benefits}
            - Ciri Karakter: {char_notes}
            - Profil Suara: {voice_template}
            - Gaya Kamera & Lighting: {cam_style}
            - Pilihan Durasi Render OmniFlow: {clip_duration}
            - Aksi Kunci: {extra_flow}
            """
            
            payload = [prompt_text]
            if active_char_img:
                payload.append(active_char_img)
                prompt_text += "\n[Karakter]: Kunci ciri wajah, kulit, dan rambut dari gambar karakter terlampir ke setiap prompt video."
            if upload_prod:
                payload.append(Image.open(upload_prod))
                prompt_text += "\n[Produk]: Kunci kemasan, warna tutup, dan label produk dari foto terlampir."

            with st.spinner("Sutradara sedang menyusun naskah dan prompt OmniFlow..."):
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
                    st.error(f"Terjadi kesalahan API: {str(e)}")
    else:
        st.info("Pilih karakter dari vault atau klik '⚡ Buat Ide Otomatis' untuk merancang konten secara instan.")
