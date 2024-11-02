"""
File: test_budget.py
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

from mock.mock import patch
from telebot import types
from code import budget, helper
from exception import BudgetNotFoundError


@patch("telebot.telebot")
def test_run(mock_telebot, mocker):
    mc = mock_telebot.return_value
    mc.reply_to.return_value = True
    message = create_message("hello from test run!")
    budget.run(message, mc)
    assert mc.reply_to.called
    # assert mc.reply_to.called_with(ANY, "Select Operation", ANY)

@patch("telebot.telebot")
def test_post_operation_selection_failing_case(mock_telebot, mocker):
    mc = mock_telebot.return_value
    mc.send_message.return_value = True

    mocker.patch.object(budget, "helper")
    budget.helper.getBudgetOptions.return_value = {}

    message = create_message("hello from budget test run!")
    budget.post_operation_selection(message, mc)
    mc.send_message.assert_called_with(11, "Invalid", reply_markup=mock.ANY)

@patch("telebot.telebot")
def test_post_operation_selection_update_case(mock_telebot, mocker):
    mc = mock_telebot.return_value
    mc.send_message.return_value = True

    mocker.patch.object(budget, "budget_update")
    budget.budget_update.run.return_value = True

    mocker.patch.object(budget, "helper")
    budget.helper.getBudgetOptions.return_value = {
        "update": "Add/Update",
        "view": "View",
        "delete": "Delete",
    }

    message = create_message("Add/Update")
    budget.post_operation_selection(message, mc)
    assert budget.budget_update.run.called

@patch("telebot.telebot")
def test_post_operation_selection_view_case(mock_telebot, mocker):
    mc = mock_telebot.return_value
    mc.send_message.return_value = True

    mocker.patch.object(budget, "budget_view")
    budget.budget_view.run.return_value = True

    mocker.patch.object(budget, "helper")
    budget.helper.getBudgetOptions.return_value = {
        "update": "Add/Update",
        "view": "View",
        "delete": "Delete",
    }

    message = create_message("View")
    budget.post_operation_selection(message, mc)
    assert budget.budget_view.run.called

@patch("telebot.telebot")
def test_post_operation_selection_delete_case(mock_telebot, mocker):
    mc = mock_telebot.return_value
    mc.send_message.return_value = True

    mocker.patch.object(budget, "budget_delete")
    budget.budget_delete.run.return_value = True

    mocker.patch.object(budget, "helper")
    budget.helper.getBudgetOptions.return_value = {
        "update": "Add/Update",
        "view": "View",
        "delete": "Delete",
    }

    message = create_message("Delete")
    budget.post_operation_selection(message, mc)
    assert budget.budget_delete.run.called

def create_message(text):
    params = {"messagebody": text}
    chat = types.User(11, False, "test")
    message = types.Message(1, None, None, chat, "text", params, "")
    message.text = text
    return message

@patch("telebot.telebot")
def test_run_no_budget_set(mock_telebot, mocker):
    """
    Tests the case where the user has not set a budget,
    and a BudgetNotFoundError should be raised with an appropriate message.
    """
    mc = mock_telebot.return_value
    mc.send_message.return_value = True
    
    # Mock helper functions to return no budget
    mocker.patch.object(helper, "isOverallBudgetAvailable", return_value=False)
    mocker.patch.object(helper, "isCategoryBudgetAvailable", return_value=False)
    
    message = create_message("hello from test run!")
    budget.run(message, mc)
    
    mc.send_message.assert_called_with(message.chat.id, "No budget configured. Use the /budget command to add or update your budget.")


@patch("telebot.telebot")
def test_run_budget_displayed(mock_telebot, mocker):
    """
    Tests that the budget is displayed when the user has an overall or category-wise budget set.
    """
    mc = mock_telebot.return_value
    mc.send_message.return_value = True
    
    # Mock helper functions to return an available budget
    mocker.patch.object(helper, "isOverallBudgetAvailable", return_value=True)
    mocker.patch.object(helper, "isCategoryBudgetAvailable", return_value=False)
    
    message = create_message("display budget")
    budget.run(message, mc)
    
    mc.send_message.assert_called_with(message.chat.id, "Retrieving your budget details...")
    
@patch("telebot.telebot")
def test_post_operation_selection_invalid_command(mock_telebot, mocker):
    """
    Tests response when the user sends an invalid command or operation.
    """
    mc = mock_telebot.return_value
    mc.send_message.return_value = True

    mocker.patch.object(budget, "helper")
    budget.helper.getBudgetOptions.return_value = {"update": "Add/Update", "view": "View", "delete": "Delete"}

    message = create_message("InvalidCommand")
    budget.post_operation_selection(message, mc)

    mc.send_message.assert_called_with(message.chat.id, "Invalid operation selected. Please choose from Add/Update, View, or Delete.")

@patch("telebot.telebot")
def test_display_overall_budget_success(mock_telebot, mocker):
    """
    Tests display of the overall budget when it is successfully retrieved.
    """
    mc = mock_telebot.return_value
    mc.send_message.return_value = True

    # Mock helper function to return a sample budget value
    mocker.patch.object(helper, "getOverallBudget", return_value="500")
    
    message = create_message("overall budget")
    budget.display_overall_budget(message.chat.id, mc)
    
    mc.send_message.assert_called_with(message.chat.id, "💰 Overall Budget: $500")

@patch("telebot.telebot")
def test_display_overall_budget_failure(mock_telebot, mocker):
    """
    Tests display of the overall budget when an error occurs in fetching the budget.
    """
    mc = mock_telebot.return_value
    mc.send_message.return_value = True

    # Mock helper function to raise an exception
    mocker.patch.object(helper, "getOverallBudget", side_effect=Exception("Database error"))
    
    message = create_message("overall budget")
    budget.display_overall_budget(message.chat.id, mc)
    
    mc.send_message.assert_called_with(message.chat.id, "Sorry, we encountered an error retrieving your overall budget.")

@patch("telebot.telebot")
def test_display_category_budget_with_data(mock_telebot, mocker):
    """
    Tests display of category budget when categories are available.
    """
    mc = mock_telebot.return_value
    mc.send_message.return_value = True

    # Mock helper function to return category budget data
    mocker.patch.object(helper, "getCategoryBudget", return_value={"Food": 200, "Utilities": 100})
    mocker.patch("graphing.viewBudget", return_value=True)
    
    message = create_message("category budget")
    budget.display_category_budget(message.chat.id, mc)
    
    mc.send_message.assert_any_call(message.chat.id, "📊 Here’s your category-wise budget:")
    mc.send_message.assert_any_call(message.chat.id, "- Food: $200\n- Utilities: $100")
    mc.send_photo.assert_called()  # Assuming the graph generation succeeds

@patch("telebot.telebot")
def test_display_category_budget_no_data(mock_telebot, mocker):
    """
    Tests display of category budget when no category budgets are set.
    """
    mc = mock_telebot.return_value
    mc.send_message.return_value = True

    # Mock helper function to return empty category budget data
    mocker.patch.object(helper, "getCategoryBudget", return_value=None)
    
    message = create_message("category budget")
    budget.display_category_budget(message.chat.id, mc)
    
    mc.send_message.assert_called_with(message.chat.id, "It looks like your category budgets haven't been set up yet.")

def create_message(text):
    """
    Helper function to create a mock Telegram message object for testing.
    """
    params = {"messagebody": text}
    chat = types.User(11, False, "test")
    message = types.Message(1, None, None, chat, "text", params, "")
    message.text = text
    return message


@patch("telebot.telebot")
def test_display_category_budget_with_data(mock_telebot, mocker):
    """
    Tests display of category budget when categories are available.
    """
    mc = mock_telebot.return_value
    mc.send_message.return_value = True

    # Mock helper function to return category budget data
    mocker.patch.object(helper, "getCategoryBudget", return_value={"Food": 200, "Utilities": 100})
    mocker.patch("graphing.viewBudget", return_value=True)
    
    message = create_message("category budget")
    budget.display_category_budget(message.chat.id, mc)
    
    mc.send_message.assert_any_call(message.chat.id, "📊 Here’s your category-wise budget:")
    mc.send_message.assert_any_call(message.chat.id, "- Food: $200\n- Utilities: $100")
    mc.send_photo.assert_called()
    # Assert that the graphing function is called correctly with the data
    mocker.patch("graphing.viewBudget").assert_called_with({"Food": 200, "Utilities": 100})

def create_message(text):
    """
    Helper function to create a mock Telegram message object for testing.
    """
    params = {"messagebody": text}
    chat = types.User(11, False, "test")
    message = types.Message(1, None, None, chat, "text", params, "")
    message.text = text
    return message
