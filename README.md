# LLM-Powered People Network

A sophisticated platform that leverages Large Language Models to create meaningful connections between people based on their interests, skills, and goals.

Scripts in `scripts/` are for pruning and refining the scraped data.
Use case:
`python submit_batch.py` to process linkedin scrapes.
`python refine_profiles.py BATCH_ID` to run pruning and refinement.
`python retrieve_batch.py BATCH_ID` to download the batch job.

### System Architecture Diagram

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│             │     │             │     │             │
│  Frontend   │────▶│   Backend   │────▶│ LLM Service │
│  (React)    │     │   (FastAPI) │     │             │
│             │◀────│             │◀────│             │
└─────────────┘     └──────┬──────┘     └─────────────┘
                           │
                           ▼
                    ┌─────────────┐     ┌─────────────┐
                    │             │     │             │
                    │ PostgreSQL  │────▶│   Vector    │
                    │  Database   │     │  Database   │
                    │             │◀────│             │
                    └─────────────┘     └─────────────┘
```

## 🚀 Getting Started

### Prerequisites

- Python 3.9+
- Node.js 16+
- PostgreSQL 13+
- Docker and Docker Compose (optional, for containerized setup)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/llm-people-network.git
   cd llm-people-network
   ```

2. Set up the backend:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Set up the frontend:
   ```bash
   cd ../frontend
   npm install
   ```

4. Set up the database:
   ```bash
   # Create PostgreSQL database
   createdb llm_network
   
   # Run migrations
   cd ../backend
   alembic upgrade head
   ```

### Configuration

1. Create a `.env` file in the backend directory:
   ```
   DATABASE_URL=postgresql://username:password@localhost/llm_network
   SECRET_KEY=your_secret_key
   LLM_API_KEY=your_llm_api_key
   ```

2. Create a `.env` file in the frontend directory:
   ```
   REACT_APP_API_URL=http://localhost:8000
   ```

## 💻 Usage

1. Start the backend server:
   ```bash
   cd backend
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   uvicorn app.main:app --reload
   ```

2. Start the frontend development server:
   ```bash
   cd frontend
   npm start
   ```

3. Access the application at `http://localhost:3000`

### Docker Setup (Alternative)

1. Build and start the containers:
   ```bash
   docker-compose up -d
   ```

2. Access the application at `http://localhost:3000`

## 📚 API Documentation

API documentation is available at `http://localhost:8000/docs` when the backend server is running.

Key endpoints include:

- `POST /api/users`: Create a new user
- `GET /api/users/{user_id}`: Get user details
- `GET /api/users/{user_id}/connections`: Get user connections
- `POST /api/connections/recommend`: Get connection recommendations
## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
