# QuantKTP - Statistical Arbitrage Trading Platform

A full-stack application for correlation analysis and statistical arbitrage trading, built with FastAPI (backend) and Next.js (frontend).

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- npm or yarn

### Backend Setup

```bash
cd backend
pip install -r requirements.txt
python main.py
```

Backend runs on `http://localhost:8000`

### Frontend Setup

```bash
cd frontend
npm install --legacy-peer-deps
npm run dev
```

Frontend runs on `http://localhost:3000`

## 📁 Project Structure

```
ktp-project-final/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── requirements.txt     # Python dependencies
│   ├── Procfile             # Railway deployment config
│   ├── railway.json         # Railway configuration
│   └── research/            # Jupyter notebooks and research
│
├── frontend/
│   ├── app/                 # Next.js app directory
│   ├── components/          # React components
│   │   └── dashboard/
│   │       └── correlation-charts/  # Correlation visualization
│   ├── package.json         # Node dependencies
│   └── vercel.json          # Vercel deployment config
│
└── DEPLOYMENT.md            # Detailed deployment guide
```

## 🌐 Deployment

### Backend (Railway)

1. Connect your GitHub repo to Railway
2. Set root directory to `backend/`
3. Add environment variables:
   - `CORS_ORIGINS` - Your Vercel frontend URL
   - `KALSHI_API_BASE` - Kalshi API base URL
   - `PORT` - Railway sets this automatically

### Frontend (Vercel)

1. Connect your GitHub repo to Vercel
2. Set root directory to `frontend/`
3. Add environment variable:
   - `NEXT_PUBLIC_API_URL` - Your Railway backend URL
4. Set build command: `npm install --legacy-peer-deps && npm run build`

See [DEPLOYMENT.md](./DEPLOYMENT.md) for detailed instructions.

## 📊 Features

- **Correlation Analysis**: Calculate Pearson correlation between two market tickers
- **Time Series Visualization**: Display X and Y time series for overlapping periods
- **Residuals Analysis**: Visualize residuals from linear regression model
- **Trading Signals**: Identify trading opportunities based on nonzero residuals

## 🔧 API Endpoints

- `GET /` - API information
- `GET /health` - Health check
- `GET /api/v1/correlation` - Get correlation data and charts
- `GET /docs` - Interactive API documentation (Swagger UI)
- `GET /redoc` - Alternative API documentation

## 📝 Environment Variables

### Backend

- `CORS_ORIGINS` - Comma-separated list of allowed origins
- `KALSHI_API_BASE` - Kalshi API base URL
- `PORT` - Server port (default: 8000)
- `HOST` - Server host (default: 0.0.0.0)

### Frontend

- `NEXT_PUBLIC_API_URL` - Backend API URL

## 🛠️ Development

### Running Locally

1. Start backend: `cd backend && python main.py`
2. Start frontend: `cd frontend && npm run dev`
3. Open `http://localhost:3000`

### Testing API

Visit `http://localhost:8000/docs` for interactive API documentation.

## 📄 License

MIT

