FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
# Copy mock_llm.py to utils
# Ensure the host directory structure maps correctly or we just copy it here if needed.
# Since it needs utils.mock_llm, we expect utils/mock_llm.py to be in the folder.
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
