import graphing
import helper
import logging
import os
from exception import BudgetNotFoundError

# === Documentation of budget_view.py ===

def run(message, bot):
    """
    Main function for displaying the budget to the user, handling both overall and category-specific budgets.
    
    Parameters:
    - message: The message from the user in Telegram.
    - bot: The Telegram bot object handling communication.
    
    If a budget is configured (either overall or category-specific), displays the budget information.
    Otherwise, raises a BudgetNotFoundError and informs the user about setting up a budget.
    """
    try:
        chat_id = message.chat.id
        if helper.isOverallBudgetAvailable(chat_id) or helper.isCategoryBudgetAvailable(chat_id):
            bot.send_message(chat_id, "Retrieving your budget details...")
            if helper.isOverallBudgetAvailable(chat_id):
                display_overall_budget(chat_id, bot)
            if helper.isCategoryBudgetAvailable(chat_id):
                display_category_budget(chat_id, bot)
        else:
            raise BudgetNotFoundError("No budget configured. Use the /budget command to add or update your budget.")
    except BudgetNotFoundError as bnf_err:
        logging.warning(f"No budget found for chat_id {chat_id}: {bnf_err}")
        bot.send_message(chat_id, str(bnf_err))
    except Exception as e:
        logging.error(f"Error in displaying budget for chat_id {chat_id}: {e}")
        helper.throw_exception(e, message, bot, logging)

def display_overall_budget(chat_id, bot):
    """
    Retrieves and displays the overall budget for the user based on their chat ID.
    
    Parameters:
    - chat_id: Unique ID of the user's chat.
    - bot: The Telegram bot object handling communication.
    """
    try:
        data = helper.getOverallBudget(chat_id)
        bot.send_message(chat_id, f"💰 Overall Budget: ${data}")
    except Exception as e:
        logging.error(f"Error in retrieving overall budget for chat_id {chat_id}: {e}")
        bot.send_message(chat_id, "Sorry, we encountered an error retrieving your overall budget.")

def display_category_budget(chat_id, bot):
    """
    Retrieves and displays the category-specific budget for the user based on their chat ID.
    Generates a graph if available and sends it to the user.
    
    Parameters:
    - chat_id: Unique ID of the user's chat.
    - bot: The Telegram bot object handling communication.
    """
    try:
        data = helper.getCategoryBudget(chat_id)
        if data:
            bot.send_message(chat_id, "📊 Here’s your category-wise budget:")
            table_text = "\n".join([f"- {category}: ${amount}" for category, amount in data.items()])
            bot.send_message(chat_id, table_text)

            # Generate graph and send if successful
            if graphing.viewBudget(data):
                with open("budget.png", "rb") as photo:
                    bot.send_photo(chat_id, photo)
                os.remove("budget.png")
            else:
                bot.send_message(chat_id, "Unable to generate a visual representation of your budget.")
        else:
            bot.send_message(chat_id, "It looks like your category budgets haven't been set up yet.")
    except Exception as e:
        logging.error(f"Error in retrieving category budget for chat_id {chat_id}: {e}")
        bot.send_message(chat_id, "Sorry, we encountered an error retrieving your category budgets.")
