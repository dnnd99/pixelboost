import streamlit as st
from streamlit.components.v1 import html
from PIL import Image
import time
from datetime import datetime
import pandas as pd

from config import Config
from modules.upscaler import Upscaler
from modules.ai_vision import AIVision
from modules.metadata import MetadataProcessor
from modules.exporter import Exporter
from modules.logger import logger
from modules.utils import Utils

# Page Config
st.set_page_config(
    page_title="PixelBoost AI",
    page_icon="✦",
    layout="wide"
)

# Initialize session state
if 'processed' not in st.session_state:
    st.session_state.processed = 0
if 'metadata_generated' not in st.session_state:
    st.session_state.metadata_generated = 0
if 'upscale_click_count' not in st.session_state:
    st.session_state.upscale_click_count = 0

# Load CSS
with open('ui/styles.css', 'r') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Initialize components
upscaler = Upscaler()
ai_vision = AIVision(st.secrets.get("GEMINI_API_KEY", ""))
metadata_processor = MetadataProcessor()
exporter = Exporter()

# Header
col1, col2 = st.columns([3, 1])
with col1:
    st.markdown("### ✦ **PixelBoost AI** `v5.0`")
with col2:
    st.markdown("🟢 **Online**")

# Stats
c1, c2, c3, c4 = st.columns(4)
c1.metric("📊 Processed", st.session_state.processed)
c2.metric("🏷️ Metadata", st.session_state.metadata_generated)
c3.metric("📐 Max Res", "4K")
c4.metric("⬆️ Max Up", "8×")

st.divider()

# API Key
api_key = st.secrets.get("GEMINI_API_KEY", "")
if not api_key:
    api_key = st.text_input("🔑 Gemini API Key", type="password", placeholder="AIzaSy...")
    if api_key:
        ai_vision = AIVision(api_key)

st.divider()

# Settings
col1, col2, col3 = st.columns(3)
with col1:
    scale = st.slider("⬆️ Upscale", Config.MIN_SCALE, Config.MAX_SCALE, Config.DEFAULT_SCALE)
    format_type = st.selectbox("📁 Format", ["PNG", "JPEG"])
with col2:
    sharpen = st.checkbox("✦ Sharpen", value=Config.DEFAULT_SHARPEN)
    keyword_language = st.selectbox("🌐 Language", ["English", "Indonesian", "Spanish"])
with col3:
    max_keywords = st.slider("🏷️ Keywords", 10, Config.MAX_KEYWORDS, Config.DEFAULT_MAX_KEYWORDS)
    media_type = st.selectbox("📷 Media", ["Photo", "Illustration", "Vector"])

st.divider()

# Upload section
uploaded_files = st.file_uploader(
    "📤 Upload Images (JPG, PNG)",
    type=['jpg', 'jpeg', 'png'],
    accept_multiple_files=True,
    label_visibility="visible"
)

if uploaded_files:
    st.info(f"📄 **{len(uploaded_files)}** file(s) uploaded")
    
    # Thumbnails preview
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
    
    # Metadata Generation
    with st.expander("🤖 Generate Metadata", expanded=True):
        if st.button("🚀 Generate Metadata", use_container_width=True, type="primary"):
            if not ai_vision.is_available():
                st.error("❌ Enter API key first")
            else:
                with st.spinner("Generating metadata..."):
                    metadata_results = []
                    prog = st.progress(0)
                    
                    # Process in batches
                    batch_size = min(len(uploaded_files), Config.MAX_BATCH_SIZE)
                    for idx, file in enumerate(uploaded_files[:batch_size]):
                        result = ai_vision.generate_metadata(
                            file.name, 
                            media_type, 
                            keyword_language, 
                            max_keywords
                        )
                        if result and result.get('status') == 'success':
                            metadata_results.append(result)
                            st.session_state.metadata_generated += 1
                        prog.progress((idx + 1) / batch_size)
                        time.sleep(0.2)
                
                st.success(f"✅ {len(metadata_results)} files processed!")
                
                if metadata_results:
                    # Display results
                    df_data = []
                    for item in metadata_results:
                        df_data.append({
                            "File": item["filename"][:20],
                            "Title": (item.get("title", "")[:25] + "…") if len(item.get("title", "")) > 25 else item.get("title", ""),
                            "Category": item.get("category", ""),
                            "Status": "✅" if item.get("status") == "success" else "❌"
                        })
                    st.dataframe(pd.DataFrame(df_data), use_container_width=True)
                    
                    # Download CSV
                    csv_data = metadata_processor.create_adobe_csv(metadata_results)
                    st.download_button(
                        "⬇ Download CSV",
                        data=csv_data,
                        file_name=f"metadata_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
    
    st.divider()
    
    # Upscale section
    st.markdown("### 🚀 Upscale & Download")
    
    if st.button("⬆️ Upscale & Download", use_container_width=True, type="primary"):
        if st.session_state.upscale_click_count == 0:
            # First click - Open sponsor
            html(
                f"""<script>
                    window.open('{Config.SPONSOR_URL}', '_blank');
                </script>""",
                height=0,
            )
            st.session_state.upscale_click_count = 1
            st.info("✅ **Sponsor opened!** Click again to process your files.")
        else:
            # Second click - Process files
            with st.spinner(f"Processing {len(uploaded_files)} file(s)..."):
                images_data = []
                prog = st.progress(0)
                status = st.empty()
                
                # Process each file
                for idx, file in enumerate(uploaded_files):
                    status.caption(f"📄 {idx+1}/{len(uploaded_files)}: {file.name[:25]}")
                    
                    try:
                        img = Image.open(file)
                        
                        # Upscale
                        upscaled = upscaler.upscale_image(img, scale, sharpen)
                        
                        # Export
                        clean_name = Utils.clean_filename(file.name)
                        buf, ext = exporter.export_image(upscaled, format_type)
                        
                        if buf:
                            images_data.append({
                                'filename': f"{clean_name}_{scale}x{ext}",
                                'data': buf.getvalue()
                            })
                        
                    except Exception as e:
                        st.warning(f"⚠️ Error processing {file.name}: {str(e)[:50]}")
                    
                    prog.progress((idx + 1) / len(uploaded_files))
                
                # Create ZIP
                zip_buf, zip_name = Utils.create_zip_from_images(images_data)
                
                st.session_state.processed += len(uploaded_files)
                st.session_state.upscale_click_count = 0  # Reset for next batch
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
    
    # Click hint
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

# Footer
st.divider()
st.markdown(
    "<div style='text-align:center;color:#ffffff33;font-size:0.75rem;padding:1rem;'>"
    "Made with ✦ by Alley Production · 2026"
    "</div>",
    unsafe_allow_html=True
)
