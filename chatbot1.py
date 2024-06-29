
import streamlit as st
import openai
import os
from pydub import AudioSegment
# from pydna.playback import play
from io import BytesIO

# Initialize OpenAI client instance
def init_openai():
    if (openai_api_key := st.session_state.get("openai_api_key")) is None:
        openai_api_key = None
    openai.api_key = openai_api_key
    return openai
# Function to generate speech from text
def generate_speech(text, client, voice="alloy"):  # Add a new parameter for voice
    response = client.Audio.create(
        model="tts-1",
        voice=voice,  # Use the new parameter
        input=text,
    )
    audio_content = response["audio"]
    st.audio(audio_content, format="audio/mp3")

st.title("💬 Chatbot")
st.caption("🚀 A Streamlit chatbot powered by OpenAI")

# Initialize session state for messages
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]

# Display message history
for msg in st.session_state["messages"]:
    st.chat_message(msg["role"]).write(msg["content"])

openai_client = init_openai()

if (prompt := st.chat_input()) and not openai_client:
    st.info("Please add your OpenAI API key to continue.")
    st.stop()

st.session_state["messages"].append({"role": "user", "content": prompt})
st.chat_message("user").write(prompt)

response = openai_client.ChatCompletion.create(
    model="gpt-4",
    messages=st.session_state["messages"]
)

msg = response.choices[0]["message"]["content"]
st.session_state["messages"].append({"role": "assistant", "content": msg})
st.chat_message("assistant").write(msg)

# Provide options to generate speech or upload voice for transcription
if st.button("Generate Speech") and openai_client:
    generate_speech(msg, openai_client)

uploaded_file = st.file_uploader("Upload Audio for Transcription", type=["mp3", "wav"])
if uploaded_file is not None and openai_client:
    file_buffer = BytesIO(uploaded_file.read())
import speech_recognition as sr

def transcribe_audio(file_path):
    r = sr.Recognizer()
    with sr.AudioFile(file_path) as source:
        audio_data = r.record(source)
        transcribed_text = r.recognize_google(audio_data)
    return transcribed_text

# Usage
if uploaded_file is not None and openai_client:
    file_buffer = BytesIO(uploaded_file.read())
    file_extension = uploaded_file.name.split(".")[-1]
    if file_extension.lower() in ["mp3", "wav"]:
        file_path = f"uploaded_audio.{file_extension}"
        with open(file_path, "wb") as f:
            f.write(file_buffer.getbuffer())
        transcribed_text = transcribe_audio(file_path)
        st.write("Transcribed text: ", transcribed_text)
    else:
        st.error("Invalid file format. Please upload an MP3 or WAV file.")
    st.write("Transcribed text: ", transcribed_text)
