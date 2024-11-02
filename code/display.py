"""
File: display.py
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

import time
from tabulate import tabulate
import helper
import graphing
import logging
from telebot import types
from datetime import datetime
from exception import DisplayOptionError, NoHistoryError

# === Documentation of display.py ===

def run(message, bot):
    """
    run(message, bot): This is the main function used to implement the delete feature.
    It takes 2 arguments for processing - message which is the message from the user, and bot
    which is the telegram bot object from the main code.py function.
    """
    helper.read_json()
    chat_id = message.chat.id
    history = helper.getUserHistory(chat_id)
    if history is None:
        bot.send_message(
            chat_id, "Oops! Looks like you do not have any spending records!"
        )
    else:
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        markup.row_width = 2
        for mode in helper.getSpendDisplayOptions():
            markup.add(mode)
        msg = bot.reply_to(
            message,
            "Please select a category to see the total expense",
            reply_markup=markup,
        )
        bot.register_next_step_handler(msg, display_total, bot)

def display_total(message, bot):
    """
    display_total(message, bot): It takes 2 arguments for processing - message which is
    the message from the user, and bot which is the telegram bot object from the
    run(message, bot): function in the same file. This function loads the user's data using
    the helper file's getUserHistory(chat_id) method. After this, depending on the option user
    has chosen on the UI, it calls the calculate_spendings(queryResult): to process the queried
    data to return to the user after which it finally passes the data to the UI for the user to view.
    """
    try:
        chat_id = message.chat.id
        DayWeekMonth = message.text

        # Filter out non-spending-related commands such as "/help"
        if DayWeekMonth.startswith("/"):
            bot.reply_to(message, "This command is not related to spendings.")
            return

        if DayWeekMonth not in helper.getSpendDisplayOptions():
            raise DisplayOptionError(
               'Sorry I can\'t show spendings for "{}"!'.format(DayWeekMonth)
            )

        history = helper.getUserHistory(chat_id)
        if history is None:
            raise NoHistoryError("Oops! Looks like you do not have any spending records!")

        bot.send_message(chat_id, "Hold on! Calculating...")
        # show the bot "typing" (max. 5 secs)
        bot.send_chat_action(chat_id, "typing")
        time.sleep(0.5)

        total_text = ""
        queryResult = []
        if DayWeekMonth == "Day":
            query = datetime.now().today().strftime(helper.getDateFormat())
            # query all that contains today's date
            queryResult = [
                value for index, value in enumerate(history) if str(query) in value
            ]
        elif DayWeekMonth == "Month":
            query = datetime.now().today().strftime(helper.getMonthFormat())
            # query all that contains today's date
            queryResult = [
                value for index, value in enumerate(history) if str(query) in value
            ]
        total_text, total_dict = calculate_spendings(queryResult)
        monthly_budget = helper.getCategoryBudget(chat_id)
        print("Print Total Spending", total_text)
        print("Print monthly budget", monthly_budget)

        spending_text = ""
        if len(total_text) == 0:
            spending_text = "You have no spendings for {}!".format(DayWeekMonth)
            bot.send_message(chat_id, spending_text)
        else:
            table = [["Category", "Amount"]]
            spending_text = "Here are your total spendings {}".format(DayWeekMonth.lower())
            for category, amount in total_dict.items():
                table.append([str(category), "$ " + str(amount)])
            spend_total_str="<pre>"+ tabulate(table, headers='firstrow')+"</pre>"
            bot.send_message(chat_id, spending_text)
            bot.send_message(chat_id, spend_total_str, parse_mode="HTML")
            graphing.visualize(total_text, monthly_budget)
            bot.send_photo(chat_id, photo=open("expenditure.png", "rb"))
    except Exception as e:
        logging.exception(str(e))
        bot.reply_to(message, str(e))


def calculate_spendings(queryResult):
    """
    calculate_spendings(queryResult): Takes 1 argument for processing - queryResult
    which is the query result from the display total function in the same file.
    It parses the query result and turns it into a form suitable for display on the UI by the user.
    """
    total_dict = {}

    for row in queryResult:
        # date,cat,money
        s = row.split(",")
        # cat
        cat = s[1]
        if cat in total_dict:
            # round up to 2 decimal
            total_dict[cat] = round(total_dict[cat] + float(s[2]), 2)
        else:
            total_dict[cat] = float(s[2])
    total_text = ""
    for key, value in total_dict.items():
        total_text += str(key) + " $" + str(value) + "\n"
    return total_text, total_dict