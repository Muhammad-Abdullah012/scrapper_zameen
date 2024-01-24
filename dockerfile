FROM python:3

WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app/

RUN pip install --upgrade pip
# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install playwright
RUN playwright install
RUN playwright install-deps


CMD ["python3", "cronjob.py"]
