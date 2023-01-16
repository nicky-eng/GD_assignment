FROM python:3.8-slim-buster
WORKDIR /app

# Setup requirements
COPY . . 
RUN apt-get update && \
    pip install --upgrade pip && \
    pip install -r requirements.txt 

# Run Flask App
EXPOSE 5000
CMD ["python", "app.py"]