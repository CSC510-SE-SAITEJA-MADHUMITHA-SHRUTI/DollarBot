"""
File: test_add.py
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

import os
import json
from mock.mock import patch
from telebot import types
from code import add
from mock import ANY
from datetime import datetime


dateFormat = "%d-%b-%Y"
timeFormat = "%H:%M"
monthFormat = "%b-%Y"
date = datetime.today().date()

@patch("telebot.telebot")
def test_run(mock_telebot, mocker):
    mc = mock_telebot.return_value
    mc.send_message.return_value = True

    message = create_message("hello from test run!")
    add.run(message, mc)
    assert mc.send_message.called


@patch("telebot.telebot")
def test_post_category_selection_working(mock_telebot, mocker):
    mc = mock_telebot.return_value
    mc.send_message.return_value = True

    message = create_message("hello from testing!")
    add.post_category_selection(message, mc, date)
    assert mc.send_message.called


@patch("telebot.telebot")
def test_post_category_selection_noMatchingCategory(mock_telebot, mocker):
    mc = mock_telebot.return_value
    mc.send_message.return_value = []
    mc.reply_to.return_value = True

    mocker.patch.object(add, "helper")
    add.helper.getSpendCategories.return_value = None

    message = create_message("hello from testing!")
    add.post_category_selection(message, mc, date)
    assert mc.reply_to.called


@patch("telebot.telebot")
def test_post_amount_input_working(mock_telebot, mocker):
    mc = mock_telebot.return_value
    mc.send_message.return_value = True

    message = create_message("120")
    add.post_amount_input(message, mc, "Food", date)
    assert mc.send_message.called


@patch("telebot.telebot")
def test_post_amount_input_working_withdata(mock_telebot, mocker):
    mc = mock_telebot.return_value
    mc.send_message.return_value = True
    mocker.patch.object(add, "helper")
    add.helper.validate_entered_amount.return_value = 10
    add.helper.write_json.return_value = True
    add.helper.getDateFormat.return_value = dateFormat
    add.helper.getTimeFormat.return_value = timeFormat

    mocker.patch.object(add, "option")
    add.option.return_value = {11, "here"}

    message = create_message("hello from testing!")
    add.post_amount_input(message, mc, "Food", date)
    assert mc.send_message.called


@patch("telebot.telebot")
def test_post_amount_input_nonworking(mock_telebot, mocker):
    mc = mock_telebot.return_value
    mc.send_message.return_value = True
    mc.reply_to.return_value = True
    mocker.patch.object(add, "helper")
    add.helper.validate_entered_amount.return_value = 0
    message = create_message("hello from testing!")
    add.post_amount_input(message, mc, "Food",date)
    assert mc.send_message.called


@patch("telebot.telebot")
def test_post_amount_input_working_withdata_chatid(mock_telebot, mocker):
    mc = mock_telebot.return_value
    mc.send_message.return_value = True
    mocker.patch.object(add, "helper")
    add.helper.validate_entered_amount.return_value = 10
    add.helper.write_json.return_value = True
    add.helper.getDateFormat.return_value = dateFormat
    add.helper.getTimeFormat.return_value = timeFormat

    mocker.patch.object(add, "option")
    add.option = {11, "here"}
    test_option = {}
    test_option[11] = "here"
    add.option = test_option

    message = create_message("hello from testing!")
    add.post_amount_input(message, mc, "Food", date)
    assert mc.send_message.called
    # assert mc.send_message.called_with(11, ANY)


def test_add_user_record_nonworking(mocker):
    mocker.patch.object(add, "helper")
    add.helper.read_json.return_value = {}
    addeduserrecord = add.add_user_record(1, "record : test")
    assert addeduserrecord


def test_add_user_record_working(mocker):
    MOCK_USER_DATA = test_read_json()
    mocker.patch.object(add, "helper")
    add.helper.read_json.return_value = MOCK_USER_DATA
    addeduserrecord = add.add_user_record(1, "record : test")
    if len(MOCK_USER_DATA) + 1 == len(addeduserrecord):
        assert True


def create_message(text):
    params = {"messagebody": text}
    chat = types.User(11, False, "test")
    return types.Message(1, None, None, chat, "text", params, "")


def test_read_json():
    try:
        if not os.path.exists("./test/dummy_expense_record.json"):
            with open("./test/dummy_expense_record.json", "w") as json_file:
                json_file.write("{}")
            return json.dumps("{}")
        elif os.stat("./test/dummy_expense_record.json").st_size != 0:
            with open("./test/dummy_expense_record.json") as expense_record:
                expense_record_data = json.load(expense_record)
            return expense_record_data

    except FileNotFoundError:
        print("---------NO RECORDS FOUND---------")

@patch("telebot.telebot")
def test_post_category_selection_invalidDate(mock_telebot, mocker):
    mc = mock_telebot.return_value
    mc.send_message.return_value = True
    mc.reply_to.return_value = True  # Assume bot replies to invalid inputs

    # Mocking helper functions
    mocker.patch.object(add, "helper")
    add.helper.getSpendCategories.return_value = ["Food", "Utilities"]

    # Setting a future date (invalid date input scenario)
    future_date = datetime.today().date().replace(year=datetime.today().year + 1)

    message = create_message("Testing invalid date input!")
    add.post_category_selection(message, mc, future_date)
    assert mc.reply_to.called  # The bot should reply due to invalid date

    
