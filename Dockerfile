#Base Python image 
FROM python:3.12.6

# Install Node.js (usa curl + installa solo ciò che serve)
RUN apt-get update && apt-get install -y curl gnupg \
    && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && npm install -g npm \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

#Helps not exposing warnings on the container
#ENV PYTHONWARNINGS="ignore"

#Helps exposing colorized output
ENV TERM xterm-256color

#Installing pip requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

#Setting up the working directory in our container
WORKDIR /progetto
COPY . /progetto

# Install Node.js dependencies (se c'è un package.json)
RUN if [ -f package.json ]; then npm install; fi

#Exposing port where our container will run
EXPOSE 8000

CMD [ "python", "/progetto/off_chain/main.py" ]

