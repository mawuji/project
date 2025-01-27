import streamlit as st
from PIL import Image
import cv2
import numpy as np
import face_recognition

# Title of the App
st.title("National Face Recognition System")

# Sidebar for navigation
st.sidebar.title("Options")
app_mode = st.sidebar.selectbox(
    "Choose the mode",
    ["Upload Image", "About"]
)

if app_mode == "Upload Image":
    st.header("Upload an Image to Detect Faces")
    
    uploaded_image = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])
    if uploaded_image is not None:
        # Display the uploaded image
        image = Image.open(uploaded_image)
        st.image(image, caption="Uploaded Image", use_column_width=True)

        # Convert image to RGB
        img_array = np.array(image)
        rgb_image = cv2.cvtColor(img_array, cv2.COLOR_BGR2RGB)

        # Perform face detection
        face_locations = face_recognition.face_locations(rgb_image)

        st.write(f"Found {len(face_locations)} face(s) in the image.")

        # Draw rectangles around faces
        for face_location in face_locations:
            top, right, bottom, left = face_location
            cv2.rectangle(rgb_image, (left, top), (right, bottom), (0, 255, 0), 2)

        # Display result
        st.image(rgb_image, caption="Image with Detected Faces", use_column_width=True)

elif app_mode == "About":
    st.subheader("About this App")
    st.write("""
    This is a demonstration of a basic national face recognition system using **Streamlit**.
    The system utilizes:
    - [Streamlit](https://streamlit.io) for the frontend.
    - [face_recognition](https://github.com/ageitgey/face_recognition) for face detection.
    - [OpenCV](https://opencv.org) for image processing.
    """)
