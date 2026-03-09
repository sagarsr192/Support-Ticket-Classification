from flask import Flask, make_response, render_template_string
import json
import pandas as pd
from textblob import TextBlob

app = Flask(__name__)


def predict_category(text: str) -> str:
    text = text.lower()
    if "payment" in text or "charged" in text or "bill" in text:
        return "Billing"
    if "password" in text or "account" in text or "login" in text:
        return "Account"
    return "Technical"


def predict_priority(text: str) -> str:
    text = text.lower()
    if "not working" in text or "crash" in text or "error" in text:
        return "High"
    if "slow" in text or "failed" in text:
        return "Medium"
    return "Low"


def sentiment(text: str) -> str:
    polarity = TextBlob(text).sentiment.polarity
    if polarity < -0.2:
        return "Frustrated"
    if polarity < 0:
        return "Angry"
    return "Neutral"


def build_df() -> pd.DataFrame:
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
        "The software freezes when generating report",
    ]
    df = pd.DataFrame({"Ticket Text": tickets})
    df["Predicted Category"] = df["Ticket Text"].apply(predict_category)
    df["Priority"] = df["Ticket Text"].apply(predict_priority)
    df["Sentiment"] = df["Ticket Text"].apply(sentiment)
    return df


HTML = """
<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Support Ticket Classifier</title>
  <script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
  <style>
    body { background:#0b1220; color:#e8edf7; font-family:Segoe UI, sans-serif; margin:0; }
    .wrap { max-width:1200px; margin:24px auto; padding:0 16px; }
    .card { background:#111a2b; border:1px solid #24324a; border-radius:12px; padding:14px; margin-top:14px; }
    h1, h2 { margin:8px 0; }
    table { width:100%; border-collapse:collapse; }
    th, td { border-bottom:1px solid #24324a; padding:8px; text-align:left; }
    .grid { display:grid; grid-template-columns:1fr 1fr; gap:12px; }
    @media (max-width: 900px) { .grid { grid-template-columns:1fr; } }
    a.button { display:inline-block; margin-top:10px; color:#0b1220; background:#9bd0ff; padding:8px 12px; border-radius:8px; text-decoration:none; font-weight:600; }
  </style>
</head>
<body>
  <div class="wrap">
    <h1>Advanced Support Ticket Classification System</h1>

    <div class="card">
      <h2>Ticket Predictions</h2>
      <table>
        <thead>
          <tr><th>Ticket Text</th><th>Predicted Category</th><th>Priority</th><th>Sentiment</th></tr>
        </thead>
        <tbody>
        {% for row in rows %}
          <tr>
            <td>{{ row["Ticket Text"] }}</td>
            <td>{{ row["Predicted Category"] }}</td>
            <td>{{ row["Priority"] }}</td>
            <td>{{ row["Sentiment"] }}</td>
          </tr>
        {% endfor %}
        </tbody>
      </table>
    </div>

    <div class="grid">
      <div class="card">
        <h2>Priority Distribution</h2>
        <div id="priority_chart" style="height:320px"></div>
      </div>
      <div class="card">
        <h2>Sentiment Analysis</h2>
        <div id="sentiment_chart" style="height:320px"></div>
      </div>
    </div>

    <div class="card">
      <h2>Export Results</h2>
      <a class="button" href="/download.csv">Export Batch Results</a>
    </div>

    <div class="card">
      <h2>Automated Response Suggestion</h2>
      <p>Suggested Reply: Please try restarting your router or logging in again. If the issue persists, our support team will assist you immediately.</p>
    </div>
  </div>

<script>
const priorityX = {{ priority_x | safe }};
const priorityY = {{ priority_y | safe }};
const sentimentL = {{ sentiment_l | safe }};
const sentimentV = {{ sentiment_v | safe }};

let pSelected = null;
let sSelected = null;

function drawPriority(blink) {
  const base = '#4ea1ff';
  const dim = '#2d3c58';
  const flash = '#9bd0ff';
  const colors = priorityX.map((_, i) => pSelected === null ? base : (i === pSelected ? (blink ? flash : base) : dim));
  const lineWidths = priorityX.map((_, i) => i === pSelected ? (blink ? 4 : 2) : 1);
  const lineColors = priorityX.map((_, i) => i === pSelected ? '#d7e8ff' : '#24324a');

  Plotly.react('priority_chart', [{
    type: 'bar', x: priorityX, y: priorityY,
    marker: { color: colors, line: { color: lineColors, width: lineWidths } }
  }], {
    paper_bgcolor:'#111a2b', plot_bgcolor:'#111a2b',
    font:{color:'#e8edf7'}, margin:{l:35,r:20,t:8,b:35},
    xaxis:{categoryorder:'array', categoryarray:['Low','Medium','High']},
    yaxis:{title:'Tickets', gridcolor:'#24324a'}
  }, {displayModeBar:false, responsive:true});
}

function drawSentiment(blink) {
  const palette = ['#4ea1ff', '#ff9d42', '#4ad6a8', '#d28cff', '#ffd166'];
  const dim = '#2d3c58';
  const flash = '#9bd0ff';
  const colors = sentimentL.map((_, i) => sSelected === null ? palette[i % palette.length] : (i === sSelected ? (blink ? flash : palette[i % palette.length]) : dim));
  const pull = sentimentL.map((_, i) => i === sSelected ? (blink ? 0.12 : 0.06) : 0);

  Plotly.react('sentiment_chart', [{
    type:'pie', labels:sentimentL, values:sentimentV, hole:0.2, textinfo:'percent+label', pull:pull,
    marker:{ color:colors, line:{ color:'#111a2b', width:2 } }
  }], {
    paper_bgcolor:'#111a2b', plot_bgcolor:'#111a2b',
    font:{color:'#e8edf7'}, margin:{l:20,r:20,t:8,b:20}, showlegend:false
  }, {displayModeBar:false, responsive:true});
}

function blink(fn) {
  const seq = [true, false, true, false, false];
  let i = 0;
  function step() {
    fn(seq[i]);
    i += 1;
    if (i < seq.length) setTimeout(step, 120);
  }
  step();
}

drawPriority(false);
drawSentiment(false);

document.getElementById('priority_chart').on('plotly_click', (e) => {
  pSelected = e.points[0].pointNumber;
  blink(drawPriority);
});

document.getElementById('sentiment_chart').on('plotly_click', (e) => {
  sSelected = e.points[0].pointNumber;
  blink(drawSentiment);
});
</script>
</body>
</html>
"""


@app.route("/")
def index():
    df = build_df()
    priority = df["Priority"].value_counts().reindex(["Low", "Medium", "High"], fill_value=0)
    sentiment_counts = df["Sentiment"].value_counts()

    return render_template_string(
        HTML,
        rows=df.to_dict(orient="records"),
        priority_x=json.dumps(priority.index.tolist()),
        priority_y=json.dumps(priority.values.tolist()),
        sentiment_l=json.dumps(sentiment_counts.index.tolist()),
        sentiment_v=json.dumps(sentiment_counts.values.tolist()),
    )


@app.route("/download.csv")
def download_csv():
    df = build_df()
    response = make_response(df.to_csv(index=False))
    response.headers["Content-Type"] = "text/csv"
    response.headers["Content-Disposition"] = "attachment; filename=predicted_tickets_batch.csv"
    return response


if __name__ == "__main__":
    app.run(debug=True)
