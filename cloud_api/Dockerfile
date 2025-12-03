FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y libsndfile1

COPY requirements.txt .

RUN pip install torch --index-url https://download.pytorch.org/whl/cpu
RUN pip install -r requirements.txt

COPY model_cache ./model_cache

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]