# Hivemind

An end-to-end AI-powered algorithmic trading system that generates investment signals from sentiment analysis of Reddit's r/WallStreetBets community and executes automated trades on the Investopedia trading simulator.

## Overview

Hivemind captures the collective intelligence ("hivemind") of retail investors on Reddit, processes it through a machine learning pipeline, and translates social sentiment into trading decisions. The system continuously streams Reddit posts, extracts stock tickers, performs sentiment analysis, trains a neural network on historical price outcomes, and executes trades — all monitored via a live React dashboard.

## Architecture

```
Reddit (r/WSB) ──► Kafka Stream ──► MongoDB
                                       │
                              Data Processing Pipeline
                                       │
                          ┌────────────▼────────────┐
                          │   ML Pipeline            │
                          │  - Ticker Extraction     │
                          │  - Sentiment Analysis    │
                          │  - Feature Engineering   │
                          │  - Neural Net Training   │
                          └────────────┬────────────┘
                                       │
                          ┌────────────▼────────────┐
                          │   Trading Execution      │
                          │  (Investopedia API)      │
                          └────────────┬────────────┘
                                       │
                          ┌────────────▼────────────┐
                          │   React Dashboard        │
                          │  (Google App Engine)     │
                          └─────────────────────────┘
```

## Project Structure

```
hivemind/
├── hivemind-core-main/          # Backend Python services
│   ├── reddit-producer/         # Streams Reddit data to Kafka/MongoDB
│   │   ├── producer.py
│   │   ├── Dockerfile
│   │   ├── producer.yaml        # Kubernetes deployment manifest
│   │   └── cloudbuild.yaml      # Google Cloud Build config
│   │
│   ├── reddit-consumer/         # Kafka consumer service
│   │   └── consumer.py
│   │
│   ├── data/                    # Data processing pipeline
│   │   ├── process.py           # Processes raw Reddit data
│   │   ├── more_comments.py     # Fetches paginated comment trees
│   │   └── added_words.json     # Custom WSB sentiment lexicon
│   │
│   ├── ml/model/                # Machine learning pipeline
│   │   ├── sentiment.py         # VADER-based sentiment analysis
│   │   ├── ticker_extractor.py  # Stock ticker extraction
│   │   ├── preprocess.py        # Feature engineering & vectorization
│   │   ├── model.py             # Neural network training
│   │   ├── db_utils.py          # MongoDB utilities
│   │   ├── model.joblib         # Serialized trained model
│   │   └── tickers.csv          # Reference list of valid tickers
│   │
│   └── trading/                 # Trade execution layer
│       ├── main.py              # Google Cloud Functions entry points
│       ├── hivemind_trading.py  # Investopedia API wrapper
│       └── investopedia_simulator_api/  # Custom Investopedia client
│           ├── investopedia_api.py
│           ├── api_models.py
│           ├── stock_trade.py
│           ├── option_trade.py
│           ├── parsers.py
│           └── session_singleton.py
│
└── hivemind-web-main/           # Frontend React application
    └── src/
        ├── components/
        │   ├── AccountValue.js   # Portfolio value card
        │   ├── AccountCash.js    # Cash balance card
        │   ├── Chart.js          # Performance chart vs S&P 500
        │   ├── Portfolio.js      # Stock holdings table
        │   ├── OpenTrades.js     # Pending orders table
        │   └── RedditList.js     # Live r/WSB feed
        └── views/
            └── Dashboard.js      # Main layout
```

## Tech Stack

### Backend
| Layer | Technology |
|---|---|
| Reddit API | PRAW 7.2.0 |
| Message Streaming | Confluent Kafka |
| Database | MongoDB |
| Sentiment Analysis | VADER + custom WSB lexicon |
| ML Model | scikit-learn MLPRegressor |
| Stock Data | yfinance |
| NLP | NLTK, regex |
| Web Scraping | BeautifulSoup4, LXML |
| Runtime | Python 3.8 |

