"""
File: code.py
Author: Vyshnavi Adusumelli, Tejaswini Panati, Harshavardhan Bandaru
Date: October 01, 2023
Description: File contains Telegram bot message handlers and their associated functions.

Copyright (c) 2023

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS," WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""


#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
import telebot
import time
import helper
import edit
import history
import pdf
import display
import estimate
import delete
import add
import budget
import analytics
import predict
import updateCategory
import weekly
import monthly
import sendEmail
import voice
import add_recurring
import os
from pdf import create_summary_pdf
from datetime import datetime
from jproperties import Properties
from telebot import types
from telegram_bot_calendar import DetailedTelegramCalendar
from add import cal

configs = Properties()

with open("user.properties", "rb") as read_prop:
    configs.load(read_prop)

api_token = str(configs.get("api_token").data)

bot = telebot.TeleBot(api_token)

telebot.logger.setLevel(logging.INFO)

option = {}
user_list = {}

# === Documentation of code.py ===

# Define listener for requests by user
def listener(user_requests):
    """
    listener(user_requests): Takes 1 argument user_requests and logs all user
    interaction with the bot including all bot commands run and any other issue logs.
    """
    for req in user_requests:
        if req.content_type == "text":
            print(
                "{} name:{} chat_id:{} \nmessage: {}\n".format(
                    str(datetime.now()),
                    str(req.chat.first_name),
                    str(req.chat.id),
                    str(req.text),
                )
            )

    message = (
        ("I'm here to help, but I can only respond to specific commands for now.\n\n"
    "To get started, try typing a command that begins with '/'.\n"
    "If you're unsure, type /faq or /help to see a list of available commands.\n\n"
    "Thanks for understanding! 😊")
    )

    try:
        helper.read_json()
        global user_list
        chat_id = user_requests[0].chat.id

        if user_requests[0].text[0] != "/":
            bot.send_message(chat_id, message)
    except Exception:
        pass

bot.set_update_listener(listener)

@bot.message_handler(commands=["help"])
def help(m):

    helper.read_json()
    global user_list
    chat_id = m.chat.id
    message = "Here are the commands you can use: \n"
    commands = helper.getCommands()
    for c in commands:
        message += "/" + c + ", "
    message += "\nUse /menu for detailed instructions about these commands."
    bot.send_message(chat_id, message)


@bot.message_handler(commands=["faq"])
def faq(m):

    helper.read_json()
    global user_list
    chat_id = m.chat.id

    faq_message = (
        ('"What does this bot do?"\n'
         ">> DollarBot lets you manage your expenses so you can always stay on top of them! \n\n"
         '"How can I add an epxense?" \n'
         ">> Type /add, then select a category to type the expense. \n\n"
         '"Can I see history of my expenses?" \n'
         ">> Yes! Use /analytics to get a graphical display, or /history to view detailed summary.\n\n"
         '"I added an incorrect expense. How can I edit it?"\n'
         ">> Use /edit command. \n\n"
         '"Can I check if my expenses have exceeded budget?"\n'
         ">> Yes! Use /budget and then select the view category. \n\n")
    )
    bot.send_message(chat_id, faq_message)

# defines how the /start and /help commands have to be handled/processed
@bot.message_handler(commands=["start", "menu"])
def start_and_menu_command(m):
    helper.read_json()
    global user_list
    chat_id = m.chat.id
    text_intro = (
        "*Welcome to the Dollar Bot!* \n"
        "DollarBot can track all your expenses with simple and easy-to-use commands :) \n"
        "Here is the complete menu:\n\n"
    )

    commands = helper.getCommands()
    keyboard = types.InlineKeyboardMarkup()

    for c in commands:  
        # generate help text out of the commands dictionary defined at the top
        text_intro += "/" + c + ": "
        text_intro += commands[c] + "\n\n"
    bot.send_message(chat_id, text_intro)
    return True

# code.py

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    """
    Handles button clicks and executes the corresponding command actions.
    """
    response_text = ""  # Initialize an empty response text

    # Check which command was clicked and perform the corresponding action
    if call.data == "summary":
        response_text = "Here is your summary report."
    elif call.data == "report":
        response_text = "Here is your detailed report."
    elif call.data == "socialmedia":
        response_text = "Share your summary on social media!"
    else:
        response_text = "Unknown command received."

    # Additional command handling (if needed)
    if call.data == "help":
        response_text = help(call.message)
    elif call.data == "pdf":
        response_text = command_pdf(call.message)
    elif call.data == "add":
        response_text = command_add(call.message)
    elif call.data == "menu":
        response_text = start_and_menu_command(call.message)
    elif call.data == "add_recurring":
        response_text = command_add_recurring(call.message)
    elif call.data == "analytics":
        response_text = command_analytics(call.message)
    elif call.data == "predict":
        response_text = command_predict(call.message)
    elif call.data == "history":
        response_text = command_history(call.message)
    elif call.data == "delete":
        response_text = command_delete(call.message)
    elif call.data == "display":
        response_text = command_display(call.message)
    elif call.data == "edit":
        response_text = command_edit(call.message)
    elif call.data == "budget":
        response_text = command_budget(call.message)
    elif call.data == "updateCategory":
        response_text = command_updateCategory(call.message)
    elif call.data == "weekly":
        response_text = command_weekly(call.message)
    elif call.data == "monthly":
        response_text = command_monthly(call.message)
    elif call.data == "sendEmail":
        response_text = command_sendEmail(call.message)
    elif call.data == "faq":
        response_text = faq(call.message)
    elif DetailedTelegramCalendar.func()(call):  # If it’s a calendar action
        cal(call, bot)
        response_text = "Calendar action processed."
    else:
        response_text = "Command not recognized."

    # Acknowledge the button press
    bot.answer_callback_query(call.id)

    # Send the response back to the user
    if response_text:
        bot.send_message(call.message.chat.id, response_text, parse_mode='Markdown')
    else:
        bot.send_message(call.message.chat.id, "An error occurred. Please try again.", parse_mode='Markdown')



# defines how the /add command has to be handled/processed
@bot.message_handler(commands=["add"])
def command_add(message):
    """
    command_add(message) Takes 1 argument message which contains the message from
    the user along with the chat ID of the user chat. It then calls add.py to run to execute
    the add functionality. Commands used to run this: commands=['add']
    """
    add.run(message, bot)

# defines how the /weekly command has to be handled/processed
@bot.message_handler(commands=["weekly"])
def command_weekly(message):
    """
    command_weekly(message) Takes 1 argument message which contains the message from
    the user along with the chat ID of the user chat. It then calls weekly.py to run to execute
    the weekly analysis functionality. Commands used to run this: commands=['weekly']
    """
    weekly.run(message, bot)

@bot.message_handler(content_types=['voice'])
def handle_voice(message):
    """
    handle_voice(message) Takes 1 argument message which contains the message from
    the user along with the chat ID of the user chat. It then calls voice.py to run to execute
    voice recognition functionality. Voice invkes this command
    """
    voice.run(message, bot)

# defines how the /monthly command has to be handled/processed
@bot.message_handler(commands=["monthly"])
def command_monthly(message):
    """
    command_monthly(message) Takes 1 argument message which contains the message from
    the user along with the chat ID of the user chat. It then calls monthly.py to run to execute
    the monthly analysis functionality. Commands used to run this: commands=['monthly']
    """
    monthly.run(message, bot)

#handles add_recurring command
@bot.message_handler(commands=['add_recurring'])
def command_add_recurring(message):
    add_recurring.run(message, bot)

# handles pdf command
@bot.message_handler(commands=["pdf"])
def command_pdf(message):
    """
    command_history(message): Takes 1 argument message which contains the message from
    the user along with the chat ID of the user chat. It then calls pdf.py to run to execute
    the add functionality. Commands used to run this: commands=['pdf']
    """
    pdf.run(message, bot)

#handles updateCategory command
@bot.message_handler(commands=["updateCategory"])
def command_updateCategory(message):
    """
    command_updateCategory(message): Takes 1 argument message which contains the message from
    the user along with the chat ID of the user chat. It then calls updateCategory.py to run to execute
    the updateCategory functionality. Commands used to run this: commands=['updateCategory']
    """
    updateCategory.run(message, bot)

# function to fetch expenditure history of the user
@bot.message_handler(commands=["history"])
def command_history(message):
    """
    command_history(message): Takes 1 argument message which contains the message from
    the user along with the chat ID of the user chat. It then calls history.py to run to execute
    the add functionality. Commands used to run this: commands=['history']
    """
    history.run(message, bot)

# function to fetch expenditure history of the user
@bot.message_handler(commands=["sendEmail"])
def command_sendEmail(message):
    """
    command_history(message): Takes 1 argument message which contains the message from
    the user along with the chat ID of the user chat. It then calls sendEmail.py to run to execute
    the sending an email of the expense history. Commands used to run this: commands=['sendEmail']
    """
    sendEmail.run(message, bot)

# function to edit date, category or cost of a transaction
@bot.message_handler(commands=["edit"])
def command_edit(message):
    """
    command_edit(message): Takes 1 argument message which contains the message from
    the user along with the chat ID of the user chat. It then calls edit.py to run to execute
    the add functionality. Commands used to run this: commands=['edit']
    """
    edit.run(message, bot)

# function to display total expenditure
@bot.message_handler(commands=["display"])
def command_display(message):
    """
    command_display(message): Takes 1 argument message which contains the message from the user
    along with the chat ID of the user chat. It then calls display.py to run to execute the add functionality.
    Commands used to run this: commands=['display']
    """
    display.run(message, bot)

# function to estimate future expenditure
@bot.message_handler(commands=["estimate"])
def command_estimate(message):
    """
    command_estimate(message): Takes 1 argument message which contains the message from the user
    along with the chat ID of the user chat. It then calls delete.py to run to execute the add functionality.
    Commands used to run this: commands=['estimate']
    """
    estimate.run(message, bot)

# handles "/delete" command
@bot.message_handler(commands=["delete"])
def command_delete(message):
    """
    command_delete(message): Takes 1 argument message which contains the message from the user
    along with the chat ID of the user chat. It then calls delete.py to run to execute the add functionality.
    Commands used to run this: commands=['display']
    """
    delete.run(message, bot)

# handles budget command
@bot.message_handler(commands=["budget"])
def command_budget(message):
    budget.run(message, bot)

# handles analytics command
@bot.message_handler(commands=["analytics"])
def command_analytics(message):
    """
    command_analytics(message): Take an argument message with content and chat ID. Calls analytics to 
    run analytics. Commands to run this commands=["analytics"]
    """
    analytics.run(message, bot)

# handles predict command
@bot.message_handler(commands=["predict"])
def command_predict(message):
    """
    command_predict(message): Take an argument message with content and chat ID. Calls predict to 
    analyze budget and spending trends and suggest a future budget. Commands to run this commands=["predict"]
    """
    predict.run(message, bot)

# handles /summary command
@bot.message_handler(commands=["summary"])
def command_summary(message):
    """
    command_summary(message): Takes the message with the user's chat ID and 
    calls the helper function to generate the summary.
    """
    helper.generate_summary(message.chat.id, bot)

# handles /report command
@bot.message_handler(commands=["report"])
def command_report(message):
    """
    Handles the /report command, requesting a date range for the report.
    """
    chat_id = message.chat.id
    bot.send_message(chat_id, "Please enter the date range for the report (format: YYYY-MM-DD to YYYY-MM-DD).")    

    @bot.message_handler(func=lambda msg: validate_date_range(msg.text))
    def handle_date_range(msg):
        date_range = msg.text.split("to")
        start_date, end_date = date_range[0].strip(), date_range[1].strip()
        helper.generate_report(chat_id, bot, start_date, end_date)

def validate_date_range(text):
    # Implement a proper date validation logic
    return "-" in text and "to" in text
 

    # Listen for the next message containing the date range
    @bot.message_handler(func=lambda msg: "-" in msg.text and "to" in msg.text)
    def handle_date_range(msg):
        date_range = msg.text.split("to")
        if len(date_range) == 2:
            start_date = date_range[0].strip()
            end_date = date_range[1].strip()
            # Generate the report and send it
            helper.generate_report(chat_id, bot, start_date, end_date)
        else:
            bot.send_message(chat_id, "Invalid format. Please try again using 'YYYY-MM-DD to YYYY-MM-DD'.")

import urllib.parse

@bot.message_handler(commands=["socialmedia"])
def command_socialmedia(message):
    """
    command_socialmedia(message): Generates a shareable link for the user's expense summary that can
    be posted on social media platforms.
    """
    chat_id = message.chat.id
    
    # Generate or fetch the link to the user's expense summary
    summary_link = generate_shareable_link(chat_id)
    
    if summary_link:
        # URL encode the summary link
        encoded_link = urllib.parse.quote(summary_link)
        
        # Message with options for social media platforms
        response_message = (
            "Your shareable link to your expense summary has been generated successfully! 🎉\n"
            f"{summary_link}\n\n"
            "Share this link on your favorite social media platforms:\n"
            f"1. Facebook: [Share on Facebook](https://www.facebook.com/sharer/sharer.php?u={encoded_link})\n"
            f"2. Twitter: [Share on Twitter](https://twitter.com/share?url={encoded_link}&text=Check%20out%20my%20expense%20summary!)\n"
            f"3. LinkedIn: [Share on LinkedIn](https://www.linkedin.com/sharing/share-offsite/?url={encoded_link})"
        )
        bot.send_message(chat_id, response_message, parse_mode="Markdown")
    else:
        bot.send_message(chat_id, "Oops! We couldn't generate a shareable link for you. Please try again later.")


def generate_shareable_link(chat_id):
    """
    Generates a shareable link for the user's expense summary.
    This function creates a PDF summary of the user's expenses, uploads it to a cloud storage service,
    and returns a shareable link.
    """
    try:
        # Assuming `pdf.create_summary_pdf(chat_id)` exists in pdf.py and generates the PDF path
        file_path = pdf.create_summary_pdf(chat_id)
        
        # For demonstration purposes, simulate creating a shareable link
        # In production, use an upload service, like Google Drive or Dropbox, to get a public link
        shareable_link = f"https://example.com/shared_files/{os.path.basename(file_path)}"
        
        # Log or print to check link
        print("Generated shareable link:", shareable_link)
        
        return shareable_link
    except Exception as e:
        logging.exception("Error generating shareable link: " + str(e))
        return None
    
def addUserHistory(chat_id, user_record):
    global user_list
    if not (str(chat_id) in user_list):
        user_list[str(chat_id)] = []
    user_list[str(chat_id)].append(user_record)
    return user_list    

def main():
    """
    main() The entire bot's execution begins here. It ensure the bot variable begins
    polling and actively listening for requests from telegram.
    """
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        logging.exception(str(e))
        time.sleep(3)
        print("Connection Timeout")

if __name__ == "__main__":
    main() # type: ignore