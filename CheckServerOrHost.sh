#!/bin/bash

# List of servers (IP addresses or hostnames) to ping
HOSTS=("10.6.26.110" "10.6.4.180" "10.6.28.10")

# Loop through each server and perform the ping
for HOST in "${HOSTS[@]}"; do
  echo -n "Check server $HOST..."
  
  # Perform the ping request (only 1 packet)
  ping -c 1 "$HOST" > /dev/null 2>&1
  
  # Check the result
  if [ $? -eq 0 ]; then
    echo "OK"
  else
    echo "Failed"
  fi
done

# List of URLs to check
URLS=("https://cyberark.indosatooredoo.com/PasswordVault/" "http://10.253.22.214:5555/prov/usermgt/" "10.128.161.140:1521")

# Loop through each URL and perform curl request
for URL in "${URLS[@]}"; do
  echo -n "Check URL $URL... "
  
  # Perform the curl request
  curl -s --head "$URL" | head -n 1 | grep "HTTP/1\.[01] [23].." > /dev/null
  
  # Check the result
  if [ $? -eq 0 ]; then
    echo "OK"
  else
    echo "Failed"
  fi
done
