# 📈 NSE FNO Backend  
**Production-grade backend system for NSE Futures & Options market analysis and algorithmic trading**

---

## 🚀 Overview

NSE FNO Backend is a high-performance backend application built with **FastAPI** for analyzing and trading National Stock Exchange (NSE) Futures and Options instruments.

It provides a robust infrastructure for:

- Real-time market data processing  
- Automated technical analysis  
- Trading signal generation  
- WebSocket-based live streaming  
- Algorithmic trading strategy support  

The system integrates with **SmartAPI (Angel One)** for live and historical market data and is designed using **modern async Python patterns** to support low-latency, scalable financial systems.

---

## ✨ Key Features

### 📊 Market Data Management
- Instrument master data ingestion for NSE FNO  
- Real-time and historical OHLC candle support  
- Multi-timeframe candle construction  
- Futures and Options (CE/PE) handling  
- Automated trading universe management with liquidity filtering  

### 🤖 Signal Processing
- Automated trading signal generation  
- Signal deduplication and confidence scoring  
- Historical signal storage and evaluation  
- Support for multiple signal types (buy, sell, neutral)  

### ⚡ Real-Time Capabilities
- WebSocket streaming for live market feeds  
- Asynchronous real-time scanning engine  
- Auto reconnection & heartbeat handling  
- High-frequency data processing  

### 📐 Technical Analysis Engine
- Support & resistance detection  
- Trend identification using moving averages  
- Breakout and pattern recognition  
- Multi-indicator signal confirmation  

### 🔌 API & Integrations
- RESTful APIs for all core operations  
- SmartAPI integration for market access  
- Pydantic-based request validation  
- Health monitoring & system metrics  
- CORS-enabled frontend support  

---

## 🏗️ System Architecture

FastAPI Application
│
├── Routers (API Layer)
│ ├── Dashboard, Health
│ ├── Instruments, Market, Signals
│ └── WebSocket Streams
│
├── Services (Business Logic)
│ ├── Candle Builder
│ ├── Real-time Scanner
│ ├── Batch Scanner
│ ├── Level Detection
│ └── Signal Deduplication
│
├── Providers (External Systems)
│ ├── SmartAPI Integration
│ └── WebSocket Provider
│
└── Database Layer
├── SQLAlchemy ORM Models
├── Async Session Manager
└── Market & Signal Storage


---

## 📂 Project Structure

nse-fno-backend/
├── app/
│ ├── main.py # FastAPI entry point
│ ├── config.py # App configuration
│ ├── deps.py # Dependency injection
│ │
│ ├── db/
│ │ ├── models.py # ORM models
│ │ └── session.py # Async DB session
│ │
│ ├── providers/
│ │ ├── smartapi_provider.py
│ │ └── ws_provider.py
│ │
│ ├── routers/
│ │ ├── dashboard.py
│ │ ├── health.py
│ │ ├── instruments.py
│ │ ├── market.py
│ │ ├── signals.py
│ │ └── ws.py
│ │
│ ├── schemas/
│ │ ├── candles.py
│ │ ├── instruments.py
│ │ └── signals.py
│ │
│ └── services/
│ ├── candle_builder.py
│ ├── realtime_scanner_service.py
│ ├── scanner_service.py
│ ├── levels_service.py
│ ├── signal_deduplicator.py
│ └── universe_service.py
│
├── requirements.txt
├── README.md

## Configuration
Configure the application through environment variables in your .env file:

### Database Configuration
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/nse_fno

### SmartAPI Configuration
SMARTAPI_API_KEY=your_api_key SMARTAPI_CLIENT_ID=your_client_id SMARTAPI_PASSWORD=your_password SMARTAPI_TOTP_SECRET=your_totp_secret

### Application Settings
APP_NAME=NSE FNO Backend DEBUG=True LOG_LEVEL=INFO

### CORS Settings
CORS_ORIGINS=["http://localhost:3000", "http://localhost:8080"]

### WebSocket Settings
WS_HEARTBEAT_INTERVAL=30 WS_RECONNECT_DELAY=5

### Market Data Settings
DEFAULT_CANDLE_INTERVAL=5m MAX_CANDLES_PER_REQUEST=1000

### Signal Generation
SIGNAL_CONFIDENCE_THRESHOLD=0.7 SIGNAL_DEDUP_WINDOW_MINUTES=30

## Key Endpoints
### Health Check
GET /health Returns application health status and database connectivity.

### Instruments
GET /instruments # List all instruments with pagination POST /instruments # Create new instrument GET /instruments/{id} # Get specific instrument PUT /instruments/{id} # Update instrument DELETE /instruments/{id} # Delete instrument

### Market Data
GET /market/candles?symbol={symbol}&interval={interval}&from={date}&to={date} Fetch historical candle data for a specific instrument.

### Signals
GET /signals # List signals with filters POST /signals # Create manual signal GET /signals/{id} # Get signal details POST /signals/generate # Trigger signal generation

### Dashboard
GET /dashboard/summary # Get market summary GET /dashboard/top-signals # Get top-performing signals WebSocket WS /ws/market # Real-time market data stream

## Services

Candle Builder Service
Aggregates tick data or quotes into OHLC candles for various timeframes (1m, 5m, 15m, 1h, 1d). Handles missing data and ensures data integrity.

### Levels Service

Calculates technical support and resistance levels using:

Pivot points (standard, Fibonacci, Camarilla) Moving averages Historical high/low analysis

### Real-time Scanner Service

Monitors live market data asynchronously to identify:

Breakouts above resistance or below support Volume spikes Price patterns (engulfing, hammer, etc.) Trend reversals

### Scanner Service

Performs batch scanning on historical data, typically scheduled to run periodically. Identifies longer-term patterns and opportunities.

### Signal Deduplicator

Prevents duplicate signals by checking:

Same instrument and signal type within a time window Similar confidence scores Overlapping price ranges

### Universe Service

Manages the active instrument universe by:

Fetching latest FNO instruments from NSE/SmartAPI Filtering by liquidity metrics (volume, open interest) Updating instrument master data Handling contract rollovers