"""
File: edit.py
Author: Vyshnavi Adusumelli, Tejaswini Panati, Harshavardhan Bandaru
Date: October 01, 2023
Description: Contains Telegram bot message handlers for expense editing features.

Copyright (c) 2023
...

"""

import helper
from telebot import types
from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP
from datetime import datetime


def run(m, bot):
    """
    Initiates the process of editing an expense.

    Args:
        m: The message object from the user.
        bot: The Telegram bot object.
    """
    chat_id = m.chat.id
    user_history = helper.getUserHistory(chat_id)

    if not user_history:
        bot.send_message(chat_id, "You have no previously recorded expenses to modify.")
        return

    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.row_width = 2

    for c in user_history:
        expense_data = c.split(",")
        formatted_expense = f"Date={expense_data[0]},\t\tCategory={expense_data[1]},\t\tAmount=${expense_data[2]}"
        markup.add(formatted_expense)

    info = bot.reply_to(m, "Select the expense to be edited:", reply_markup=markup)
    bot.register_next_step_handler(info, select_category_to_be_updated, bot)


def select_category_to_be_updated(m, bot):
    """
    Handles the user's selection of expense categories for updating.

    Args:
        m: The message object received from the user.
        bot: The Telegram bot object.
    """
    selected_data = m.text.split(",") if m.text else []
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.row_width = 2

    for c in selected_data:
        markup.add(c.strip())

    choice = bot.reply_to(m, "What do you want to update?", reply_markup=markup)
    bot.register_next_step_handler(choice, enter_updated_data, bot, selected_data, [])


def enter_updated_data(m, bot, selected_data, updated):
    """
    Handles the user's input for updating expense information.

    Args:
        m: The message object received from the user.
        bot: The Telegram bot object.
        selected_data: List of selected expense information.
        updated: List of updated categories.
    """
    choice1 = m.text if m.text else ""
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.row_width = 2

    for cat in helper.getSpendCategories():
        markup.add(cat)

    if "Date" in choice1:
        handle_date_selection(m, bot, selected_data, updated)

    elif "Category" in choice1:
        new_cat = bot.reply_to(m, "Please select the new category:", reply_markup=markup)
        bot.register_next_step_handler(new_cat, edit_cat, bot, selected_data, updated)

    elif "Amount" in choice1:
        new_cost = bot.reply_to(m, "Please type the new cost\n(Enter only numerical value)")
        bot.register_next_step_handler(new_cost, edit_cost, bot, selected_data, updated)


def handle_date_selection(m, bot, selected_data, updated):
    """
    Handles the date selection for expense updates.

    Args:
        m: The message object received from the user.
        bot: The Telegram bot object.
        selected_data: List of selected expense information.
        updated: List of updated categories.
    """
    calendar, step = DetailedTelegramCalendar().build()
    bot.send_message(m.chat.id, f"Select {LSTEP[step]}", reply_markup=calendar)

    @bot.callback_query_handler(func=DetailedTelegramCalendar.func())
    def edit_cal(c):
        chat_id = c.message.chat.id
        result, key, step = DetailedTelegramCalendar().process(c.data)

        if not result and key:
            bot.edit_message_text(f"Select {LSTEP[step]}", chat_id, c.message.message_id, reply_markup=key)
        elif result:
            data = datetime.today().date()
            if result > data:
                bot.send_message(chat_id, "Cannot select future dates. Please try /edit command again with correct dates.")
            else:
                edit_date(bot, selected_data, result, c, updated)
                bot.edit_message_text(f"Date is updated: {result}", chat_id, c.message.message_id)


def update_different_category(m, bot, selected_data, updated):
    """
    Prompts the user to update another category if desired.

    Args:
        m: The message object received from the user.
        bot: The Telegram bot object.
        selected_data: List of selected expense information.
        updated: List of updated categories.
    """
    if m.text.lower() == "y":
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        markup.row_width = 2
        for c in selected_data:
            if c not in updated:
                markup.add(c.strip())
        choice = bot.reply_to(m, "What do you want to update?", reply_markup=markup)
        bot.register_next_step_handler(choice, enter_updated_data, bot, selected_data, updated)


