"""
File: analytics.py
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
import get_analysis
from exception import InvalidOperationError

def run(message, bot):
    """
    run(message, bot): This is the main function used to implement the analytics feature.
    It pop ups a menu on the bot asking the user to choose to view analytics
    after which control is given to post_operation_selection(message, bot) for further proccessing.
    It takes 2 arguments for processing - message which is the message from the user, and bot which is the
    telegram bot object from the main code.py function.
    """
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    options = helper.getAnalyticsOptions()
    markup.row_width = 2
    for c in options.values():
        markup.add(c)
    msg = bot.reply_to(message, "Select the type of analysis (grouped by category):", reply_markup=markup)
    bot.register_next_step_handler(msg, post_operation_selection, bot)
    
def post_operation_selection(message, bot):
    """
    post_operation_selection(message, bot): Processes user-selected operations and 
    invokes corresponding analysis functions.
    
    Args:
        message: The message object containing user input.
        bot: The Telegram bot object for sending messages.
    """
    chat_id = message.chat.id
    op = message.text
    options = helper.getAnalyticsOptions()

    try:
        # Validate the operation
        validate_operation(op, options)

        # Mapping operations to functions
        operation_mapping = {
            options["overall"]: get_analysis.viewOverallBudget,
            options["spend"]: get_analysis.viewSpendWise,
            options["remaining"]: get_analysis.viewRemaining,
            options["history"]: get_analysis.viewHistory,
        }

        # Execute the corresponding function
        operation_mapping[op](chat_id, bot)

    except InvalidOperationError as e:
        bot.send_message(chat_id, f"Invalid operation selected: '{e.operation}'. Please choose a valid option.")
    except Exception as e:
        helper.throw_exception(e, message, bot, logging)


def validate_operation(op, options):
    """
    Validates whether the provided operation is in the available options.
    
    Args:
        op: The operation to validate.
        options: A dictionary of valid operations.
    
    Raises:
        InvalidOperationError: If the operation is not valid.
    """
    if op not in options.values():
        raise InvalidOperationError(op)
