# Price Insight API

REST API for multi-category price tracking and deal aggregation across e-commerce, travel, real estate, and utilities

## Features

- **Multi-Category Tracking**: E-commerce, travel, real estate, utilities
- **Price Alerts**: Email notifications for price drops and deals
- **User Authentication**: JWT-based auth with welcome emails
- **Export Reports**: PDF/CSV exports for all categories
- **Currency Normalization**: All prices converted to Nigerian Naira
- **Automated Scraping**: Scheduled price monitoring

## Quick Start

```bash
# Clone and setup
git clone https://github.com/Adelodunpeter25/price-insight.git
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
- **Scraping**: httpx + BeautifulSoup4 with rate limiting
- **Scheduling**: APScheduler
