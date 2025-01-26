import streamlit as st
import pyttsx3  # Basic TTS library for prototyping
import re
from gtts import gTTS  # For text-to-speech with specific accents
from tempfile import NamedTemporaryFile

# Initialize TTS engine
engine = pyttsx3.init()

# Configure TTS voice options
voices = engine.getProperty('voices')
# Fallback to default voice if no specific match is found
african_accent = next((voice for voice in voices if "English" in voice.name or "english" in voice.languages), voices[0])

engine.setProperty('voice', african_accent.id)
engine.setProperty('rate', 150)  # Default rate

def process_text(text, skip_citations=True):
    """
    Process text by optionally removing citations and footnotes.
    Citations are identified using common patterns like [1], (Author, Year).
    """
    if skip_citations:
        # Remove patterns like [1], [1-3], (Author, Year)
        text = re.sub(r'\[.*?\]|\(.*?\)', '', text)
    return text.strip()

import pyttsx3

def save_audio_offline(text, filename="output.mp3"):
    engine = pyttsx3.init()
    engine.save_to_file(text, filename)
    engine.runAndWait()

save_audio_offline("This is a test.")


# Streamlit interface
st.title("EduVoice Africa: Audio Notes for Students")
st.write("Convert your study notes and literature reviews into audio with an African accent.")

# File uploader
uploaded_file = st.file_uploader("Upload a text file (PDF, DOCX, TXT)", type=["txt", "pdf", "docx"])

# Options
skip_citations = st.checkbox("Skip citations and footnotes", value=True)
reading_speed = st.slider("Reading Speed (words per minute)", 100, 250, 150)
selected_accent = st.selectbox("Select African Accent", ["Ghanaian English", "Nigerian English", "Kenyan English"])

from PyPDF2 import PdfReader
from docx import Document

# Ensure that a file is uploaded before accessing its attributes
if uploaded_file is not None:
    # Check the file type based on its name
    if uploaded_file.name.endswith('.txt'):
        try:
            file_content = uploaded_file.read().decode("utf-8")  # Assuming UTF-8 encoding
            st.text_area("Uploaded File Content", file_content, height=300)
        except UnicodeDecodeError:
            st.error("Could not decode the text file. Ensure it uses UTF-8 encoding.")
    elif uploaded_file.name.endswith('.pdf'):
        try:
            pdf_reader = PdfReader(uploaded_file)
            file_content = ''.join([page.extract_text() for page in pdf_reader.pages])
            st.text_area("Uploaded File Content", file_content, height=300)
        except Exception as e:
            st.error(f"Error reading PDF file: {e}")
    elif uploaded_file.name.endswith('.docx'):
        try:
            doc = Document(uploaded_file)
            file_content = '\n'.join([para.text for para in doc.paragraphs])
            st.text_area("Uploaded File Content", file_content, height=300)
        except Exception as e:
            st.error(f"Error reading DOCX file: {e}")
    else:
        st.error("Unsupported file type.")
else:
    # Notify the user to upload a file
    st.info("Please upload a file to continue.")

# Generate audio if the user has uploaded a file
if uploaded_file and st.button("Generate Audio"):
    processed_text = process_text(file_content, skip_citations=skip_citations)
    audio_file_path = "output.mp3"  # Define output file name
    save_audio_offline(processed_text, filename=audio_file_path)

    
    # Provide an audio player for the generated audio file
    st.audio(audio_file_path, format="audio/mp3", start_time=0)
    st.success("Audio generated successfully!")

# Footer
st.write("**EduVoice Africa** | Empowering students through accessible learning.")
