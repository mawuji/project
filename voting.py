import streamlit as st
import pandas as pd
import hashlib
import openpyxl
from PIL import Image
from datetime import datetime
from io import BytesIO

# Page Configuration
st.set_page_config(page_title="E-Voting System - Ghana", layout="wide")
st.title("E-Voting System for National Elections in Ghana")

# Section: Voter Authentication
st.header("Voter Authentication")

# Input fields for authentication
voter_id = st.text_input("Enter Your Voter ID")
biometric_key = st.text_input("Enter Biometric Key", type="password")

# Database for voter authentication
voters_db = {
    "VOTER12345": hashlib.sha256("bio12345".encode()).hexdigest(),
    "VOTER67890": hashlib.sha256("bio67890".encode()).hexdigest(),
    "VOTER67891": hashlib.sha256("bio67891".encode()).hexdigest()
}

# List to track voters who have already voted
if "voters_voted" not in st.session_state:
    st.session_state["voters_voted"] = set()

# Store authentication status in session state
if "voter_authenticated" not in st.session_state:
    st.session_state["voter_authenticated"] = False

# Authentication logic
def authenticate_voter(voter_id, biometric_key):
    if voter_id in voters_db:
        hashed_key = hashlib.sha256(biometric_key.encode()).hexdigest()
        if voters_db[voter_id] == hashed_key:
            return True
    return False

# Handle authentication button click
if st.button("Authenticate"):
    if authenticate_voter(voter_id, biometric_key):
        st.success("Authentication Successful! Proceed to vote.")
        st.session_state["voter_authenticated"] = True  # Set authenticated status
    else:
        st.error("Authentication Failed. Please check your Voter ID and Biometric Key.")

# Section: Vote Casting
st.header("Vote Casting")

# Candidates with local image paths
candidates = {
    "Kekeli A": r"C:\Users\resel\Project\kekeli.jpeg",
    "Paccy B": r"C:\Users\resel\Project\Pacci.jpeg",
    "Ben C": r"C:\Users\resel\Project\candidate.jpeg",
}

# Function to resize images
def resize_image(image_path, width, height):
    try:
        img = Image.open(image_path)
        img = img.resize((width, height))  # Resize to the specified dimensions
        return img
    except Exception as e:
        st.error(f"Error loading image for {image_path}: {e}")
        return None

# Candidate selection
selected_candidate = st.radio("Select your Asst Class Rep candidate:", options=list(candidates.keys()))

# Display candidate images with custom dimensions
cols = st.columns(len(candidates))
for i, (candidate, img_path) in enumerate(candidates.items()):
    with cols[i]:
        resized_img = resize_image(img_path, width=300, height=200)  # Set custom dimensions
        if resized_img:
            st.image(resized_img, caption=candidate, use_container_width=False)

# Vote submission
if "vote_logs" not in st.session_state:
    st.session_state["vote_logs"] = []

if st.button("Submit Vote"):
    if st.session_state["voter_authenticated"]:  # Check authentication status in session state
        if voter_id in st.session_state["voters_voted"]:
            st.error("You have already voted. Each voter can vote only once.")
        elif selected_candidate:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            vote = {
                "Voter ID": hashlib.sha256(voter_id.encode()).hexdigest(),
                "Vote": selected_candidate,
                "Timestamp": timestamp
            }
            st.session_state["vote_logs"].append(vote)  # Store vote in session state
            st.session_state["voters_voted"].add(voter_id)  # Mark voter as having voted
            st.success(f"Your vote for {selected_candidate} has been recorded.")
        else:
            st.error("Please select a candidate before submitting your vote.")
    else:
        st.error("You must authenticate first before submitting your vote.")

# Dashboard for Election Officials
if "official_access" not in st.session_state:
    st.session_state["official_access"] = False

st.sidebar.header("Election Officials Login")
official_username = st.sidebar.text_input("Username")
official_password = st.sidebar.text_input("Password", type="password")

# Authentication for officials
def authenticate_official(username, password):
    officials_db = {
        "admin": hashlib.sha256("admin123".encode()).hexdigest()
    }
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    return officials_db.get(username) == hashed_password

if st.sidebar.button("Login"):
    if authenticate_official(official_username, official_password):
        st.sidebar.success("Login successful.")
        st.session_state["official_access"] = True
    else:
        st.sidebar.error("Invalid credentials.")

if st.session_state["official_access"]:
    st.header("Voting Logs and Results Dashboard")

    logs_df = pd.DataFrame(st.session_state["vote_logs"])

    # Ensure the 'Vote' column exists before trying to access it
    if not logs_df.empty and "Vote" in logs_df.columns:
        st.subheader("Voting Logs")
        st.table(logs_df)

        if not logs_df.empty:
            output_logs = BytesIO()
            with pd.ExcelWriter(output_logs, engine="openpyxl") as writer:
                logs_df.to_excel(writer, index=False, sheet_name="Logs")
            output_logs.seek(0)
            st.download_button(
                label="Download Logs as Excel",
                data=output_logs,
                file_name="voting_logs.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

        results = logs_df["Vote"].value_counts().to_dict()
        st.subheader("Election Results")
        for candidate, votes in results.items():
            st.write(f"{candidate}: {votes} votes")

        if results:
            results_df = pd.DataFrame(list(results.items()), columns=["Candidate", "Votes"])
            output_results = BytesIO()
            with pd.ExcelWriter(output_results, engine="openpyxl") as writer:
                results_df.to_excel(writer, index=False, sheet_name="Results")
            output_results.seek(0)
            st.download_button(
                label="Download Results as Excel",
                data=output_results,
                file_name="voting_results.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    else:
        st.subheader("Voting Logs")
        st.write("No votes have been cast yet.")

st.write("\n---\n")
st.write("Developed for the national elections of Ghana using secure and transparent technologies.")
