# Coffee: Smart POS & Predictive Forecast Management System

An intelligent coffee shop management and retail analytics system built with Django and scikit-learn. The platform combines catalog management and point-of-sale inventory operations with pre-trained machine learning models for demand forecasting, revenue estimation, and inventory level prediction.

---

## System Overview

Coffee integrates transactional retail workflows with predictive intelligence. Rather than relying solely on historical spreadsheets, the system loads serialized scikit-learn predictive pipelines to assist cafe managers in scheduling production, calculating restock quantities, and projecting revenue based on seasonal, temporal, and product-level indicators.

### Key Capabilities

- **Predictive Analytics Suite (`core/ml_models/`):**
  - **Demand Forecasting (`model1_demand_forecast.pkl`):** Estimates upcoming order volume and customer foot-traffic patterns.
  - **Revenue Forecasting (`model2_revenue_forecast.pkl`):** Projects gross income across defined planning horizons.
  - **Inventory Forecasting (`model3_inventory_forecast.pkl`):** Calculates ingredient and stock run-rate to prevent stockouts and waste.
- **Product & Catalog Management (`products/`):** Model hierarchy supporting dynamic pricing, categorized menu hierarchies, and image upload handlers.
- **Automated Database Seeding (`product_category_seeder.py`):** Standalone data seeder to hydrate categories and product menus into SQLite/PostgreSQL.
- **Media Asset Pipeline:** Dedicated media serving configuration for uploaded product photography and promotional assets.

---

## Tech Stack

- **Backend Framework:** Django (Python 3.13 / 3.11+)
- **Machine Learning & Analytics:** scikit-learn, joblib / pickle, NumPy, pandas
- **Database:** SQLite (Default for development) / PostgreSQL-ready
- **Frontend Layer:** Django Templates, HTML5, CSS3, JavaScript
- **Static & Media Asset Handling:** Django Staticfiles, Pillow (image processing)

---

## Repository Structure

```text
Coffee/
├── Coffee/                        # Root Django project configuration
│   ├── asgi.py                    # ASGI server entry point
│   ├── settings.py                # Installed apps, database, and media configurations
│   ├── urls.py                    # Master URL routing table
│   ├── views.py                   # Root project endpoints
│   └── wsgi.py                    # WSGI deployment hook
├── core/                          # Analytics & dashboard application
│   ├── migrations/                # Database migrations for core models
│   ├── ml_models/                 # Serialized scikit-learn predictive pipelines
│   │   ├── model1_demand_forecast.pkl
│   │   ├── model2_revenue_forecast.pkl
│   │   └── model3_inventory_forecast.pkl
│   ├── admin.py                   # Core model administration
│   ├── apps.py                    # App configuration
│   ├── models.py                  # Analytical event and logging entities
│   ├── tests.py                   # Unit and integration test suite
│   └── views.py                   # ML model inference endpoints & dashboard
├── products/                      # Product and category catalog application
│   ├── migrations/                # Schema changes (pricing, images, categories)
│   ├── admin.py                   # Catalog administration interface
│   ├── apps.py                    # App configuration
│   ├── models.py                  # Product, Category, and Inventory models
│   └── views.py                   # Menu browsing and management views
├── media/                         # Uploaded product thumbnails and banners
│   └── products/
├── db.sqlite3                     # Local development database
├── manage.py                      # Django command-line utility
└── product_category_seeder.py     # Database population script