### Frontend
| Layer | Technology |
|---|---|
| UI Framework | React 17 |
| Component Library | Material-UI 4 |
| Charts | Recharts 2 |
| Routing | React Router DOM 5 |

### Infrastructure
| Service | Technology |
|---|---|
| Container Runtime | Docker |
| Orchestration | Kubernetes |
| CI/CD | Google Cloud Build |
| Serverless Functions | Google Cloud Functions |
| Frontend Hosting | Google App Engine |

## How It Works

### 1. Data Collection
The Reddit producer (`reddit-producer/producer.py`) connects to Reddit via PRAW and streams posts and comments from r/WallStreetBets in real-time using a multi-threaded `ThreadPoolExecutor` (up to 64 concurrent jobs). Raw submissions and full comment trees are stored in MongoDB.

### 2. Data Processing
The processing pipeline (`data/process.py`) extracts:
- Full comment threads via Reddit's MoreComments API
- Cleaned text (URLs and HTML tags stripped via BeautifulSoup)
- Structured JSON with submission metadata

### 3. Machine Learning Pipeline

**Ticker Extraction** (`ml/model/ticker_extractor.py`): Uses the `reticker` library combined with a reference CSV of all valid stock tickers to identify mentioned stocks in posts and comments. Inherits tickers from parent comments when children don't mention any.

**Sentiment Analysis** (`ml/model/sentiment.py`): Runs VADER sentiment with a custom WSB-specific lexicon (`added_words.json`) that maps community slang to sentiment scores:
- Positive: `bull`, `green`, `long`, `call`, `moon`, `tendies`, `rocket`, `diamond` → +3.0
- Negative: `bear`, `red`, `short`, `put`, `drop`, `sell`, `loss` → -3.0
- Options shorthand normalized: `300c` → `call`, `412p` → `put`

**Feature Engineering** (`ml/model/preprocess.py`): Builds ~20-dimensional feature vectors per post:
- **Social**: score, num_comments, upvote_ratio, awards count
- **Sentiment**: VADER pos/neg/neu scores
- **Temporal**: month, day, year from UTC timestamp
- **Categorical**: distinguished flag, stickied flag
- **Target (fitness)**: 5-day forward cumulative return for mentioned tickers, sigmoid-normalized to [-1, 1]

**Model Training** (`ml/model/model.py`): Trains a multi-layer perceptron regressor:
- Architecture: MLPRegressor with layers `(100, 50, 20, 10)`
- Activation: `tanh`
- Solver: `lbfgs`
- Input: MinMaxScaler-normalized feature vectors
- Output: Predicted fitness score (quality of the trade signal)
- Serialized to `model.joblib` for inference

### 4. Trade Execution
The trading layer (`trading/main.py`) is deployed as Google Cloud Functions. It loads the trained model, preprocesses incoming Reddit posts, and filters high-confidence predictions to place orders via the Investopedia Simulator API (`trading/investopedia_simulator_api/`).

The `InvestopediaApi` class handles:
- Session management (login/cookie persistence via singleton)
- Portfolio fetching (HTML parsing of Investopedia pages)
- Stock and options trading (buy/sell/short/cover)
- Rate limiting (6 requests per 20 seconds)
- Order types: MARKET, LIMIT, STOP, STOP_LIMIT
- Durations: DAY, GTC, GTD, EOD, OnOpen, OnClose

### 5. Dashboard
The React frontend (`hivemind-web-main/`) polls Google Cloud Functions endpoints and displays:
- Real-time portfolio value and cash balance
- Performance chart vs S&P 500 benchmark
- Current stock holdings with cost basis and P&L
- Pending/open orders
- Live r/WallStreetBets post feed for context

## Data Flow

```
Reddit Stream (PRAW)
    ↓
MongoDB (raw: WSB-data.historical-data)
    ↓
Comment Extraction + Text Cleaning
    ↓
Ticker Extraction + Sentiment Scoring
    ↓
5-day Price Lookup (yfinance) → Fitness Label
    ↓
MongoDB (processed: WSB.historical)
    ↓
Feature Vectorization + Normalization
    ↓
MongoDB (vectors: WSB.vectors / WSB.inputs)
    ↓
MLPRegressor Training → model.joblib
    ↓
Cloud Function: Inference on new posts
    ↓
Trade Execution (Investopedia API)
    ↓
Dashboard Monitoring (React)
```

