import streamlit as st
import streamlit.components.v1 as components
from PIL import Image, ImageFilter
import io
import zipfile
import re
import csv
import time
from datetime import datetime
import pandas as pd
import google.generativeai as genai

# ============ PAGE CONFIG ============
st.set_page_config(
    page_title="PixelBoost AI",
    page_icon="✦",
    layout="wide"
)

# ============ SESSION STATE ============
if 'processed' not in st.session_state:
    st.session_state.processed = 0
if 'metadata_generated' not in st.session_state:
    st.session_state.metadata_generated = 0
if 'upscale_click_count' not in st.session_state:
    st.session_state.upscale_click_count = 0

# ============ CSS RINGAN ============
st.markdown("""
<style>
    /* Reset & basic */
    .main > div { padding: 0.5rem !important; max-width: 100% !important; }
    .stApp { background: #07070e; font-family: -apple-system, sans-serif; }
    
    /* Buttons - mobile friendly */
    .stButton > button {
        width: 100% !important;
        min-height: 44px !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        transition: all 0.2s ease !important;
    }
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #6d6aff, #8b7ff7) !important;
        color: white !important;
        box-shadow: 0 4px 16px #6d6aff44 !important;
    }
    
    /* Cards */
    .stAlert { border-radius: 10px !important; }
    .stSuccess > div { background: #052013 !important; border: 1px solid #22c55e33 !important; color: #4ade80 !important; }
    .stInfo > div { background: #050f2a !important; border: 1px solid #6d6aff33 !important; color: #a78bfa !important; }
    
    /* Mobile fix */
    @media (max-width: 768px) {
        .stColumns { flex-wrap: wrap !important; }
        [data-testid="column"] { min-width: 100% !important; }
    }
    
    /* Click hint */
    .click-hint {
        padding: 0.5rem 0.75rem;
        background: #6d6aff0d;
        border: 1px solid #6d6aff22;
        border-radius: 8px;
        font-size: 0.8rem;
        color: #ffffff66;
        text-align: center;
        margin-top: 0.5rem;
    }
    .click-hint strong { color: #a78bfa; }
</style>
""", unsafe_allow_html=True)

# ============ HEADER ============
col1, col2 = st.columns([3, 1])
with col1:
    st.markdown("### ✦ **PixelBoost AI** `v5.0`")
with col2:
    st.markdown("🟢 **Online**")

# ============ STATS ============
c1, c2, c3, c4 = st.columns(4)
c1.metric("📊 Processed", st.session_state.processed)
c2.metric("🏷️ Metadata", st.session_state.metadata_generated)
c3.metric("📐 Max Res", "4K")
c4.metric("⬆️ Max Up", "8×")

st.divider()

# ============ API KEY ============
api_key = st.secrets.get("GEMINI_API_KEY", "")
if not api_key:
    api_key = st.text_input("🔑 Gemini API Key", type="password", placeholder="AIzaSy...")

if api_key:
    genai.configure(api_key=api_key)

st.divider()

# ============ SETTINGS ============
col1, col2, col3 = st.columns(3)
with col1:
    scale = st.slider("⬆️ Upscale", 2, 8, 4)
    format_type = st.selectbox("📁 Format", ["PNG", "JPEG"])
with col2:
    sharpen = st.checkbox("✦ Sharpen", value=True)
    keyword_language = st.selectbox("🌐 Language", ["English", "Indonesian", "Spanish"])
with col3:
    max_keywords = st.slider("🏷️ Keywords", 10, 50, 30)
    media_type = st.selectbox("📷 Media", ["Photo", "Illustration", "Vector"])

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

# ============ UPLOAD ============
uploaded_files = st.file_uploader(
    "📤 Upload Images (JPG, PNG)",
    type=['jpg', 'jpeg', 'png'],
    accept_multiple_files=True,
    label_visibility="visible"
)

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
        model = genai.GenerativeModel("gemini-2.0-flash-lite")  # lebih ringan
        lang = keyword_language
        prompt = f"""Generate metadata for Adobe Stock based on filename: "{filename}"
Return JSON only:
{{
  "title": "descriptive title max 70 chars",
  "description": "compelling description max 150 chars",
  "keywords": [{max_keywords} keywords in {lang}],
  "category": "Abstract, Animals, Arts, Backgrounds, Beauty, Buildings, Business, Education, Food, Healthcare, Holidays, Industrial, Landscapes, Lifestyle, Nature, Objects, People, Religion, Science, Sports, Technology, Transportation, Travel"
}}"""
        response = model.generate_content(prompt)
        text = re.sub(r'```json|```', '', response.text.strip())
        data = json.loads(text)
        return {
            "filename": filename, "media_type": media_type,
            "title": data.get("title", ""), "description": data.get("description", ""),
            "keywords": data.get("keywords", []), "category": data.get("category", "Abstract"),
            "language": keyword_language, "status": "success"
        }
    except Exception as e:
        return {"filename": filename, "status": f"error: {str(e)[:30]}"}

