# Official ubuntu image.
FROM ubuntu:19.04

# Install Firefox & python pip
RUN apt-get update && apt-get install -y firefox wget python3-pip

# Install Chrome
# RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
# RUN dpkg -i google-chrome-stable_current_amd64.deb; apt-get -fy install

# Install Python dependencies.
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

# Copy local code to the container image.
ENV APP_HOME /app
WORKDIR $APP_HOME

COPY . .

COPY geckodriver /bin/
# Run the web service on container startup
# Here we use the gunicorn
CMD exec gunicorn --bind :$PORT --workers 1 --threads 1 main:app