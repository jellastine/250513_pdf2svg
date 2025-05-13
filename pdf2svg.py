import streamlit as st
import fitz  # PyMuPDF
import os
import tempfile
import zipfile
import io

# --- 사용자 지정 비밀번호 설정 ---
PASSWORD = "1121"  # 원하는 비밀번호로 변경하세요

# 비밀번호 입력 UI
st.title("PDF to SVG Converter")
password_input = st.text_input("Enter password to access the app:", type="password")

# 비밀번호 검증
if password_input != PASSWORD:
    if password_input:
        st.error("Incorrect password. Access denied.")
    st.stop()

# 인증된 사용자만 이 아래의 기능을 사용 가능
st.markdown("Upload a PDF file, choose an output directory on the server, and download the resulting SVGs as a ZIP archive.")

uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])
output_dir = st.text_input("Output directory path (server-side)", "output_svgs")

if st.button("Convert to SVG"):
    if not uploaded_file:
        st.error("Please upload a PDF file before converting.")
    else:
        # Save uploaded PDF to a temporary file
        with tempfile.TemporaryDirectory() as tmpdir:
            temp_pdf_path = os.path.join(tmpdir, uploaded_file.name)
            with open(temp_pdf_path, 'wb') as tmp_file:
                tmp_file.write(uploaded_file.getbuffer())

            # Convert PDF to SVGs
            try:
                os.makedirs(output_dir, exist_ok=True)
                doc = fitz.open(temp_pdf_path)
                svg_paths = []
                for i in range(doc.page_count):
                    page = doc.load_page(i)
                    svg = page.get_svg_image()
                    filename = f"page_{i+1:03d}.svg"
                    file_path = os.path.join(output_dir, filename)
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(svg)
                    svg_paths.append(file_path)
                doc.close()
            except Exception as e:
                st.error(f"Conversion failed: {e}")
                st.stop()

            # Create ZIP archive in memory
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
                for path in svg_paths:
                    zipf.write(path, arcname=os.path.basename(path))
            zip_buffer.seek(0)

            st.success("Conversion complete!")
            st.download_button(
                label="Download SVGs as ZIP",
                data=zip_buffer,
                file_name="svgs.zip",
                mime="application/zip"
            )
