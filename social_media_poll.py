import streamlit as st
from transformers import pipeline
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from wordcloud import WordCloud

# Title and Description
st.title("AI for Mining, Forecasting, and Explaining Public Opinion")
st.markdown("""
This application explores **AI techniques** for analyzing public opinion from social media data.  
Key Features:
- **Opinion Mining:** Sentiment and opinion analysis using NLP.
- **Forecasting Public Trends:** Time-series forecasting of public sentiment.
- **Explainable AI (XAI):** Transparent AI insights for stakeholders.
""")

# Sidebar for user inputs
st.sidebar.header("Configure Settings")
task = st.sidebar.selectbox("Select Task", ["Opinion Mining", "Forecasting", "Explainable AI"])

# Opinion Mining Section
if task == "Opinion Mining":
    st.header("Opinion Mining: Sentiment Analysis")
    st.markdown("Extract sentiments and opinions from user-generated social media text.")

    # Input area for text analysis
    user_text = st.text_area("Enter Social Media Text", "This product is amazing! I love it.")
    if st.button("Analyze Sentiment"):
        # Using Hugging Face sentiment-analysis pipeline
        sentiment_pipeline = pipeline("sentiment-analysis")
        sentiment = sentiment_pipeline(user_text)
        st.write("**Sentiment Analysis Result:**", sentiment[0])

    # Upload and visualize data
    uploaded_file = st.file_uploader("Upload CSV with Social Media Text", type="csv")
    if uploaded_file:
        data = pd.read_csv(uploaded_file)
        st.write("Sample Data:")
        st.dataframe(data.head())
        if "text" in data.columns:
            sentiments = sentiment_pipeline(list(data["text"]))
            data["sentiment"] = [s["label"] for s in sentiments]
            st.write("**Processed Data:**")
            st.dataframe(data)

            # Visualize sentiments
            sentiment_counts = data["sentiment"].value_counts()
            plt.figure(figsize=(6, 4))
            sentiment_counts.plot(kind="bar", color=["green", "red"])
            plt.title("Sentiment Distribution")
            plt.xlabel("Sentiment")
            plt.ylabel("Count")
            st.pyplot(plt)

# Forecasting Section
elif task == "Forecasting":
    st.header("Forecasting Public Trends")
    st.markdown("Use time-series analysis to predict shifts in public opinion.")

    # Simulated time-series data
    st.markdown("**Sample Forecasting Data:**")
    dates = pd.date_range(start="2023-01-01", periods=100)
    sentiments = np.random.uniform(0.4, 0.9, size=100)
    time_series = pd.DataFrame({"Date": dates, "Sentiment Score": sentiments})
    st.line_chart(time_series.set_index("Date"))

    st.markdown("""
    Forecasting methods like **ARIMA**, **LSTM**, and **GRU** can be applied to predict future sentiment trends.
    """)

# Explainable AI Section
elif task == "Explainable AI":
    st.header("Explainable AI (XAI)")
    st.markdown("Understand the reasoning behind AI predictions to build trust and usability.")

    # Demonstrating SHAP and LIME concepts
    st.markdown("""
    - **SHAP** (SHapley Additive exPlanations): Visualizes feature importance for predictions.
    - **LIME** (Local Interpretable Model-agnostic Explanations): Explains individual predictions.
    """)
    st.markdown("**Example:** Analyzing feature impact on sentiment predictions.")
    feature_importance = {"Keyword1": 0.3, "Keyword2": 0.25, "Keyword3": 0.2, "Keyword4": 0.15, "Keyword5": 0.1}
    st.bar_chart(pd.Series(feature_importance))

# Footer
st.markdown("---")
st.markdown("**Developed with 💡 by AI Enthusiast**")
