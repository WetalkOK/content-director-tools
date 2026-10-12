import streamlit as st
from google import genai
from PIL import Image
import base64
import io
import json

st.set_page_config(
    page_title="OmniStudio Compact Pro",
    page_icon="🎬",
    layout="wide"
)

# Model resmi sesuai dokumentasi Google AI Studio terbaru
TARGET_MODEL = "gemini-3.8-flash"

def image_to_base64_part(pil_image):
    """Konversi PIL Image ke format data inline Base64 untuk Interactions API."""
    buffered = io.BytesIO()
    pil_image.save(buffered, format="JPEG")
    b64_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
    return {
        "type": "image",
        "data": b64_str,
        "mime_type": "image/jpeg"
    }

# Session State
if "character_vault" not in st.session_state:
    st.session_state.character_vault = {}

if "auto_brief" not in st.session_state:
    st.session_state.auto_brief = {"title": "", "notes": "", "action": ""}

# CSS Compact & Minimalist
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
    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 1.5rem !important;
        max-width: 95% !important;
    }
    div[data-testid="stVerticalBlock"] > div {
        gap: 0.4rem !important;
    }
    .compact-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 10px 18px;
        margin-bottom: 12px;
    }
    .stButton > button {
        background: #0F172A !important;
        color: #FFFFFF !important;
        font-weight: 600 !important;
        border-radius: 8px !important;
        padding: 6px 14px !important;
        border: none !important;
        font-size: 13px !important;
    }
    .stButton > button:hover {
        background: #4F46E5 !important;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
# Sidebar
with st.sidebar:
    st.markdown("### ⚙️ **Konfigurasi**")
    # Cek apakah tersimpan di Streamlit Secrets, jika tidak ambil dari input manual
    default_key = st.secrets.get("GEMINI_API_KEY", "") if hasattr(st, "secrets") else ""
    api_key = st.text_input("Gemini API Key", value=default_key, type="password")
    st.caption(f"Engine: Interactions API ({TARGET_MODEL})")
    
    st.markdown("---")
    st.markdown("### 👤 **Character Vault**")
    c_name = st.text_input("Nama Karakter", key="v_name")
    c_desc = st.text_input("Ciri Fisik", placeholder="Contoh: 23th sawo matang ponytail", key="v_desc")
    c_img = st.file_uploader("Upload Foto", type=["jpg", "jpeg", "png"], key="v_img")
    
    if st.button("💾 Simpan ke Vault", use_container_width=True):
        if c_name and c_img:
            st.session_state.character_vault[c_name] = {
                "image": Image.open(c_img),
                "desc": c_desc
            }
            st.success(f"'{c_name}' tersimpan!")
        else:
            st.warning("Nama dan foto wajib diisi.")
            
    if st.session_state.character_vault:
        st.markdown("**Daftar Tersimpan:**")
        for k in list(st.session_state.character_vault.keys()):
            c1, c2 = st.columns([3, 1])
            c1.caption(f"• {k}")
            if c2.button("✕", key=f"d_{k}"):
                del st.session_state.character_vault[k]
                st.rerun()

# Header
st.markdown("""
<div class="compact-header">
    <div>
        <strong style="font-size: 1.15rem; color: #0F172A;">🎬 OmniStudio Pro Director</strong>
        <span style="font-size: 0.8rem; color: #64748B; margin-left: 8px;">UGC • Podcast • Komedi • C-Drama • Talking Head</span>
    </div>
    <span style="font-size: 0.75rem; background: #EEF2FF; color: #4F46E5; padding: 3px 8px; border-radius: 6px; font-weight: 600;">9:16 ENGINE</span>
</div>
""", unsafe_allow_html=True)

SYSTEM_DIRECTOR_INSTRUCTION = """
Kamu adalah AI & UGC Content Director profesional untuk Reels, TikTok, Shorts.
Engine render pengguna: OmniFlow / Flow 1.1 Flash (durasi 4, 6, 8, atau 10 detik).
Format: 9:16 vertikal, dialog Indonesia natural (12-18 kata per 8 detik), prompt visual bahasa Inggris deskriptif tanpa kata klise ('cinematic', 'hyper-realistic').

Format Output:
1. Konsep & Analisis Visual
2. 3 Pilihan Hook
3. Script & Dialog (Lengkap jeda & ekspresi)
4. Panduan Voice Profile
5. Kartu Karakter & Aset
6. Tabel Storyboard (Timeline, Durasi, Aksi, Kamera)
7. Prompt Gambar Tambahan
8. Blok Prompt Video OmniFlow (Per klip, mandiri, siap salin)
9. Arahan Editing & Hashtags
"""

col_left, col_right = st.columns([1, 1.2], gap="medium")

with col_left:
    c_m1, c_m2 = st.columns([2.2, 1.2])
    with c_m1:
        mode = st.selectbox(
            "Format Konten",
            [
                "UGC Review & Jual Produk",
                "AI Influencer / Daily Vlog",
                "Talking Head Edukasi",
                "Podcast 2 Karakter",
                "Video Lucu / Absurd Juxtaposition",
                "Candid Street Mini-DV (2000s)",
                "Drama Pendek Vertikal / C-Drama"
            ],
            label_visibility="collapsed"
        )
    with c_m2:
        if st.button("⚡ Ide Otomatis", use_container_width=True):
            if not api_key:
                st.error("Isi API Key di sidebar.")
            else:
                client = genai.Client(api_key=api_key)
                prompt_auto = (
                    f"Buat 1 ide menarik untuk format '{mode}'. "
                    "Kembalikan HANYA teks JSON yang valid tanpa Markdown fence dengan key: title, notes, action."
                )
                try:
                    interaction = client.interactions.create(
                        model=TARGET_MODEL,
                        input=prompt_auto
                    )
                    raw_text = interaction.output_text.strip()
                    if raw_text.startswith("```json"):
                        raw_text = raw_text[7:]
                    if raw_text.startswith("```"):
                        raw_text = raw_text[3:]
                    if raw_text.endswith("```"):
                        raw_text = raw_text[:-3]
                    data = json.loads(raw_text.strip())
                    st.session_state.auto_brief["title"] = data.get("title", "")
                    st.session_state.auto_brief["notes"] = data.get("notes", "")
                    st.session_state.auto_brief["action"] = data.get("action", "")
                    st.rerun()
                except Exception as e:
                    st.error(f"Gagal generate otomatis: {e}")

    tab_aset, tab_detail, tab_kamera = st.tabs(["👤 Karakter & Produk", "📝 Cerita & Naskah", "🎬 Kamera & Suara"])

    active_char_img = None
    upload_prod_img = None

    with tab_aset:
        v_keys = list(st.session_state.character_vault.keys())
        sel_char = st.selectbox("Pilih Karakter dari Vault", ["-- Upload Baru --"] + v_keys)
        
        col_img1, col_img2 = st.columns(2)
        with col_img1:
            if sel_char != "-- Upload Baru --":
                active_char_img = st.session_state.character_vault[sel_char]["image"]
                st.image(active_char_img, width=110)
                char_notes = st.text_input("Ciri Karakter", value=st.session_state.character_vault[sel_char]["desc"])
            else:
                up_c = st.file_uploader("Wajah/Karakter", type=["jpg", "png"], key="single_up_c")
                if up_c:
                    active_char_img = Image.open(up_c)
                    st.image(active_char_img, width=90)
                char_notes = st.text_input("Ciri Karakter", placeholder="Contoh: Rania 23th sawo matang")
        
        with col_img2:
            if "Produk" in mode:
                up_p = st.file_uploader("Foto Produk", type=["jpg", "png"], key="single_up_p")
                if up_p:
                    upload_prod_img = Image.open(up_p)
                    st.image(upload_prod_img, width=90)
            else:
                st.caption("Mode ini tidak memerlukan foto kemasan produk.")

    with tab_detail:
        prod_title = st.text_input(
            "Topik / Nama Produk",
            value=st.session_state.auto_brief["title"],
            placeholder="Contoh: Brightening Serum / Pewaris yang menyamar"
        )
        prod_benefits = st.text_area(
            "Poin Keunggulan / Inti Cerita",
            value=st.session_state.auto_brief["notes"],
            placeholder="Contoh: Cepat menyerap / Dipermalukan di pesta",
            height=65
        )

    with tab_kamera:
        col_t1, col_t2 = st.columns(2)
        with col_t1:
            voice_template = st.selectbox("Template Suara", [
                "UGC Kasual Curhat",
                "AI Influencer Trendy",
                "Podcast Dialog Alami",
                "Drama / Tegang",
                "Storyteller Reflektif",
                "Komedi / Sarkastik"
            ])
            clip_dur = st.selectbox("Durasi OmniFlow", ["4 detik", "6 detik", "8 detik", "10 detik"], index=2)
        with col_t2:
            cam_style = st.selectbox("Lensa Kamera", [
                "Smartphone 4K (Daylight)",
                "Mini-DV (Grainy Low-Contrast)",
                "C-Drama Contrast (Moody)",
                "Studio Podcast Warm",
                "Muted Cool Dawn / Fog"
            ])
            extra_flow = st.text_input("Aksi Kunci", value=st.session_state.auto_brief["action"], placeholder="Contoh: Kamera jatuh ke tanah")

    st.markdown("<div style='height: 4px;'></div>", unsafe_allow_html=True)
    generate_btn = st.button("🚀 Rancang Paket Produksi Lengkap", type="primary", use_container_width=True)

with col_right:
    st.markdown("**Hasil Storyboard & Prompt Siap Render**")
    if generate_btn:
        if not api_key:
            st.error("Masukkan Gemini API Key di sidebar.")
        elif not prod_title:
            st.warning("Isi topik atau klik tombol ⚡ Ide Otomatis.")
        else:
            client = genai.Client(api_key=api_key)
            prompt_text = f"""
            {SYSTEM_DIRECTOR_INSTRUCTION}

            Buatkan paket produksi lengkap untuk:
            - Mode: {mode}
            - Nama Produk/Topik: {prod_title}
            - Manfaat/Inti: {prod_benefits}
            - Ciri Karakter: {char_notes}
            - Profil Suara: {voice_template}
            - Kamera & Lighting: {cam_style}
            - Durasi OmniFlow: {clip_dur}
            - Aksi Kunci: {extra_flow}
            """
            
            # Susun payload input berbasis multimodal Interactions API
            input_payload = [{"type": "text", "text": prompt_text}]
            
            if active_char_img:
                input_payload.append(image_to_base64_part(active_char_img))
                prompt_text += "\n[Karakter]: Kunci detail visual wajah dan tubuh karakter dari gambar terlampir."
                
            if upload_prod_img:
                input_payload.append(image_to_base64_part(upload_prod_img))
                prompt_text += "\n[Produk]: Kunci kemasan produk fisik dari gambar terlampir."

            with st.spinner("Sutradara sedang menyusun paket naskah dan prompt..."):
                try:
                    interaction = client.interactions.create(
                        model=TARGET_MODEL,
                        input=input_payload
                    )
                    st.success("Paket produksi selesai!")
                    st.markdown(interaction.output_text)
                except Exception as e:
                    st.error(f"Terjadi kesalahan API: {str(e)}")
    else:
        st.info("Pilih mode, siapkan data singkat atau klik '⚡ Ide Otomatis', lalu klik tombol untuk memproses.")
