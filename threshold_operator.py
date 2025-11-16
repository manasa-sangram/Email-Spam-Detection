# Import required libraries
import streamlit as st
import pandas as pd
import random
import time

# Define a fixed threshold above which a message is classified as spam
THRESHOLD = 0.7

# Load dataset function
def load_dataset():
    # Read the phishing email dataset
    df = pd.read_csv("phishing_emails.csv")

    # Convert the numeric 'label' (1 = spam, 0 = ham) to string values
    df['label'] = df['label'].apply(lambda x: 'spam' if x == 1 else 'ham')

    # Rename the 'body' column to 'message' for clarity
    df = df.rename(columns={'body': 'message'})

    # Return only the required columns
    return df[['sender', 'subject', 'message', 'label']]

# Function to simulate spam score based on label
def generate_spam_score(label):
    # If label is 'spam', generate score between 0.7–1.0
    # Else for 'ham', generate score between 0.0–0.6
    return round(random.uniform(0.7, 1.0), 2) if label == 'spam' else round(random.uniform(0.0, 0.6), 2)

# Apply threshold and label email as spam or ham
def apply_threshold(df):
    # Generate a spam score for each row
    df['spam_score'] = df['label'].apply(generate_spam_score)

    # Compare score to threshold to classify
    df['is_spam'] = df['spam_score'] >= THRESHOLD
    return df

# Set up Streamlit page configuration
st.set_page_config(page_title="📧 Email Spam Detection", layout="wide")
st.title("📧 Real-Time Email Spam Detection")

# Sidebar settings
with st.sidebar:
    st.subheader("📊 Controls")

    # Start button to begin streaming
    start_streaming = st.button("▶ Start Streaming")

    # Slider to control delay between emails (streaming simulation)
    delay = st.slider("⏱ Delay between emails (sec)", 1, 5, 2)

# Create session state variable to track which messages are expanded
if "expanded" not in st.session_state:
    st.session_state.expanded = {}

# Load and process dataset
df = apply_threshold(load_dataset())

# Create containers for email streaming
container = st.container()
stop_signal = st.empty()

# Begin message streaming if user clicked "Start Streaming"
if start_streaming:
    # Optional "Stop" button to interrupt stream
    stop = stop_signal.button("⛔ Stop Streaming")

    # Iterate through each email in the dataset
    for i, row in df.iterrows():
        if stop:
            st.warning("🚨 Streaming stopped.")
            break

        # Create a unique key for each message
        key = f"msg_{i}"

        # Initialize expanded state for this message if not set
        if key not in st.session_state.expanded:
            st.session_state.expanded[key] = False

        with container:
            # Display header and sender information
            st.markdown(f"### ✉️ Message #{i+1}")
            st.markdown(f"**From:** `{row['sender']}`")
            st.markdown(f"**Subject:** {row['subject']}`")

            # Break message into sentences
            sentences = row['message'].split('. ')

            # Create preview using first 2 sentences
            preview = '. '.join(sentences[:2]) + ('...' if len(sentences) > 2 else '')

            # Combine full message
            full = '. '.join(sentences)

            # Display full message or preview based on expanded state
            if st.session_state.expanded[key]:
                # If expanded, show full message and link to "Show less"
                st.markdown(f"**Body:** {full} [**Show less**](#{key})", unsafe_allow_html=True)

                # Form to handle "Show less" click
                with st.form(f"less_{i}"):
                    if st.form_submit_button("Show less"):
                        st.session_state.expanded[key] = False
            else:
                # If collapsed, show only preview and "Show more..." link
                st.markdown(f"**Body:** {preview} [**Show more...**](#{key})", unsafe_allow_html=True)

            # Display spam score
            st.markdown(f"**Spam Score:** `{row['spam_score']}`")

            # Visual spam/ham classification
            if row['is_spam']:
                st.error("🚫 SPAM Detected!")
            else:
                st.success("✅ Not Spam (Ham)")

            # Divider line between emails
            st.markdown("---")

        # Delay between messages to simulate real-time streaming
        time.sleep(delay)

    # Final success message
    st.success("✅ All messages streamed.")
