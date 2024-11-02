"""
File: add.py
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
import helper
import logging
from telebot import types
from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP
from helper import display_remaining_budget
from datetime import datetime
from exception import InvalidAmountError, InvalidCategoryError

option = {}

# === Documentation of add.py ===

def run(message, bot):
    """
    run(message, bot): This is the main function used to implement the add feature.
    It pop ups a menu on the bot asking the user to choose their expense category,
    after which control is given to post_category_selection(message, bot) for further proccessing.
    It takes 2 arguments for processing - message which is the message from the user,
    and bot which is the telegram bot object from the main code.py function.
    """
    helper.read_json()
    helper.read_category_json()
    chat_id = message.chat.id
    message = bot.send_message(chat_id, "Select date")
    calendar, step = DetailedTelegramCalendar().build()
    bot.send_message(chat_id, f"Select {LSTEP[step]}", reply_markup=calendar)


def cal(c,bot):
    chat_id = c.message.chat.id
    result, key, step = DetailedTelegramCalendar().process(c.data)

    if not result and key:
        bot.edit_message_text(
            f"Select {LSTEP[step]}",
            chat_id,
            c.message.message_id,
            reply_markup=key,
        )
    elif result:
        data = datetime.today().date()
        if (result > data):
            bot.send_message(chat_id,"Cannot select future dates, Please try /add command again with correct dates")
        else:
            category_selection(c.message,bot,result)

def category_selection(msg,bot,date):
    """
    category_selection(msg, bot, date): Handles the selection of expense categories.

    Parameters:
    - msg (telegram.Message): The message object received from the user.
    - bot (telegram.Bot): The Telegram bot object.
    - date (datetime.datetime): The date associated with the expense.

    This function generates a keyboard with available expense categories, prompts the user to select a category,
    and registers the next step handler to handle the amount input. If no categories are available, it informs
    the user to add a category first.
    """
    
    try:
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        markup.row_width = 2
        categories = helper.getSpendCategories()
        if not categories:
            bot.reply_to(msg, "You don't have any categories. Please add a category!!")
        else:
            for c in categories:
                markup.add(c)
            msg = bot.reply_to(msg, "Select Category", reply_markup=markup)
            bot.register_next_step_handler(msg, post_category_selection, bot, date)
    except Exception as e:
        print(e)


def post_category_selection(message, bot, date):
    """
    post_category_selection(message, bot): It takes 3 arguments for processing -
    message which is the message from the user, and bot which is the telegram bot object
    from the run(message, bot): function in the add.py file. It requests the user to enter the amount
    they have spent on the expense category chosen and then passes control to
    post_amount_input(message, bot): for further processing.
    """
    try:
        chat_id = message.chat.id
        selected_category = message.text
        if selected_category not in helper.getSpendCategories():
            bot.send_message(
                chat_id, "Invalid", reply_markup=types.ReplyKeyboardRemove()
            )
            raise InvalidCategoryError(selected_category, "I don’t recognize this category")
        option[chat_id] = selected_category
        message = bot.send_message(
            chat_id, "How much did you spend on {}? \n(Numeric values only)".format(str(option[chat_id])),)
        bot.register_next_step_handler(message, post_amount_input, bot, selected_category, date)
    except Exception as e:
        logging.exception(str(e))
        bot.reply_to(message, "Oh no! " + str(e))
        display_text = ""
        commands = helper.getCommands()
        for c in commands:
            # generate help text out of the commands dictionary defined at the top
            display_text += "/" + c + ": "
            display_text += commands[c] + "\n"
        bot.send_message(chat_id, "Please select a menu option from below:")
        bot.send_message(chat_id, display_text)


def post_amount_input(message, bot, selected_category, date):
    """
    post_amount_input(message, bot): It takes 2 arguments for processing -
    message which is the message from the user, and bot which is the telegram bot
    object from the post_category_selection(message, bot): function in the add.py file.
    It takes the amount entered by the user, validates it with helper.validate() and then
    calls add_user_record to store it.
    """
    try:
        print("---------------------------------------------------")
        chat_id = message.chat.id
        amount_entered = message.text
        amount_value = helper.validate_entered_amount(amount_entered)  # validate
        if amount_value == 0:  # cannot be $0 spending
            raise InvalidAmountError("Spent amount has to be a non-zero number.")

        date_of_entry = date.strftime(helper.getDateFormat())
        date_str, category_str, amount_str = (
            str(date_of_entry),
            str(selected_category),
            str(amount_value),
        )
        helper.write_json(
            add_user_record(
                chat_id, "{},{},{}".format(date_str, category_str, amount_str)
            )
        )
        bot.send_message(
            chat_id,
            "The following expenditure has been recorded: You have spent ${} for {} on {}".format(
                amount_str, category_str, date_str
            ),
        )
        helper.display_remaining_budget(message, bot, selected_category)  # Use 'selected_category' instead of 'cat'

    except Exception as e:
        logging.exception(str(e))
        bot.send_message(chat_id, "Oh no. " + str(e))

def add_user_record(chat_id, record_to_be_added):
    """
    add_user_record(chat_id, record_to_be_added): Takes 2 arguments -
    chat_id or the chat_id of the user's chat, and record_to_be_added which
    is the expense record to be added to the store. It then stores this expense record in the store.
    """
    user_list = helper.read_json()
    print(f"user_list before addition: {user_list}")  # Debug output

    # Ensure user_list is initialized properly
    if user_list is None:
        user_list = {}  # Initialize as empty dictionary if read_json returned None

    if str(chat_id) not in user_list:
        user_list[str(chat_id)] = helper.createNewUserRecord()

    user_list[str(chat_id)]["data"].append(record_to_be_added)
    return user_list
