# FROM ubuntu:bionic

# RUN apt-get update && apt-get install -y \
#     python3 python3-pip \
#     fonts-liberation libappindicator3-1 libasound2 libatk-bridge2.0-0 \
#     libnspr4 libnss3 lsb-release xdg-utils libxss1 libdbus-glib-1-2 \
#     curl unzip wget \
#     xvfb

# # install geckodriver and firefox

# RUN GECKODRIVER_VERSION=`curl https://github.com/mozilla/geckodriver/releases/latest | grep -Po 'v[0-9]+.[0-9]+.[0-9]+'` && \
#     wget https://github.com/mozilla/geckodriver/releases/download/$GECKODRIVER_VERSION/geckodriver-$GECKODRIVER_VERSION-linux64.tar.gz && \
#     tar -zxf geckodriver-$GECKODRIVER_VERSION-linux64.tar.gz -C /usr/local/bin && \
#     chmod +x /usr/local/bin/geckodriver && \
#     rm geckodriver-$GECKODRIVER_VERSION-linux64.tar.gz

# RUN FIREFOX_SETUP=firefox-setup.tar.bz2 && \
#     apt-get purge firefox && \
#     wget -O $FIREFOX_SETUP "https://download.mozilla.org/?product=firefox-latest&os=linux64" && \
#     tar xjf $FIREFOX_SETUP -C /opt/ && \
#     ln -s /opt/firefox/firefox /usr/bin/firefox && \
#     rm $FIREFOX_SETUP

FROM python:3.7
RUN apt-get update
RUN apt-get install -y gconf-service libasound2 libatk1.0-0 libcairo2 libcups2 libfontconfig1 libgdk-pixbuf2.0-0 libgtk-3-0 libnspr4 \
     libpango-1.0-0 libxss1 fonts-liberation libappindicator3-1 libnss3 lsb-release xdg-utils

# Font libraries needed for headless
RUN apt-get update && \
    apt-get -qq -y install  libxpm4 libxrender1 libgtk2.0-0 libnss3\ 
       libgconf-2-4  libpango1.0-0 libxss1 libxtst6 fonts-liberation\ 
       libappindicator1 xdg-utils

RUN apt-get -y install \
               xvfb gtk2-engines-pixbuf \
               xfonts-cyrillic xfonts-100dpi xfonts-75dpi xfonts-base xfonts-scalable \
               imagemagick x11-apps zip

# Install Chrome
RUN wget http://dl.google.com/linux/deb/pool/main/g/google-chrome-stable/google-chrome-stable_70.0.3538.77-1_amd64.deb
RUN dpkg -i google-chrome-stable_70.0.3538.77-1_amd64.deb; apt-get -fy install
# RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
# RUN dpkg -i google-chrome-stable_current_amd64.deb; apt-get -fy install

# Install Python dependencies.
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

# Copy local code to the container image.
ENV APP_HOME /app
WORKDIR $APP_HOME

COPY . /$APP_HOME

# Run the web service on container startup
CMD exec gunicorn --bind :$PORT --workers 8 --timeout 900 --threads 1 main:app