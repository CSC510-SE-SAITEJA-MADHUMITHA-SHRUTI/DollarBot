#!/bin/bash

# Install required packages
pip3 install -r requirements.txt

# Extract API token from user.properties
api_token=$(grep "api_token" user.properties | cut -d'=' -f2)

# Initialize flag variable correctly
flag="old"

echo "Checking for API Token..."
if [ -z "$api_token" ]; then
  echo "Welcome to DollarBot!"
  echo "Follow the steps below to generate an API token to uniquely identify your personal DollarBot. Then, proceed to enter the generated token when prompted to run DollarBot."
  echo
  echo "1. Download and install the Telegram desktop application for your system from the following site: https://desktop.telegram.org/"
  echo "2. Once you log in to your Telegram account, search for 'BotFather' in Telegram. Click on 'Start' --> enter the following command:"
  echo "/newbot"
  echo "3. Follow the instructions on screen and choose a name for your bot. Post this, select a username for your bot that ends with 'bot' (as per the instructions on your Telegram screen)."
  echo "4. BotFather will now confirm the creation of your bot and provide a TOKEN to access the HTTP API - copy this token."
  echo
  echo "Do you want to add your API token now? (Y/n)"
  read option

  if [[ "$option" == 'y' || "$option" == 'Y' ]]; then
    flag="new"  # Correctly set the flag variable
    echo "Enter the copied token: "
    read api_token
    echo "api_token=$api_token" >> user.properties  # Append the token to the properties file
  fi
fi

if [ -n "$api_token" ]; then
    echo "Thanks for choosing DollarBot! Starting DollarBot with new API token..." 
    python3 code/code.py
fi
