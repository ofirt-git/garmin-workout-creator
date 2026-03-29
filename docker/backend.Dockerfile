FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY backend/ ./backend/
COPY workout_parser/ ./workout_parser/
COPY garmin_uploader/ ./garmin_uploader/
COPY core/ ./core/

# Set Python path
ENV PYTHONPATH=/app

# Expose port
EXPOSE 8000

# Run migrations and start server
CMD alembic -c backend/alembic.ini upgrade head && \
    uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
