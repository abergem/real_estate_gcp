FROM python:3.7

# Install Python dependencies.
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

# Copy local code to the container image.
ENV APP_HOME /app
WORKDIR $APP_HOME

COPY . /$APP_HOME

# Run the web service on container startup
CMD exec gunicorn --bind :$PORT --workers 8 --timeout 900 --threads 8 main:app