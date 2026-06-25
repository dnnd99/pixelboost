import streamlit as st
import streamlit.components.v1 as components
from PIL import Image, ImageFilter
import io
import zipfile
import re
import json
import csv
import time
from datetime import datetime
import pandas as pd
import google.generativeai as genai

# ============ PAGE CONFIG ============
st.set_page_config(
    page_title="PixelBoost AI",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============ SESSION STATE ============
if 'processed' not in st.session_state:
    st.session_state.processed = 0
if 'metadata_generated' not in st.session_state:
    st.session_state.metadata_generated = 0
if 'sponsor_clicked' not in st.session_state:
    st.session_state.sponsor_clicked = False
if 'show_modal' not in st.session_state:
    st.session_state.show_modal = False
if 'api_key' not in st.session_state:
    st.session_state.api_key = ""

# ============ CSS RINGAN + MODAL ============
st.markdown("""
<style>
    /* ── RESET ── */
    .main > div { padding: 0.5rem !important; max-width: 100% !important; }
    .stApp { background: #07070e; font-family: -apple-system, BlinkMacSystemFont, sans-serif; }
    #MainMenu, footer, .stDeployButton { display: none !important; }
    
    /* ── BUTTONS ── */
    .stButton > button {
        width: 100% !important;
        min-height: 44px !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        transition: all 0.2s ease !important;
        font-size: 0.9rem !important;
    }
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #6d6aff, #8b7ff7) !important;
        color: white !important;
        box-shadow: 0 4px 16px #6d6aff44 !important;
    }
    .stButton > button[kind="primary"]:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 24px #6d6aff66 !important;
    }
    .stButton > button[kind="primary"]:active {
        transform: translateY(0) !important;
    }
    
    /* ── INPUTS ── */
    .stTextInput > div > div > input {
        background: #161628 !important;
        border: 1px solid #ffffff12 !important;
        border-radius: 10px !important;
        color: #e2e2ff !important;
        padding: 0.5rem 0.75rem !important;
        min-height: 40px !important;
    }
    .stTextInput > div > div > input:focus {
        border-color: #6d6aff66 !important;
        box-shadow: 0 0 0 3px #6d6aff18 !important;
    }
    .stSelectbox > div > div {
        background: #161628 !important;
        border: 1px solid #ffffff12 !important;
        border-radius: 10px !important;
        color: #e2e2ff !important;
        min-height: 40px !important;
    }
    
    /* ── SLIDER ── */
    .stSlider > div > div > div {
        background: linear-gradient(90deg, #6d6aff, #a78bfa) !important;
    }
    .stSlider > div > div > div > div {
        background: #ffffff !important;
        border: 2px solid #6d6aff !important;
        box-shadow: 0 0 8px #6d6aff66 !important;
        width: 18px !important;
        height: 18px !important;
    }
    
    /* ── FILE UPLOADER ── */
    [data-testid="stFileUploader"] > div {
        background: #0f0f1a !important;
        border: 2px dashed #ffffff12 !important;
        border-radius: 12px !important;
        padding: 1.5rem 1rem !important;
        transition: border-color 0.2s !important;
    }
    [data-testid="stFileUploader"] > div:hover {
        border-color: #6d6aff55 !important;
        background: #12102a !important;
    }
    
    /* ── ALERTS ── */
    .stSuccess > div {
        background: #052013 !important;
        border: 1px solid #22c55e33 !important;
        color: #4ade80 !important;
        border-radius: 10px !important;
        padding: 0.75rem !important;
    }
    .stError > div {
        background: #1a0505 !important;
        border: 1px solid #ef444433 !important;
        color: #f87171 !important;
        border-radius: 10px !important;
        padding: 0.75rem !important;
    }
    .stInfo > div {
        background: #050f2a !important;
        border: 1px solid #6d6aff33 !important;
        color: #a78bfa !important;
        border-radius: 10px !important;
        padding: 0.75rem !important;
    }
    
    /* ── EXPANDER ── */
    [data-testid="stExpander"] {
        border: 1px solid #ffffff0a !important;
        border-radius: 10px !important;
        background: #0f0f1a !important;
    }
    [data-testid="stExpander"] summary {
        color: #ffffff55 !important;
        font-weight: 600 !important;
    }
    
    /* ── METRIC ── */
    [data-testid="stMetricValue"] {
        color: #e2e2ff !important;
        font-weight: 700 !important;
    }
    [data-testid="stMetricLabel"] {
        color: #ffffff44 !important;
        font-size: 0.7rem !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
    }
    
    /* ── DATAFRAME ── */
    [data-testid="stDataFrame"] {
        border: 1px solid #ffffff0a !important;
        border-radius: 10px !important;
        overflow: auto !important;
    }
    [data-testid="stDataFrame"] table {
        font-size: 0.75rem !important;
    }
    
    /* ── HINT ── */
    .hint-box {
        padding: 0.5rem 0.75rem;
        background: #6d6aff0d;
        border: 1px solid #6d6aff22;
        border-radius: 8px;
        font-size: 0.85rem;
        color: #ffffff66;
        text-align: center;
        margin-top: 0.5rem;
        line-height: 1.5;
    }
    .hint-box strong {
        color: #a78bfa;
        font-weight: 600;
    }
    
    /* ── MOBILE ── */
    @media (max-width: 768px) {
        .stColumns { flex-wrap: wrap !important; }
        [data-testid="column"] { min-width: 100% !important; }
        .stButton > button { font-size: 0.8rem !important; min-height: 40px !important; }
    }
    @media (max-width: 480px) {
        .main > div { padding: 0.25rem !important; }
        [data-testid="stMetricValue"] { font-size: 1.2rem !important; }
    }
    
    /* ── MODAL ── */
    .modal-overlay {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.85);
        backdrop-filter: blur(8px);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 999999;
        padding: 1rem;
        animation: fadeIn 0.3s ease;
    }
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    @keyframes slideUp {
        from { transform: translateY(30px); opacity: 0; }
        to { transform: translateY(0); opacity: 1; }
    }
    .modal-content {
        background: linear-gradient(145deg, #0f0f1a, #1a1a2e);
        border: 1px solid #6d6aff44;
        border-radius: 20px;
        padding: 2rem 1.5rem;
        max-width: 480px;
        width: 100%;
        text-align: center;
        animation: slideUp 0.4s ease;
        box-shadow: 0 25px 60px rgba(0, 0, 0, 0.8);
        position: relative;
    }
    .modal-icon { font-size: 3rem; margin-bottom: 0.5rem; display: block; }
    .modal-title {
        font-size: 1.3rem;
        font-weight: 700;
        color: #e2e2ff;
        margin-bottom: 0.5rem;
    }
    .modal-sub {
        font-size: 0.9rem;
        color: #ffffff77;
        margin-bottom: 1.5rem;
        line-height: 1.6;
    }
    .modal-sub strong { color: #a78bfa; }
    .modal-sponsor-btn {
        display: inline-block;
        background: linear-gradient(135deg, #6d6aff, #8b7ff7);
        color: white !important;
        padding: 0.8rem 2rem;
        border-radius: 12px;
        text-decoration: none;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 20px #6d6aff44;
        width: 100%;
        border: none;
        cursor: pointer;
        font-family: inherit;
    }
    .modal-sponsor-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 30px #6d6aff66;
    }
    .modal-sponsor-btn:active { transform: translateY(0); }
    .modal-divider {
        height: 1px;
        background: linear-gradient(90deg, transparent, #6d6aff44, transparent);
        margin: 1.5rem 0;
    }
    .modal-footer {
        display: flex;
        gap: 0.75rem;
        margin-top: 0.5rem;
    }
    .modal-footer button {
        flex: 1;
        padding: 0.6rem;
        border-radius: 10px;
        border: 1px solid #ffffff12;
        background: transparent;
        color: #ffffff77;
        font-weight: 500;
        font-size: 0.85rem;
        cursor: pointer;
        transition: all 0.2s ease;
        font-family: inherit;
    }
    .modal-footer button:hover {
        background: #ffffff08;
        color: #ffffff;
        border-color: #ffffff22;
    }
    .modal-footer button.primary-btn {
        background: #6d6aff22;
        border-color: #6d6aff44;
        color: #a78bfa;
    }
    .modal-footer button.primary-btn:hover {
        background: #6d6aff33;
        border-color: #6d6aff66;
    }
    .modal-footer button.primary-btn.active {
        background: #22c55e33;
        border-color: #22c55e66;
        color: #4ade80;
    }
    @media (max-width: 480px) {
        .modal-content { padding: 1.5rem 1rem; }
        .modal-title { font-size: 1.1rem; }
        .modal-sub { font-size: 0.8rem; }
        .modal-sponsor-btn { font-size: 0.9rem; padding: 0.7rem 1.5rem; }
        .modal-footer button { font-size: 0.75rem; padding: 0.5rem; }
    }
</style>
""", unsafe_allow_html=True)

# ============ HEADER ============
col1, col2 = st.columns([3, 1])
with col1:
    st.markdown("### ✦ **PixelBoost AI** `v5.0`")
with col2:
    st.markdown("🟢 **Online**")

st.divider()

# ============ STATS ============
c1, c2, c3, c4 = st.columns(4)
c1.metric("📊 Processed", st.session_state.processed)
c2.metric("🏷️ Metadata", st.session_state.metadata_generated)
c3.metric("📐 Max Res", "4K")
c4.metric("⬆️ Max Up", "8×")

st.divider()

# ============ API KEY ============
with st.expander("🔑 API Configuration", expanded=False):
    api_key = st.secrets.get("GEMINI_API_KEY", "")
    if not api_key:
        api_key = st.text_input(
            "Gemini API Key",
            type="password",
            value=st.session_state.api_key,
            placeholder="AIzaSy...",
            label_visibility="visible"
        )
        if api_key:
            st.session_state.api_key = api_key
            genai.configure(api_key=api_key)
            st.success("✅ API key configured")
    else:
        st.success("✅ API key loaded from secrets")
        genai.configure(api_key=api_key)

st.divider()

# ============ SETTINGS ============
st.markdown("### ⚙️ Settings")
col1, col2, col3 = st.columns(3)
with col1:
    scale = st.slider("⬆️ Upscale", 2, 8, 4, help="Upscale factor (2x - 8x)")
    format_type = st.selectbox("📁 Format", ["PNG", "JPEG"])
with col2:
    sharpen = st.checkbox("✦ Sharpen", value=True, help="Apply sharpening filter")
    keyword_language = st.selectbox(
        "🌐 Language",
        ["English", "Indonesian", "Spanish", "French", "German", "Japanese", "Chinese", "Arabic"]
    )
with col3:
    max_keywords = st.slider("🏷️ Keywords", 10, 50, 30, step=5)
    media_type = st.selectbox("📷 Media", ["Photo", "Illustration", "Vector", "3D Render"])

st.divider()

# ============ CATEGORY MAP ============
CATEGORY_MAP = {
    "Abstract": "1", "Animals/Wildlife": "2", "Arts/Entertainment": "3",
    "Backgrounds/Textures": "4", "Beauty/Fashion": "5", "Buildings/Landmarks": "6",
    "Business/Finance": "7", "Education": "8", "Food/Drink": "9",
    "Healthcare/Medical": "10", "Holidays": "11", "Industrial": "12",
    "Landscapes": "13", "Lifestyle": "14", "Nature": "15",
    "Objects": "16", "People": "17", "Religion": "18",
    "Science": "19", "Sports/Recreation": "20", "Technology": "21",
    "Transportation": "22", "Travel": "23"
}

# ============ HELPERS ============
def clean_filename(name):
    name = re.sub(r'[^a-z0-9\-]', '-', name.lower())
    name = re.sub(r'-+', '-', name).strip('-')
    return name[:80]

def generate_metadata(filename, api_key, media_type, keyword_language, max_keywords=30):
    if not api_key:
        return None
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.0-flash-lite")
        lang = keyword_language
        prompt = f"""You are an Adobe Stock SEO expert. Based on filename: "{filename}"
Generate COMPLETE metadata in JSON format only, no explanation:
{{
  "title": "descriptive title max 70 chars, SEO-friendly",
  "description": "compelling description max 150 chars",
  "keywords": [{max_keywords} relevant keywords in {lang}, mix of broad and specific terms],
  "category": "one of: Abstract, Animals/Wildlife, Arts/Entertainment, Backgrounds/Textures, Beauty/Fashion, Buildings/Landmarks, Business/Finance, Education, Food/Drink, Healthcare/Medical, Holidays, Industrial, Landscapes, Lifestyle, Nature, Objects, People, Religion, Science, Sports/Recreation, Technology, Transportation, Travel",
  "alt_text": "descriptive alt text max 100 chars",
  "suggested_usage": ["3-5 suggested use cases"]
}}"""
        response = model.generate_content(prompt)
        text = re.sub(r'```json|```', '', response.text.strip())
        data = json.loads(text)
        return {
            "filename": filename,
            "media_type": media_type,
            "title": data.get("title", ""),
            "description": data.get("description", ""),
            "keywords": data.get("keywords", []),
            "category": data.get("category", "Abstract"),
            "alt_text": data.get("alt_text", ""),
            "suggested_usage": ", ".join(data.get("suggested_usage", [])),
            "language": keyword_language,
            "status": "success"
        }
    except Exception as e:
        return {
            "filename": filename,
            "media_type": media_type,
            "title": "",
            "description": "",
            "keywords": [],
            "category": "Abstract",
            "alt_text": "",
            "suggested_usage": "",
            "language": keyword_language,
            "status": f"error: {str(e)[:50]}"
        }

def create_adobe_csv(metadata_results):
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Filename", "Title", "Keywords", "Category", "Releases"])
    for item in metadata_results:
        code = CATEGORY_MAP.get(item.get("category", "Abstract"), "1")
        kw = item.get("keywords", [])
        kw_str = ", ".join(kw[:49]) if isinstance(kw, list) else str(kw)
        writer.writerow([
            item.get("filename", ""),
            item.get("title", "")[:200],
            kw_str,
            code,
            ""
        ])
    return output.getvalue()

# ============ UPLOAD ============
st.markdown("### 📤 Upload Files")
uploaded_files = st.file_uploader(
    "Drop images here — JPG, PNG",
    type=['jpg', 'jpeg', 'png'],
    accept_multiple_files=True,
    label_visibility="collapsed"
)

# ============ MAIN CONTENT ============
if uploaded_files:
    st.success(f"📄 **{len(uploaded_files)}** file(s) uploaded")
    
    # Preview thumbnails
    preview_cols = st.columns(min(4, len(uploaded_files)))
    for idx, file in enumerate(uploaded_files[:4]):
        with preview_cols[idx % 4]:
            try:
                img = Image.open(file)
                img.thumbnail((100, 100))
                st.image(img, use_column_width=True)
                st.caption(file.name[:15] + ("..." if len(file.name) > 15 else ""))
            except:
                st.markdown(f"📄 {file.name[:10]}")
    
    if len(uploaded_files) > 4:
        st.caption(f"+ {len(uploaded_files) - 4} more")
    
    st.divider()
    
    # ===== METADATA =====
    with st.expander("🤖 Generate Metadata", expanded=True):
        if st.button("🚀 Generate Metadata", use_container_width=True, type="primary"):
            if not api_key:
                st.error("❌ Please enter Gemini API key first")
            else:
                with st.spinner(f"Generating metadata for {min(len(uploaded_files), 20)} files..."):
                    metadata_results = []
                    prog = st.progress(0)
                    for idx, file in enumerate(uploaded_files[:20]):  # Max 20 files
                        result = generate_metadata(
                            file.name,
                            api_key,
                            media_type,
                            keyword_language,
                            max_keywords
                        )
                        if result:
                            metadata_results.append(result)
                            st.session_state.metadata_generated += 1
                        prog.progress((idx + 1) / min(len(uploaded_files), 20))
                        time.sleep(0.15)
                
                st.success(f"✅ {len(metadata_results)} files processed!")
                
                # Show results
                if metadata_results:
                    df_data = []
                    for item in metadata_results:
                        title = item.get("title", "")
                        df_data.append({
                            "File": item["filename"][:25],
                            "Title": (title[:30] + "…") if len(title) > 30 else title,
                            "Category": item.get("category", ""),
                            "Status": "✅" if item.get("status") == "success" else "❌"
                        })
                    st.dataframe(pd.DataFrame(df_data), use_container_width=True)
                    
                    # Download button
                    csv_data = create_adobe_csv(metadata_results)
                    st.download_button(
                        "⬇ Download Adobe CSV",
                        data=csv_data,
                        file_name=f"metadata_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
    
    st.divider()
    
    # ===== UPSCALE =====
    st.markdown("### 🚀 Upscale & Download")
    
    # ── UPSACLE BUTTON ──
    if st.button("⬆️ Upscale & Download", use_container_width=True, type="primary"):
        if not st.session_state.sponsor_clicked:
            # Tampilkan modal
            st.session_state.show_modal = True
            st.rerun()
        else:
            # Proses langsung
            with st.spinner(f"Processing {len(uploaded_files)} file(s)..."):
                zip_buf = io.BytesIO()
                zip_name = f"pixelboost_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
                prog = st.progress(0)
                status = st.empty()
                
                with zipfile.ZipFile(zip_buf, 'w', zipfile.ZIP_DEFLATED) as zf:
                    for idx, file in enumerate(uploaded_files):
                        status.caption(f"📄 {idx+1}/{len(uploaded_files)}: {file.name[:25]}")
                        clean_name = clean_filename(os.path.splitext(file.name)[0])
                        
                        try:
                            img = Image.open(file)
                            # Upscale
                            img = img.resize(
                                (int(img.width * scale), int(img.height * scale)),
                                Image.Resampling.LANCZOS
                            )
                            # Sharpen
                            if sharpen:
                                img = img.filter(ImageFilter.UnsharpMask(radius=2, percent=150, threshold=3))
                            # Convert to RGB
                            if img.mode in ('RGBA', 'LA', 'P'):
                                img = img.convert('RGB')
                            # Save
                            buf = io.BytesIO()
                            if format_type == "PNG":
                                img.save(buf, format='PNG', optimize=True, compress_level=6)
                                ext = ".png"
                            else:
                                img.save(buf, format='JPEG', quality=90, optimize=True)
                                ext = ".jpg"
                            zf.writestr(f"{clean_name}_{scale}x{ext}", buf.getvalue())
                        except Exception as e:
                            st.warning(f"⚠️ Error: {file.name} - {str(e)[:40]}")
                        
                        prog.progress((idx + 1) / len(uploaded_files))
                
                zip_buf.seek(0)
                st.session_state.processed += len(uploaded_files)
                st.session_state.sponsor_clicked = False  # Reset
                status.empty()
                
                st.success(f"✅ {len(uploaded_files)} files processed!")
                mb = len(zip_buf.getvalue()) / (1024 * 1024)
                st.download_button(
                    f"⬇ Download ZIP ({mb:.1f} MB)",
                    data=zip_buf.getvalue(),
                    file_name=zip_name,
                    mime="application/zip",
                    use_container_width=True,
                    type="primary"
                )
    
    # ── HINT ──
    if st.session_state.sponsor_clicked:
        st.success("✅ Sponsor confirmed! Click **Upscale & Download** again to process.")
    else:
        st.markdown("""
        <div class="hint-box">
            Click <strong>Upscale & Download</strong> → sponsor modal appears → open sponsor → click again to process
        </div>
        """, unsafe_allow_html=True)

# ============ MODAL SPONSOR ============
if st.session_state.show_modal:
    st.markdown("""
    <div class="modal-overlay" id="modalOverlay">
        <div class="modal-content">
            <span class="modal-icon">🎯</span>
            <div class="modal-title">Support Us!</div>
            <div class="modal-sub">
                Please open our sponsor to continue.<br>
                <strong>Click the button below</strong> (opens in new tab)
            </div>
            
            <button class="modal-sponsor-btn" onclick="openSponsor()">
                🚀 Open Sponsor
            </button>
            
            <div class="modal-divider"></div>
            
            <div class="modal-footer">
                <button onclick="closeModal()">✕ Cancel</button>
                <button class="primary-btn" id="continueBtn" onclick="confirmSponsor()">
                    ✅ I've Opened It
                </button>
            </div>
        </div>
    </div>
    
    <script>
        function openSponsor() {
            window.open(
                'https://www.effectivecpmnetwork.com/hetg54us4?key=052b147073a8a1411c3b8815ecc9fa2e',
                '_blank'
            );
            var btn = document.getElementById('continueBtn');
            btn.classList.add('active');
            btn.innerHTML = '✅ Opened! Click to confirm';
        }
        
        function closeModal() {
            var overlay = document.getElementById('modalOverlay');
            if (overlay) overlay.style.display = 'none';
        }
        
        function confirmSponsor() {
            fetch('/_stcore/stream/update', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    key: 'sponsor_clicked',
                    value: true
                })
            }).catch(() => {});
            
            var btn = document.getElementById('continueBtn');
            btn.innerHTML = '✅ Confirmed!';
            btn.style.background = '#22c55e33';
            btn.style.borderColor = '#22c55e66';
            
            setTimeout(function() {
                closeModal();
                window.location.reload();
            }, 500);
        }
        
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape') closeModal();
        });
    </script>
    """, unsafe_allow_html=True)
    
    # Set flag setelah modal ditutup
    if st.session_state.show_modal:
        st.session_state.show_modal = False
        st.rerun()

# ============ FOOTER ============
st.divider()
st.markdown(
    """
    <div style="text-align:center;color:#ffffff22;font-size:0.7rem;padding:1rem 0.5rem;">
        Made with ✦ by Alley Production · 2026
    </div>
    """,
    unsafe_allow_html=True
)
