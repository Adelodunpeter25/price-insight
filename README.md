# Price Insight Platform

Multi-category deal aggregation platform that tracks prices across e-commerce, travel, real estate, and utilities.

## Features

- **Multi-Category Tracking**: E-commerce, travel, real estate, utilities
- **Price Alerts**: Email notifications for price drops and deals
- **User Authentication**: JWT-based auth with welcome emails
- **Export Reports**: PDF/CSV exports for all categories
- **Currency Normalization**: All prices in Nigerian Naira
- **Automated Scraping**: Scheduled price monitoring

## Quick Start

```bash
# Clone and setup
git clone <repo-url>
cd price-insight/backend

# Install dependencies
uv sync

# Setup environment
cp .env.example .env
# Edit .env with your settings

# Run migrations
make migrate

# Start server
make dev
```

## API Endpoints

- **Auth**: `/api/auth/register`, `/api/auth/login`
- **E-commerce**: `/api/ecommerce/products`, `/api/ecommerce/deals`
- **Travel**: `/api/travel/flights`, `/api/travel/hotels`
- **Real Estate**: `/api/real_estate/properties`
- **Utilities**: `/api/utilities/services`

## Environment Variables

```env
DATABASE_URL=postgresql+asyncpg://user:pass@host/db
REDIS_URL=redis://localhost:6379
JWT_SECRET_KEY=your-secret-key
EXCHANGE_RATE_API_KEY=your-api-key
RESEND_API_KEY=your-resend-key
```

## Commands

```bash
make dev          # Run development server
make migrate      # Generate and apply migrations
make test         # Run tests
make lint         # Run linter
make format       # Format code
```

## Tech Stack

- **Backend**: FastAPI, SQLAlchemy, PostgreSQL
- **Auth**: JWT with Argon2 hashing
- **Email**: Resend API with HTML templates
- **Scraping**: aiohttp with rate limiting
- **Scheduling**: APScheduler