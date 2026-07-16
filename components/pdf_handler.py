import io
import re
import streamlit as st
from PyPDF2 import PdfReader
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import simpleSplit


def handle_pdf_upload(key: str = "pdf_uploader"):
    """Handles PDF upload and returns extracted text."""
    uploaded_file = st.file_uploader("📚 Upload your study material (PDF)", type=["pdf"], key=key)
    pdf_text = ""

    if uploaded_file:
        with st.spinner("Extracting text from PDF..."):
            reader = PdfReader(uploaded_file)
            for page in reader.pages:
                pdf_text += page.extract_text() or ""
        st.success("✅ PDF processed successfully!")
        st.text_area("Extracted Text:", pdf_text[:2000], height=200)
    return pdf_text


def generate_pdf_from_text(text: str, title: str = "BrainDrain Notes") -> bytes:
    """Generate a multi-page PDF from plain/markdown text and return bytes."""
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    left_margin = 54
    right_margin = 54
    top_margin = 54
    bottom_margin = 54
    usable_width = width - left_margin - right_margin

    base_font = "Helvetica"
    base_size = 12
    line_height = 16

    def draw_header(page_num: int):
        c.setFont("Helvetica-Bold", 14)
        c.drawString(left_margin, height - top_margin + 6, title)
        c.setFont("Helvetica", 9)
        c.drawRightString(width - right_margin, height - top_margin + 6, f"Page {page_num}")
        c.setLineWidth(0.5)
        c.line(left_margin, height - top_margin, width - right_margin, height - top_margin)

    def new_page(page_num):
        c.showPage()
        draw_header(page_num)
        c.setFont(base_font, base_size)
        return height - top_margin - 24

    normalized = (text or "").replace("\t", "    ")
    lines = normalized.splitlines()
    if not lines:
        lines = [normalized]

    y = height - top_margin - 24
    page_num = 1
    draw_header(page_num)
    c.setFont(base_font, base_size)

    heading_re = re.compile(r"^(#{1,6})\s+(.*)$")
    bullet_re = re.compile(r"^(\s*)([-*•])\s+(.*)$")

    for raw_line in lines:
        line = raw_line.rstrip()

        if not line.strip():
            y -= 8
            if y <= bottom_margin:
                page_num += 1
                y = new_page(page_num)
            continue

        h_match = heading_re.match(line)
        if h_match:
            hashes, h_text = h_match.groups()
            level = len(hashes)
            size = {1: 26, 2: 22, 3: 18}.get(level, 16)

            y -= 12
            if y <= bottom_margin:
                page_num += 1
                y = new_page(page_num)
            c.setFont("Helvetica-Bold", size)
            wrapped = simpleSplit(h_text, "Helvetica-Bold", size, usable_width)
            for i, w in enumerate(wrapped):
                if y <= bottom_margin:
                    page_num += 1
                    y = new_page(page_num)
                    c.setFont("Helvetica-Bold", size)
                c.drawString(left_margin, y, w)
                y -= (size + 4 if i == 0 else size + 2)
            y -= 8
            c.setFont(base_font, base_size)
            continue

        b_match = bullet_re.match(line)
        if b_match:
            indent_spaces, _, b_text = b_match.groups()
            level = min(len(indent_spaces) // 2, 4)
            indent_offset = 22 + (level * 20)
            bullet_x = left_margin + indent_offset - 10
            text_x = left_margin + indent_offset
            max_width = usable_width - indent_offset

            wrapped = simpleSplit(b_text, base_font, base_size, max_width)
            for i, w in enumerate(wrapped):
                if y <= bottom_margin:
                    page_num += 1
                    y = new_page(page_num)
                    c.setFont(base_font, base_size)
                if i == 0:
                    c.setFont("Helvetica", base_size)
                    c.drawString(bullet_x, y, "•")
                c.drawString(text_x, y, w)
                y -= line_height
            y -= 6
            continue

        wrapped = simpleSplit(line, base_font, base_size, usable_width)
        for w in wrapped:
            if y <= bottom_margin:
                page_num += 1
                y = new_page(page_num)
                c.setFont(base_font, base_size)
            c.drawString(left_margin, y, w)
            y -= line_height
        y -= 8

    c.save()
    buffer.seek(0)
    return buffer.getvalue()