def edit_date(bot, selected_data, result, c, updated):
    """
    Updates the date for the selected expense.

    Args:
        bot: The Telegram bot object.
        selected_data: List of selected expense information.
        result: The new date selected by the user.
        c: The callback query.
        updated: List of updated categories.
    """
    chat_id = c.message.chat.id
    new_date = datetime.strftime(result, helper.getDateFormat())
    data_edit = helper.getUserHistory(chat_id)

    for i in range(len(data_edit)):
        user_data = data_edit[i].split(",")
        selected_date = selected_data[0].split("=")[1]
        selected_category = selected_data[1].split("=")[1]
        selected_amount = selected_data[2].split("=")[1]

        if (user_data[0] == selected_date and user_data[1] == selected_category and user_data[2] == selected_amount[1:]):
            data_edit[i] = f"{new_date},{selected_category},{selected_amount[1:]}"
            break

    helper.update_user_data(chat_id, data_edit)
    updated.append(f"Date={new_date}")
    selected_data[0] = f"Date={new_date}"

    if len(updated) == 3:
        bot.send_message(chat_id, "You have updated all the categories for this expense.")
        return

    resp = bot.send_message(chat_id, "Do you want to update another category in this expense? (Y/N)")
    bot.register_next_step_handler(resp, update_different_category, bot, selected_data, updated)


def edit_cat(m, bot, selected_data, updated):
    """
    Updates the category for the selected expense.

    Args:
        m: The message object received from the user.
        bot: The Telegram bot object.
        selected_data: List of selected expense information.
        updated: List of updated categories.
    """
    new_cat = m.text if m.text else ""
    chat_id = m.chat.id
    data_edit = helper.getUserHistory(chat_id)

    for i in range(len(data_edit)):
        user_data = data_edit[i].split(",")
        selected_date = selected_data[0].split("=")[1]
        selected_category = selected_data[1].split("=")[1]
        selected_amount = selected_data[2].split("=")[1]

        if (user_data[0] == selected_date and user_data[1] == selected_category and user_data[2] == selected_amount[1:]):
            data_edit[i] = f"{selected_date},{new_cat},{selected_amount[1:]}"
            break

    helper.update_user_data(chat_id, data_edit)
    updated.append(f"Category={new_cat}")
    selected_data[1] = f"Category={new_cat}"
    bot.reply_to(m, "Category is updated.")

    if len(updated) == 3:
        bot.send_message(chat_id, "You have updated all the categories for this expense.")
        return

    resp = bot.send_message(chat_id, "Do you want to update another category in this expense? (Y/N)")
    bot.register_next_step_handler(resp, update_different_category, bot, selected_data, updated)


def edit_cost(m, bot, selected_data, updated):
    """
    Updates the cost for the selected expense.

    Args:
        m: The message object received from the user.
        bot: The Telegram bot object.
        selected_data: List of selected expense information.
        updated: List of updated categories.
    """
    new_cost = m.text if m.text else ""
    chat_id = m.chat.id
    data_edit = helper.getUserHistory(chat_id)

    if helper.validate_entered_amount(new_cost) != 0:
        for i in range(len(data_edit)):
            user_data = data_edit[i].split(",")
            selected_date = selected_data[0].split("=")[1]
            selected_category = selected_data[1].split("=")[1]
            selected_amount = selected_data[2].split("=")[1]

            if (user_data[0] == selected_date and user_data[1] == selected_category and user_data[2] == selected_amount[1:]):
                data_edit[i] = f"{selected_date},{selected_category},{new_cost}"
                break

        helper.update_user_data(chat_id, data_edit)
        updated.append(f"Amount=${new_cost}")
        selected_data[2] = f"Amount=${new_cost}"
        bot.reply_to(m, "Cost is updated.")

        if len(updated) == 3:
            bot.send_message(chat_id, "You have updated all the categories for this expense.")
            return

        resp = bot.send_message(chat_id, "Do you want to update another category in this expense? (Y/N)")
        bot.register_next_step_handler(resp, update_different_category, bot, selected_data, updated)
    else:
        bot.reply_to(m, "Invalid amount entered. Please enter a numeric value.")
        run(m, bot)
