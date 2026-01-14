## NSE FNO Backend
A comprehensive backend application built with FastAPI for analyzing and trading National Stock Exchange (NSE) Futures and Options (FNO) instruments. This system provides real-time market data processing, automated signal generation, technical analysis, and WebSocket-based live updates for algorithmic trading strategies.
Table of Contents

Overview
Key Features
Architecture
Project Structure
Configuration
API Documentation
Services

# Overview
The NSE FNO Backend is designed for traders and quantitative analysts who need a robust infrastructure for processing derivatives market data. It integrates with SmartAPI (Angel One's trading platform) to fetch live and historical data, performs technical analysis to identify trading opportunities, and delivers signals through both REST APIs and WebSocket connections.
The application is built with modern async Python patterns, ensuring high performance and scalability for real-time market data processing.

# Key Features
Market Data Management

Fetch and store instrument master data for NSE FNO segments
Real-time and historical OHLC (Open, High, Low, Close) candle data
Multi-timeframe candle construction from tick data
Support for futures and options (Call/Put) instruments
Automated universe management with liquidity filtering

Signal Processing

Automated trading signal generation using technical indicators
Signal deduplication to avoid redundant alerts
Confidence scoring for each signal
Historical signal tracking and performance analysis
Support for multiple signal types (buy, sell, neutral)

Real-Time Capabilities

WebSocket streaming for live market data
Real-time market scanning for trading opportunities
Asynchronous processing for high-frequency updates
Connection lifecycle management with automatic reconnection

Technical Analysis

Support/resistance level calculation using pivot points
Moving average-based trend identification
Breakout and pattern recognition
Multi-indicator signal confirmation

API & Integration

RESTful API endpoints for all major operations
SmartAPI integration for data sourcing
Comprehensive health monitoring
CORS support for web-based frontends
Request validation using Pydantic schemas

# Architecture
The application follows a clean, layered architecture:

┌─────────────────────────────────────────┐
│         FastAPI Application             │
├─────────────────────────────────────────┤
│  Routers (API Endpoints)                │
│  - Dashboard, Health, Instruments       │
│  - Market Data, Signals, WebSocket      │
├─────────────────────────────────────────┤
│  Services (Business Logic)              │
│  - Signal Generation & Deduplication    │
│  - Real-time & Batch Scanning           │
│  - Candle Building, Level Calculation   │
├─────────────────────────────────────────┤
│  Providers (External Integration)       │
│  - SmartAPI Provider                    │
│  - WebSocket Provider                   │
├─────────────────────────────────────────┤
│  Database Layer (SQLAlchemy ORM)        │
│  - Models: Instrument, Signal, Candle   │
│  - Async Session Management             │
└─────────────────────────────────────────┘

# Project Structure

nse-fno-backend/
├── app/
│   ├── __init__.py              # Package initialization
│   ├── config.py                # Application configuration and settings
│   ├── deps.py                  # Dependency injection utilities
│   ├── main.py                  # FastAPI app entry point
│   │
│   ├── db/
│   │   ├── __init__.py          # Database package initialization
│   │   ├── models.py            # SQLAlchemy ORM models
│   │   └── session.py           # Database session management
│   │
│   ├── providers/
│   │   ├── __init__.py          # Providers package initialization
│   │   ├── smartapi_provider.py # SmartAPI integration
│   │   └── ws_provider.py       # WebSocket provider
│   │
│   ├── routers/
│   │   ├── __init__.py          # Routers package initialization
│   │   ├── dashboard.py         # Dashboard endpoints
│   │   ├── health.py            # Health check endpoints
│   │   ├── instruments.py       # Instrument CRUD operations
│   │   ├── market.py            # Market data endpoints
│   │   ├── signals.py           # Signal management endpoints
│   │   └── ws.py                # WebSocket endpoints
│   │
│   ├── schemas/
│   │   ├── __init__.py          # Schemas package initialization
│   │   ├── candles.py           # Candle data schemas
│   │   ├── instruments.py       # Instrument schemas
│   │   └── signals.py           # Signal schemas
│   │
│   ├── scripts/                 # Utility scripts
│   │
│   └── services/
│       ├── __init__.py          # Services package initialization
│       ├── candle_builder.py    # Candle construction service
│       ├── levels_service.py    # Support/resistance calculation
│       ├── realtime_scanner_service.py  # Live market scanning
│       ├── scanner_service.py   # Batch scanning service
│       ├── signal_deduplicator.py # Signal deduplication
│       └── universe_service.py  # Instrument universe management
│
├── requirements.txt             # Python dependencies
├── .env                         # Environment variables (not in repo)
└── README.md                    # This file

# Configuration
Configure the application through environment variables in your .env file:

# Database Configuration
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/nse_fno

# SmartAPI Configuration
SMARTAPI_API_KEY=your_api_key
SMARTAPI_CLIENT_ID=your_client_id
SMARTAPI_PASSWORD=your_password
SMARTAPI_TOTP_SECRET=your_totp_secret

# Application Settings
APP_NAME=NSE FNO Backend
DEBUG=True
LOG_LEVEL=INFO

# CORS Settings
CORS_ORIGINS=["http://localhost:3000", "http://localhost:8080"]

# WebSocket Settings
WS_HEARTBEAT_INTERVAL=30
WS_RECONNECT_DELAY=5

# Market Data Settings
DEFAULT_CANDLE_INTERVAL=5m
MAX_CANDLES_PER_REQUEST=1000

# Signal Generation
SIGNAL_CONFIDENCE_THRESHOLD=0.7
SIGNAL_DEDUP_WINDOW_MINUTES=30

## Key Endpoints
# Health Check
GET /health
Returns application health status and database connectivity.
# Instruments
GET    /instruments          # List all instruments with pagination
POST   /instruments          # Create new instrument
GET    /instruments/{id}     # Get specific instrument
PUT    /instruments/{id}     # Update instrument
DELETE /instruments/{id}     # Delete instrument
# Market Data
GET /market/candles?symbol={symbol}&interval={interval}&from={date}&to={date}
Fetch historical candle data for a specific instrument.
# Signals
GET  /signals                # List signals with filters
POST /signals                # Create manual signal
GET  /signals/{id}           # Get signal details
POST /signals/generate       # Trigger signal generation
# Dashboard
GET /dashboard/summary       # Get market summary
GET /dashboard/top-signals   # Get top-performing signals
WebSocket
WS /ws/market                # Real-time market data stream

## Services
# Candle Builder Service
Aggregates tick data or quotes into OHLC candles for various timeframes (1m, 5m, 15m, 1h, 1d). Handles missing data and ensures data integrity.

# Levels Service
Calculates technical support and resistance levels using:

Pivot points (standard, Fibonacci, Camarilla)
Moving averages
Historical high/low analysis

# Real-time Scanner Service
Monitors live market data asynchronously to identify:

Breakouts above resistance or below support
Volume spikes
Price patterns (engulfing, hammer, etc.)
Trend reversals

# Scanner Service
Performs batch scanning on historical data, typically scheduled to run periodically. Identifies longer-term patterns and opportunities.

# Signal Deduplicator
Prevents duplicate signals by checking:

Same instrument and signal type within a time window
Similar confidence scores
Overlapping price ranges

# Universe Service
Manages the active instrument universe by:

Fetching latest FNO instruments from NSE/SmartAPI
Filtering by liquidity metrics (volume, open interest)
Updating instrument master data
Handling contract rollovers