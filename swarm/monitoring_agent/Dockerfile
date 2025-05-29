FROM python:3.12.3-slim

WORKDIR /app

# copy files 
COPY requirements_docker.txt .
RUN pip install --no-cache-dir -r requirements_docker.txt

# copy app
COPY app.py .

# open port 5555
EXPOSE 5000

# launch
CMD ["python", "app.py"]