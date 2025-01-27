import streamlit as st
import speech_recognition as sr
import requests
import pyttsx3
from gtts import gTTS
import simpleaudio as sa
import os
from pydub import AudioSegment  # Add this import

# Placeholder Mobile Money API URL (replace with the actual API endpoint)
API_URL = "https://example.com/mobile-money-api"

# Initialize authentication state
if "auth_success" not in st.session_state:
    st.session_state.auth_success = False

# Function to speak the given text using gTTS
import pygame
import os
from gtts import gTTS

def speak(text):
    tts = gTTS(text, lang='en')
    temp_file = "temp_audio.mp3"
    tts.save(temp_file)
    pygame.mixer.init()
    pygame.mixer.music.load(temp_file)
    pygame.mixer.music.play()

    try:
        # Play the music until it finishes
        while pygame.mixer.music.get_busy():
            continue
    finally:
        # Ensure the file is removed even if an error happens
        pygame.mixer.music.stop()  # Stop the music if it's still playing
        pygame.mixer.quit()  # Close pygame mixer
        os.remove(temp_file)  # Remove the temporary audio file


# Function to authenticate the user's phone number with the mobile money service
def authenticate_phone(phone_number, pin):
    response = requests.post(
        f"{API_URL}/authenticate",
        json={"phone_number": phone_number, "pin": pin},
    )
    return response.status_code == 200

# Function to process a transaction via mobile money
def process_transaction(phone_number, recipient_number, amount, transaction_type):
    response = requests.post(
        f"{API_URL}/transaction",
        json={
            "phone_number": phone_number,
            "recipient_number": recipient_number,
            "amount": amount,
            "transaction_type": transaction_type,
        },
    )
    if response.status_code == 200:
        return True, response.json().get("new_balance", 0.0)
    else:
        return False, response.json().get("message", "Transaction failed.")

# Function to process speech commands
def process_command(command):
    command = command.lower()

    if "buy data" in command:
        amount = extract_amount(command)
        if amount:
            return "data", float(amount)
        else:
            return "error", "Please specify the amount of data you want to purchase."

    elif "buy airtime" in command:
        amount = extract_amount(command)
        if amount:
            return "airtime", float(amount)
        else:
            return "error", "Please specify the amount of airtime you want to purchase."

    elif "transfer money" in command:
        amount = extract_amount(command)
        recipient = extract_recipient(command)
        if amount and recipient:
            return "transfer", (recipient, float(amount))
        else:
            return "error", "Please specify the recipient and amount for the transfer."

    elif "check balance" in command:
        return "balance", None

    else:
        return "error", "Command not recognized. Please say 'buy data', 'buy airtime', 'transfer money', or 'check balance'."

# Function to extract amount from the speech command
def extract_amount(command):
    words = command.split()
    for word in words:
        if word.isdigit():
            return word
    return None

# Function to extract recipient number from the speech command
def extract_recipient(command):
    # Assuming the recipient number is always mentioned after the word "to"
    words = command.split()
    for i, word in enumerate(words):
        if word == "to" and i + 1 < len(words):
            return words[i + 1]
    return None

# Streamlit app
st.title("Voice Command: Buy Data, Airtime, Transfer Money")
st.write("Use your voice to purchase data or airtime, transfer money, check your balance, and more.")

# Authenticate phone number
if not st.session_state.auth_success:
    phone_number = st.text_input("Enter your phone number:")
    if st.button("Authenticate"):
        if not phone_number.isdigit() or len(phone_number) < 10:
            st.error("Invalid phone number. Please enter a valid 10-digit number.")
        else:
            st.session_state.auth_success = True
            st.success("Phone number authenticated. Proceed with your transaction.")
else:
    st.info("Phone number authenticated. Proceed with your transaction.")

# Button to start listening
if st.session_state.auth_success and st.button("Click to Speak"):
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.write("Listening...")
        speak("Listening...")
        try:
            audio = recognizer.listen(source, timeout=10, phrase_time_limit=100)
            command = recognizer.recognize_google(audio)
            st.write(f"You said: {command}")

            # Process the command
            command_type, amount_or_message = process_command(command)

            if command_type == "error":
                st.error(amount_or_message)
                speak(amount_or_message)

            elif command_type == "balance":
                response = requests.get(f"{API_URL}/balance", params={"phone_number": phone_number})
                if response.status_code == 200:
                    balance = response.json().get("balance", 0.0)
                    st.success(f"Your current wallet balance is GHS {balance}.")
                    speak(f"Your current wallet balance is GHS {balance}.")
                else:
                    st.error("Failed to retrieve balance. Please try again.")
                    speak("Failed to retrieve balance. Please try again.")

            elif command_type in ["data", "airtime"]:
                recipient_number = st.text_input("Enter recipient phone number (or leave blank for self):")
                recipient_number = recipient_number if recipient_number else phone_number

                if amount_or_message <= 0:
                    st.error("Invalid amount. Please specify a valid amount.")
                    speak("Invalid amount. Please specify a valid amount.")
                else:
                    input_pin = st.text_input("Enter your mobile money PIN:", type="password")
                    if st.button("Confirm Transaction"):
                        if authenticate_phone(phone_number, input_pin):
                            success, result = process_transaction(
                                phone_number, recipient_number, amount_or_message, command_type
                            )
                            if success:
                                st.success(
                                    f"Successfully purchased {command_type} for GHS {amount_or_message} for {recipient_number}."
                                )
                                st.info(f"New wallet balance: GHS {result}.")
                                speak(f"Successfully purchased {command_type} for GHS {amount_or_message} for {recipient_number}. New wallet balance: GHS {result}.")
                            else:
                                st.error(result)
                                speak(result)
                        else:
                            st.error("Authentication failed. Incorrect PIN.")
                            speak("Authentication failed. Incorrect PIN.")

            elif command_type == "transfer":
                recipient, amount = amount_or_message
                if amount <= 0:
                    st.error("Invalid amount for transfer. Please specify a valid amount.")
                    speak("Invalid amount for transfer. Please specify a valid amount.")
                else:
                    input_pin = st.text_input("Enter your mobile money PIN:", type="password")
                    if st.button("Confirm Transfer"):
                        if authenticate_phone(phone_number, input_pin):
                            success, result = process_transaction(
                                phone_number, recipient, amount, "transfer"
                            )
                            if success:
                                st.success(f"Successfully transferred GHS {amount} to {recipient}.")
                                st.info(f"New wallet balance: GHS {result}.")
                                speak(f"Successfully transferred GHS {amount} to {recipient}. New wallet balance: GHS {result}.")
                            else:
                                st.error(result)
                                speak(result)
                        else:
                            st.error("Authentication failed. Incorrect PIN.")
                            speak("Authentication failed. Incorrect PIN.")

        except sr.UnknownValueError:
            st.error("Sorry, we couldn't understand you. Please try again.")
            speak("Sorry, we couldn't understand you. Please try again.")
        except sr.RequestError:
            st.error("Could not process the request. Please check your internet connection.")
            speak("Could not process the request. Please check your internet connection.")
        except Exception as e:
            st.error("An error occurred.")
            speak("An error occurred.")

st.write("Note: Ensure you have a stable internet connection and proper microphone access.")
