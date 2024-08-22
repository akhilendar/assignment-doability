import os
import gdown
import streamlit as st
from PyPDF2 import PdfReader
import docx
import pytesseract
from PIL import Image
import re


def download_curriculum():
    curriculum_dir = "curriculum_files"
    os.makedirs(curriculum_dir, exist_ok=True)
    drive_links = {
        "fundamentals": "https://drive.google.com/uc?id=18kk_ByuHkwD9elQLkYasOPC6edLplIV4",
        "mern_fullstack": "https://drive.google.com/uc?id=1zomgxelkRYbnG1eT-iJdUcVAS_oaGsFY",
        "data_analytics": "https://drive.google.com/uc?id=1YCdnPkIZzXufN3qF9KQQTL5lbD6wxdVG",
        "java_fullstack": "https://drive.google.com/uc?id=1xv6LplsAOAfJ_824LVepIfIPMbZmk249",
        "qa_testing": "https://drive.google.com/uc?id=18-PWgg4tMlnU6o6dOMmb5nL2n48cC6mr",
    }

    curriculum_files = {}
    for name, url in drive_links.items():
        output = os.path.join(curriculum_dir, f"{name}.pdf")
        if not os.path.exists(output) or os.path.getsize(output) == 0:
            if os.path.exists(output):
                os.remove(output)
            gdown.download(url, output, quiet=False)
        try:
            with open(output, "rb") as f:
                PdfReader(f)
            curriculum_files[name] = output
        except Exception as e:
            st.error(
                f"Failed to download or verify the file: {output}. Error: {e}")
            return None
    return curriculum_files


def extract_text_from_pdf(file_path):
    try:
        reader = PdfReader(file_path)
        text = " ".join(page.extract_text()
                        for page in reader.pages if page.extract_text())
        return normalize_text(text)
    except Exception as e:
        st.error(f"Error reading PDF file {file_path}: {e}")
        return ""


def extract_text_from_doc(file_path):
    try:
        doc = docx.Document(file_path)
        text = "\n".join(para.text for para in doc.paragraphs)
        return normalize_text(text)
    except Exception as e:
        st.error(f"Error reading DOC file {file_path}: {e}")
        return ""


def extract_text_from_image(file_path):
    try:
        img = Image.open(file_path)
        text = pytesseract.image_to_string(img)
        return normalize_text(text)
    except Exception as e:
        st.error(f"Error processing image file {file_path}: {e}")
        return ""


def normalize_text(text):
    # Lowercase, remove non-alphanumeric characters
    return re.sub(r'\W+', ' ', text.lower())


def calculate_doability(content, curriculum):
    content_words = content.split()
    curriculum_words = set(curriculum.split())
    match_count = sum(1 for word in content_words if word in curriculum_words)
    return (match_count / len(content_words)) * 100 if content_words else 0


def main():
    st.title("Assignment Do-ability Checker")
    curriculum_files = download_curriculum()
    if not curriculum_files:
        st.error("Failed to load curriculum files.")
        return

    uploaded_file = st.file_uploader("Please upload your assignment document", type=[
                                     "pdf", "docx", "doc", "png", "jpg", "jpeg"])
    if uploaded_file:
        file_type = uploaded_file.type
        content = ""
        if file_type == "application/pdf":
            content = extract_text_from_pdf(uploaded_file)
        elif file_type in ["application/vnd.openxmlformats-officedocument.wordprocessingml.document", "application/msword"]:
            content = extract_text_from_doc(uploaded_file)
        elif file_type in ["image/png", "image/jpeg"]:
            content = extract_text_from_image(uploaded_file)
        else:
            st.error("Unsupported file type.")
            return

        curriculum = " ".join(extract_text_from_pdf(f)
                              for f in curriculum_files.values())
        doability = calculate_doability(content, curriculum)
        st.write(f"{doability:.2f}% Doable")


if __name__ == "__main__":
    main()
