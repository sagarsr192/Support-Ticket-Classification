import streamlit as st
import pandas as pd
import json
import streamlit.components.v1 as components
from textblob import TextBlob

st.set_page_config(page_title="Support Ticket Classifier", layout="wide")

st.markdown(
    """
    <style>
    .stApp {
        background-color: #0b1220;
        color: #e8edf7;
    }

    /* Keep text readable across common Streamlit containers. */
    .stMarkdown,
    .stText,
    .stSubheader,
    .stHeader,
    .stDataFrame,
    label,
    p,
    span,
    div {
        color: #e8edf7;
    }

    /* Dark surfaces for chat-style components and cards. */
    .stChatMessage,
    .stChatInputContainer,
    .stAlert,
    section[data-testid="stSidebar"],
    div[data-testid="stExpander"] {
        background-color: #111a2b;
        color: #e8edf7;
        border-color: #24324a;
    }

    div[data-testid="stChatInput"] textarea {
        background-color: #111a2b;
        color: #e8edf7;
        border: 1px solid #2d3c58;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("Advanced Support Ticket Classification System")

# -----------------------------
# Sample Ticket Data
# -----------------------------

tickets = [
"My internet is not working since yesterday",
"I was charged twice for my subscription",
"I cannot reset my password",
"The mobile app crashes when opening",
"Website is loading very slowly",
"I need help changing my subscription plan",
"My account is locked",
"Payment failed but money was deducted",
"I cannot upload files to the system",
"The dashboard is showing an error",
"Please refund my last payment",
"Login page is not loading",
"I forgot my password",
"Unable to update my billing information",
"The software freezes when generating report"
]

df = pd.DataFrame({"Ticket Text": tickets})

# -----------------------------
# Simple Rule Based Prediction
# -----------------------------

def predict_category(text):

    text = text.lower()

    if "payment" in text or "charged" in text or "bill" in text:
        return "Billing"

    elif "password" in text or "account" in text or "login" in text:
        return "Account"

    else:
        return "Technical"


def predict_priority(text):

    text = text.lower()

    if "not working" in text or "crash" in text or "error" in text:
        return "High"

    elif "slow" in text or "failed" in text:
        return "Medium"

    else:
        return "Low"


def sentiment(text):

    polarity = TextBlob(text).sentiment.polarity

    if polarity < -0.2:
        return "Frustrated"

    elif polarity < 0:
        return "Angry"

    else:
        return "Neutral"


# Apply predictions
df["Predicted Category"] = df["Ticket Text"].apply(predict_category)
df["Priority"] = df["Ticket Text"].apply(predict_priority)
df["Sentiment"] = df["Ticket Text"].apply(sentiment)

# -----------------------------
# Show Table
# -----------------------------

st.subheader("Ticket Predictions")

st.dataframe(df)

# -----------------------------
# Charts Section
# -----------------------------


def _render_priority_chart(priority_df):
    x_values = json.dumps(priority_df["Priority"].tolist())
    y_values = json.dumps(priority_df["Tickets"].tolist())
    priority_html = """
        <div id="priority_chart" style="height:340px;"></div>
        <script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
        <script>
        const px = __X_VALUES__;
        const py = __Y_VALUES__;
        const pBase = '#4ea1ff';
        const pDim = '#2d3c58';
        const pBlink = '#9bd0ff';
        let pSelected = null;

        function drawPriority(isBlink) {
            const colors = px.map((_, i) => pSelected === null ? pBase : (i === pSelected ? (isBlink ? pBlink : pBase) : pDim));
            const lineWidths = px.map((_, i) => i === pSelected ? (isBlink ? 4 : 2) : 1);
            const lineColors = px.map((_, i) => i === pSelected ? '#d7e8ff' : '#24324a');

            Plotly.react('priority_chart', [{
                type: 'bar',
                x: px,
                y: py,
                marker: { color: colors, line: { color: lineColors, width: lineWidths } },
                hovertemplate: 'Priority: %{x}<br>Tickets: %{y}<extra></extra>'
            }], {
                paper_bgcolor: '#111a2b',
                plot_bgcolor: '#111a2b',
                font: { color: '#e8edf7' },
                margin: { l: 35, r: 20, t: 10, b: 35 },
                xaxis: { title: '', categoryorder: 'array', categoryarray: ['Low', 'Medium', 'High'] },
                yaxis: { title: 'Tickets', gridcolor: '#24324a' }
            }, {displayModeBar: false, responsive: true});
        }

        drawPriority(false);
        const pChart = document.getElementById('priority_chart');
        pChart.on('plotly_click', function(evt) {
            pSelected = evt.points[0].pointNumber;
            const seq = [true, false, true, false, false];
            let i = 0;
            function animate() {
                drawPriority(seq[i]);
                i += 1;
                if (i < seq.length) setTimeout(animate, 120);
            }
            animate();
        });
        </script>
    """
    priority_html = priority_html.replace("__X_VALUES__", x_values).replace("__Y_VALUES__", y_values)

    components.html(
        priority_html,
        height=350,
    )


def _render_sentiment_chart(sentiment_df):
    labels = json.dumps(sentiment_df["Sentiment"].tolist())
    values = json.dumps(sentiment_df["Tickets"].tolist())
    sentiment_html = """
        <div id="sentiment_chart" style="height:340px;"></div>
        <script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
        <script>
        const sl = __LABELS__;
        const sv = __VALUES__;
        const sPalette = ['#4ea1ff', '#ff9d42', '#4ad6a8', '#d28cff', '#ffd166'];
        const sDim = '#2d3c58';
        const sBlink = '#9bd0ff';
        let sSelected = null;

        function drawSentiment(isBlink) {
            const colors = sl.map((_, i) => sSelected === null ? sPalette[i % sPalette.length] : (i === sSelected ? (isBlink ? sBlink : sPalette[i % sPalette.length]) : sDim));
            const pull = sl.map((_, i) => i === sSelected ? (isBlink ? 0.12 : 0.06) : 0);

            Plotly.react('sentiment_chart', [{
                type: 'pie',
                labels: sl,
                values: sv,
                hole: 0.2,
                textinfo: 'percent+label',
                pull: pull,
                marker: { color: colors, line: { color: '#111a2b', width: 2 } },
                hovertemplate: 'Sentiment: %{label}<br>Tickets: %{value}<extra></extra>'
            }], {
                paper_bgcolor: '#111a2b',
                plot_bgcolor: '#111a2b',
                font: { color: '#e8edf7' },
                margin: { l: 20, r: 20, t: 10, b: 20 },
                showlegend: false
            }, {displayModeBar: false, responsive: true});
        }

        drawSentiment(false);
        const sChart = document.getElementById('sentiment_chart');
        sChart.on('plotly_click', function(evt) {
            sSelected = evt.points[0].pointNumber;
            const seq = [true, false, true, false, false];
            let i = 0;
            function animate() {
                drawSentiment(seq[i]);
                i += 1;
                if (i < seq.length) setTimeout(animate, 120);
            }
            animate();
        });
        </script>
    """
    sentiment_html = sentiment_html.replace("__LABELS__", labels).replace("__VALUES__", values)

    components.html(
        sentiment_html,
        height=350,
    )

col1, col2 = st.columns(2)

# Priority chart
with col1:

    st.subheader("Priority Distribution")

    priority_df = (
        df["Priority"]
        .value_counts()
        .rename_axis("Priority")
        .reset_index(name="Tickets")
    )
    _render_priority_chart(priority_df)

# Sentiment chart
with col2:

    st.subheader("Sentiment Analysis")

    sentiment_df = (
        df["Sentiment"]
        .value_counts()
        .rename_axis("Sentiment")
        .reset_index(name="Tickets")
    )
    _render_sentiment_chart(sentiment_df)

st.caption("Click a bar or pie slice to make it blink and stay highlighted.")

# -----------------------------
# Export Results
# -----------------------------

st.subheader("Export Results")

csv = df.to_csv(index=False)

st.download_button(
    label="Export Batch Results",
    data=csv,
    file_name="predicted_tickets_batch.csv",
    mime="text/csv"
)

# -----------------------------
# Automated Response
# -----------------------------

st.subheader("Automated Response Suggestion")

st.info(
"Suggested Reply: Please try restarting your router or logging in again. "
"If the issue persists, our support team will assist you immediately."
)