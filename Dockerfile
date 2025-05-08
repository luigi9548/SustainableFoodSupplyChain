#Base Python image 
FROM python:3.12.6

# Install Node.js
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get update && apt-get install -y nodejs \
    && npm install -g npm

#Helps not exposing warnings on the container
ENV PYTHONWARNINGS="ignore"

#Helps exposing colorized output
ENV TERM xterm-256color

#Installing pip requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

#Setting up the working directory in our container
WORKDIR /progetto
COPY . /progetto

# Install Node.js dependencies
RUN npm install

# Install Hardhat 
RUN npx hardhat compile

#Exposing port where our container will run
EXPOSE 8000

CMD [ "python", "/progetto/off_chain/main.py" ]