## Setup & Deployment

### Prerequisites
- Python 3.8+
- Node.js 12+
- MongoDB instance
- Reddit API credentials (PRAW)
- Investopedia Simulator account
- Google Cloud Platform project (for deployment)
- Docker + Kubernetes (for producer)

### Environment Variables

**Reddit Producer** (Kubernetes secrets):
```
CLIENT_ID          # Reddit API client ID
CLIENT_SECRET      # Reddit API client secret
MONGODB_SERVICE_HOST
MONGODB_SERVICE_PORT
MONGO_ROOT_USERNAME
MONGO_ROOT_PASSWORD
```

**Trading Service**:
```
username           # Investopedia account username
password           # Investopedia account password
```

### Installation

**Backend services:**
```bash
# Reddit Producer
cd hivemind-core-main/reddit-producer
pip install -r requirements.txt
python producer.py

# Data Processing
cd hivemind-core-main/data
pip install -r requirements.txt
python process.py

# ML Pipeline
cd hivemind-core-main/ml/model
pip install -r requirements.txt
python preprocess.py   # Build feature vectors
python model.py        # Train the model

# Trading (local)
cd hivemind-core-main/trading
bash install_investopedia_api.sh
pip install -r requirements.txt
```

**Frontend:**
```bash
cd hivemind-web-main
npm install
npm start            # Development
npm run build        # Production build
```

### Kubernetes Deployment (Reddit Producer)
```bash
cd hivemind-core-main/reddit-producer
gcloud builds submit --config cloudbuild.yaml
kubectl apply -f producer.yaml
```

### Google App Engine (Frontend)
```bash
cd hivemind-web-main
npm run build
gcloud app deploy
```

## MongoDB Schema

**`WSB-data.historical-data`** — Raw Reddit data
```json
{
  "id": "string",
  "title": "string",
  "selftext": "string",
  "score": 0,
  "created_utc": 0,
  "num_comments": 0,
  "upvote_ratio": 0.0,
  "comments": [{ "body": "string", "score": 0, "parent_id": "string" }]
}
```

**`WSB.historical`** — Enriched with ML features
```json
{
  "...raw fields...",
  "pos": 0.0, "neg": 0.0, "neu": 0.0,
  "tickers": ["AAPL", "TSLA"],
  "fitness": 0.42
}
```

**`WSB.vectors`** / **`WSB.inputs`** — Training data
```json
{
  "vector": [0.1, 0.5, 0.3, "...~20 features..."],
  "fitness": 0.42
}
```

## Key Design Decisions

- **Fitness label from price data**: Rather than relying on human-labeled sentiment, the model learns from actual 5-day forward returns, making it self-supervised.
- **Custom WSB lexicon**: Standard sentiment tools miss WallStreetBets slang; the custom `added_words.json` significantly improves signal quality for this domain.
- **Sentence-level sentiment averaging**: Prevents long posts with mixed sentiment from averaging out to neutral.
- **Sigmoid normalization of returns**: Compresses unbounded price returns to [-1, 1], stabilizing training.
- **Investopedia simulator**: Uses a paper trading environment for risk-free backtesting and demonstration.
- **Microservices on GCP**: Each component (producer, functions, frontend) scales independently.

## Limitations

- Investopedia Simulator is web-scraped, not backed by an official API, making it brittle to UI changes.
- Model trained on historical WSB data; performance degrades as community language evolves.
- 5-day fitness window is a simplification; real signal decay and market regime changes are not modeled.
- Cloud Functions trading endpoints use hardcoded trade parameters in the current implementation.

## License

See [trading/investopedia_simulator_api/LICENSE](hivemind-core-main/trading/investopedia_simulator_api/LICENSE) for the Investopedia API component license.
