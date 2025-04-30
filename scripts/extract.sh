#!/bin/bash

echo "Extracting Ganache's log..."

# Controlla se Ganache è in esecuzione
docker ps | grep ganache
if [ $? -ne 0 ]; then
  echo "Ganache is not running."
  exit 1
fi

# Stampa i log senza filtro per capire cosa sta succedendo
docker-compose logs ganache

# Estrai i log cercando le righe giuste
docker-compose logs ganache | grep -A 50 "Available Accounts\|Private Keys" > accounts.txt

# Controlla se accounts.txt contiene dati
if [ -s accounts.txt ]; then
  echo "All the local information for registration purpose are extracted in accounts.txt"
else
  echo "No relevant log entries found."
fi
