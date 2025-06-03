# CAT API

A modern FastAPI-based REST API application for managing categories, states, and monitoring alerts.

## 🚀 Features

- FastAPI-based REST API with OpenAPI documentation
- PostgreSQL database integration
- JWT Authentication
- Database migrations with Alembic
- CORS middleware enabled
- Modular project structure
- API versioning
- Environment-based configuration

## 📋 Prerequisites

- Python 3.12 or higher
- PostgreSQL database
- Git
- WSL or Ubuntu environment

## 🛠️ Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd cat-api
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # For Linux/WSL
# or
.\venv\Scripts\activate  # For Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the project root with the following variables:
```env
POSTGRES_USER=your_postgres_user
POSTGRES_PASSWORD=your_postgres_password
POSTGRES_DB=cat_api_db
POSTGRES_SERVER=localhost
POSTGRES_PORT=5432
SECRET_KEY=your_secret_key  # Generate a secure secret key
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

5. Create the PostgreSQL database:
```bash
sudo -u postgres psql
postgres=# CREATE DATABASE cat_api_db;
postgres=# \q
```

6. Run database migrations:
```bash
alembic upgrade head
```

## 🚀 Running the Application

1. Start the FastAPI server:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

2. Access the API documentation:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 📁 Project Structure

```
cat-api/
├── alembic/              # Database migrations
├── app/
│   ├── api/             # API routes and endpoints
│   │   └── v1/
│   ├── core/            # Core configuration
│   ├── db/              # Database session and configuration
│   ├── models/          # SQLAlchemy models
│   ├── schemas/         # Pydantic schemas
│   └── services/        # Business logic
├── scripts/             # Utility scripts
└── requirements.txt     # Project dependencies
```

## 🔑 Authentication

The API uses JWT Bearer token authentication:
1. Create a user account (if required)
2. Obtain a token from `/api/v1/auth/login`
3. Use the token in the Authorization header: `Bearer <your_token>`

## 🛠️ Available Scripts

- `scripts/add_states.py`: Utility script to populate the database with US states

## 📝 API Endpoints

The API provides the following main endpoints:

- `/api/v1/auth/*`: Authentication endpoints
- `/api/v1/common/states`: State management
- `/api/v1/common/categories`: Category management
- `/api/v1/monitoring/*`: Monitoring and alerts

For detailed API documentation, please refer to the Swagger UI or ReDoc pages.

## 🧪 Running Tests

(Add test instructions when tests are implemented)

## 🤝 Contributing

1. Fork the repository
2. Create a new branch: `git checkout -b feature-name`
3. Make your changes and commit: `git commit -m 'Add feature'`
4. Push to the branch: `git push origin feature-name`
5. Submit a pull request

## 📄 License

(Add license information)