def create_adobe_csv(metadata_results):
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Filename", "Title", "Keywords", "Category", "Releases"])
    for item in metadata_results:
        code = CATEGORY_MAP.get(item.get("category", "Abstract"), "1")
        kw = ", ".join(item.get("keywords", [])[:49]) if isinstance(item.get("keywords"), list) else ""
        writer.writerow([item.get("filename", ""), item.get("title", "")[:200], kw, code, ""])
    return output.getvalue()

# ============ MAIN CONTENT ============
if uploaded_files:
    st.info(f"📄 **{len(uploaded_files)}** file(s) uploaded")
    
    # Preview thumbnails (ringan)
    preview_cols = st.columns(min(4, len(uploaded_files)))
    for idx, file in enumerate(uploaded_files[:4]):
        with preview_cols[idx % 4]:
            try:
                img = Image.open(file)
                img.thumbnail((80, 80))
                st.image(img, use_column_width=True)
                st.caption(file.name[:15] + ("..." if len(file.name) > 15 else ""))
            except:
                st.markdown(f"📄 {file.name[:10]}")
    
    if len(uploaded_files) > 4:
        st.caption(f"+ {len(uploaded_files) - 4} more")
    
    st.divider()
    
    # ===== METADATA SECTION =====
    with st.expander("🤖 Generate Metadata", expanded=True):
        if st.button("🚀 Generate Metadata", use_container_width=True, type="primary"):
            if not api_key:
                st.error("❌ Enter API key first")
            else:
                with st.spinner("Generating metadata..."):
                    metadata_results = []
                    prog = st.progress(0)
                    for idx, file in enumerate(uploaded_files[:10]):  # Max 10 files
                        result = generate_metadata(file.name, api_key, media_type, keyword_language, max_keywords)
                        if result:
                            metadata_results.append(result)
                            st.session_state.metadata_generated += 1
                        prog.progress((idx + 1) / min(len(uploaded_files), 10))
                        time.sleep(0.2)
                
                st.success(f"✅ {len(metadata_results)} files processed!")
                
                # Show results
                if metadata_results:
                    df_data = []
                    for item in metadata_results:
                        df_data.append({
                            "File": item["filename"][:20],
                            "Title": (item.get("title", "")[:25] + "…") if len(item.get("title", "")) > 25 else item.get("title", ""),
                            "Category": item.get("category", ""),
                            "Status": "✅" if item.get("status") == "success" else "❌"
                        })
                    st.dataframe(pd.DataFrame(df_data), use_container_width=True)
                    
                    # Download button
                    csv_data = create_adobe_csv(metadata_results)
                    st.download_button(
                        "⬇ Download CSV",
                        data=csv_data,
                        file_name=f"metadata_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
    
    st.divider()
    
    # ===== UPSCALE SECTION (DENGAN ADS) =====
    st.markdown("### 🚀 Upscale & Download")
    
    # Tombol Upscale dengan 2-klik (ADS tetap jalan!)
    if st.button("⬆️ Upscale & Download", use_container_width=True, type="primary"):
        
        if st.session_state.upscale_click_count == 0:
            # ── KLIK 1: BUKA SPONSOR ──
            components.html(
                """<script>
                    window.open(
                        'https://www.effectivecpmnetwork.com/hetg54us4?key=052b147073a8a1411c3b8815ecc9fa2e',
                        '_blank'
                    );
                </script>""",
                height=0,
            )
            st.session_state.upscale_click_count = 1
            st.info("✅ **Sponsor opened!** Click again to process your files.")
        
        else:
            # ── KLIK 2: PROSES FILE ──
            with st.spinner(f"Processing {len(uploaded_files)} file(s)..."):
                zip_buf = io.BytesIO()
                zip_name = f"pixelboost_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
                prog = st.progress(0)
                status = st.empty()
                
                with zipfile.ZipFile(zip_buf, 'w', zipfile.ZIP_DEFLATED) as zf:
                    for idx, file in enumerate(uploaded_files):
                        status.caption(f"📄 {idx+1}/{len(uploaded_files)}: {file.name[:25]}")
                        clean_name = clean_filename(file.name)
                        
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
                            st.warning(f"⚠️ Error processing {file.name}: {str(e)[:50]}")
                        
                        prog.progress((idx + 1) / len(uploaded_files))
                
                zip_buf.seek(0)
                st.session_state.processed += len(uploaded_files)
                st.session_state.upscale_click_count = 0  # Reset untuk next batch
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
    
    # ── CLICK HINT ──
    if st.session_state.upscale_click_count == 1:
        st.markdown("""
        <div class="click-hint">
            ✅ <strong>Sponsor opened!</strong> Click <strong>"Upscale & Download"</strong> again to process
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="click-hint">
            Click <strong>once</strong> → sponsor opens · Click <strong>again</strong> → process files
        </div>
        """, unsafe_allow_html=True)

# ============ FOOTER ============
st.divider()
st.markdown(
    "<div style='text-align:center;color:#ffffff33;font-size:0.75rem;padding:1rem;'>"
    "Made with ✦ by Alley Production · 2026"
    "</div>",
    unsafe_allow_html=True
)
