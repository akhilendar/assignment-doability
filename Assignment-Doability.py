import os
import gdown
import streamlit as st
from PyPDF2 import PdfReader
import docx
import pytesseract
from PIL import Image

# Function to download the curriculum files


def download_curriculum():
    curriculum_dir = "curriculum_files"
    # Create the directory if it doesn't exist
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
        # Redownload if the file is incomplete or corrupted
        if not os.path.exists(output) or os.path.getsize(output) == 0:
            if os.path.exists(output):
                os.remove(output)  # Remove the incomplete file
            gdown.download(url, output, quiet=False)

        # Verify that the file was downloaded correctly by attempting to open it
        try:
            with open(output, "rb") as f:
                PdfReader(f)
            curriculum_files[name] = output
        except Exception as e:
            st.error(
                f"Failed to download or verify the file: {output}. Error: {e}")
            return None

    return curriculum_files

# Extract text from PDF


def extract_text_from_pdf(file_path):
    try:
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        st.error(f"Error reading PDF file {file_path}: {e}")
        return ""

# Extract text from DOC/DOCX


def extract_text_from_doc(file_path):
    doc = docx.Document(file_path)
    text = "\n".join([para.text for para in doc.paragraphs])
    return text

# Extract text from image


def extract_text_from_image(file_path):
    img = Image.open(file_path)
    text = pytesseract.image_to_string(img)
    return text

# Load and combine curriculum content with a focus on MERN and Fundamentals


def load_curriculum(curriculum_files):
    curriculum_texts = []
    # Always prioritize MERN stack
    mern_text = extract_text_from_pdf(curriculum_files["mern_fullstack"])
    fundamentals_text = extract_text_from_pdf(curriculum_files["fundamentals"])
    curriculum_texts.append(mern_text)
    curriculum_texts.append(fundamentals_text)

    # If needed, include other stacks
    for key in ["data_analytics", "java_fullstack", "qa_testing"]:
        curriculum_texts.append(extract_text_from_pdf(curriculum_files[key]))

    return " ".join(curriculum_texts)

# Calculate the do-ability percentage


def calculate_doability(content, curriculum):
    content_words = set(content.split())
    curriculum_words = set(curriculum.split())
    match_count = len(content_words.intersection(curriculum_words))
    return (match_count / len(content_words)) * 100 if content_words else 0

# Streamlit Web App


def main():
    st.title("Assignment Do-ability Checker")

    st.write("Loading curriculum files...")
    curriculum_files = download_curriculum()

    if not curriculum_files:
        st.error("Failed to load curriculum files.")
        return

    st.write("Curriculum files loaded.")

    uploaded_file = st.file_uploader("Please upload your assignment document", type=[
                                     "pdf", "docx", "doc", "png", "jpg", "jpeg"])

    if uploaded_file is not None:
        file_details = {"FileName": uploaded_file.name,
                        "FileType": uploaded_file.type}
        # st.write(file_details)

        if uploaded_file.type == "application/pdf":
            content = extract_text_from_pdf(uploaded_file)
        elif uploaded_file.type in ["application/vnd.openxmlformats-officedocument.wordprocessingml.document", "application/msword"]:
            content = extract_text_from_doc(uploaded_file)
        elif uploaded_file.type in ["image/png", "image/jpeg"]:
            content = extract_text_from_image(uploaded_file)
        else:
            st.error("Unsupported file type.")
            return

        curriculum = load_curriculum(curriculum_files)
        do_ability = calculate_doability(content, curriculum)

        st.title(f"{do_ability:.2f}% is doable out of 100%")


if __name__ == "__main__":
    main()
