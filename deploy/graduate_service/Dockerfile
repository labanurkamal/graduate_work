FROM python:3.10-slim

WORKDIR /opt/app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/opt/app/src/

COPY assistant/requirements.txt requirements.txt
RUN pip install --upgrade pip --no-cache-dir \
    && pip install --no-cache-dir -r requirements.txt

COPY assistant/ .

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]