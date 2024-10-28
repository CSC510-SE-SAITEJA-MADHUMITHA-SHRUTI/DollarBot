import re
import json
import os
from datetime import datetime
from notify import notify

spend_categories = [
    "Food",
    "Groceries",
    "Utilities",
    "Transport",
    "Shopping",
    "Miscellaneous",
]
choices = ["Date", "Category", "Cost"]
spend_display_option = ["Day", "Month"]
spend_estimate_option = ["Next day", "Next month"]
update_options = {"continue": "Continue", "exit": "Exit"}
budget_options = {"update": "Add/Update", "view": "View", "delete": "Delete"}
budget_types = {"overall": "Overall Budget", "category": "Category-Wise Budget"}
data_format = {"data": [], "budget": {"overall": None, "category": None}}
analytics_options = {"overall": "Overall budget split", "spend": "Split of current spend", "remaining": "Remaining value", "history": "Time series graph of spend history"}

commands = {
    "menu": "Display commands with their descriptions.",
    "help": "Display the list of commands.",
    "pdf": "Save history as PDF.",
    "add": "This option is for adding your expenses \
       \n 1. It will give you the list of categories to choose from. \
       \n 2. You will be prompted to enter the amount corresponding to your spending \
       \n 3.The message will be prompted to notify the addition of your expense with the amount, date, time, and category.",
    "analytics": "This option gives user a graphical representation of their expenditures \
        \n You will get an option to choose the type of data you want to see.",
    "predict": "This option analyzes your recorded spendings and gives you a budget that will accommodate for them.",
    "history": "This option is to give you the detailed summary of your expenditure with Date, time, category, and amount. A quick lookup into your spendings.",
    "delete": "This option is to Clear/Erase all your records.",
    "edit": "This option helps you to go back and correct/update the missing details \
        \n 1. It will give you the list of your expenses you wish to edit \
        \n 2. It will let you change the specific field based on your requirements like amount/date/category.",
    "budget": "This option is to set/update/delete the budget. \
        \n 1. The Add/update category is to set the new budget or update the existing budget \
        \n 2. The view category gives the detail if budget is exceeding or in limit with the difference amount \
        \n 3. The delete category allows to delete the budget and start afresh!",
    "summary": "Generates a summary of your overall and category-wise budgets, showing remaining and spent amounts.",
    "report": "Generates a comprehensive report over a custom date range, with individual transactions and totals by category. Ideal for detailed monthly or quarterly reviews.",
    "socialmedia": "Generate a shareable link to post your expense summary on social media platforms."
}


dateFormat = "%d-%b-%Y"
timeFormat = "%H:%M"
monthFormat = "%b-%Y"

# === Documentation of helper.py ===

# function to load .json expense record data
def read_json():
    """
    read_json(): Function to load .json expense record data
    """
    try:
        if not os.path.exists("expense_record.json"):
            with open("expense_record.json", "w") as json_file:
                json_file.write("{}")
            return json.dumps("{}")
        elif os.stat("expense_record.json").st_size != 0:
            with open("expense_record.json") as expense_record:
                expense_record_data = json.load(expense_record)
            return expense_record_data

    except FileNotFoundError:
        print("---------NO RECORDS FOUND---------")

def write_json(user_list):
    """
    write_json(user_list): Stores data into the datastore of the bot.
    """
    try:
        with open("expense_record.json", "w") as json_file:
            json.dump(user_list, json_file, ensure_ascii=False, indent=4)
    except FileNotFoundError:
        print("Sorry, the data file could not be found.")

# Summary command
def generate_summary(chat_id, bot):
    """
    generate_summary(chat_id, bot): Generates a summary of the user's overall and category-wise budget.
    """
    overall_budget = getOverallBudget(chat_id)
    category_budget = getCategoryBudget(chat_id)
    total_spent = calculate_total_spendings(getUserHistory(chat_id))
    
    summary_message = "===== Budget Summary =====\n\n"
    
    if overall_budget is not None:
        remaining_overall = calculateRemainingOverallBudget(chat_id)
        summary_message += f"Overall Budget: ${overall_budget}\n"
        summary_message += f"Total Spent: ${total_spent}\n"
        summary_message += f"Remaining Overall Budget: ${remaining_overall}\n\n"
    else:
        summary_message += "No overall budget set.\n\n"
    
    summary_message += "Category-Wise Budget:\n"
    if category_budget:
        for category, budget in category_budget.items():
            spent = calculate_total_spendings_for_category(getUserHistory(chat_id), category)
            remaining = float(budget) - spent
            summary_message += f"{category}:\n  Budget: ${budget}\n  Spent: ${spent}\n  Remaining: ${remaining}\n"
    else:
        summary_message += "No category-wise budget set."
    
    bot.send_message(chat_id, summary_message)

def generate_report(chat_id, bot, start_date, end_date):
    """
    generate_report(chat_id, bot, start_date, end_date): Generates a detailed spending report
    for the specified date range and sends it to the user.
    """
    try:
        # Convert dates from string to datetime for comparison
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")

        if start > end:
            bot.send_message(chat_id, "Start date must be before end date. Please try again.")
            return

        # Fetch expenses for the specified date range
        expenses = fetch_expenses(chat_id, start, end)
        if expenses is None or not expenses:
            bot.send_message(chat_id, f"No expenses found between {start_date} and {end_date}.")
            return

        # Generate the report content
        report_content = f"📅 Report from {start_date} to {end_date} 📅\n\n"
        total_spent = 0
        for expense in expenses:
            report_content += f"{expense['date'].strftime('%d-%b-%Y')}: {expense['category']} - ${expense['amount']}\n"
            total_spent += expense['amount']  # Sum the amounts

        report_content += f"\nTotal Spent: ${total_spent:.2f}"
        bot.send_message(chat_id, report_content)

    except ValueError:
        bot.send_message(chat_id, "Invalid date format. Please use YYYY-MM-DD.")
    except Exception as e:
        bot.send_message(chat_id, "An error occurred while generating the report.")
        print(f"Error: {e}")  # Print the exception for debugging
         

def generate_shareable_link(chat_id):
    """
    Generates a shareable link for the user's expense summary.
    This function assumes that an external service API (e.g., Google Drive API) is used to upload
    the summary and obtain a link that can be publicly shared.
    """
    try:
        # Generate the PDF summary
        file_path = pdf.create_summary_pdf(chat_id)
        
        # Upload the file to a service like Google Drive or Dropbox (assuming helper.upload_to_drive exists)
        shareable_link = helper.upload_to_drive(file_path)
        
        return shareable_link
    except Exception as e:
        logging.exception("Error generating shareable link: " + str(e))
        return None
    
def create_shareable_link(chat_id):
    """
    Creates a shareable link for the user's expenses.
    This could be replaced with actual upload logic.
    """
    try:
        # Placeholder for the file path, you can replace this with actual file generation logic
        file_name = f"{chat_id}_expenses_summary.pdf"
        
        # Simulated link creation
        shareable_link = f"https://example.com/shared_files/{file_name}"
        
        # Log or print to check link
        print("Generated shareable link:", shareable_link)
        
        return shareable_link
    except Exception as e:
        logging.exception("Error generating shareable link: " + str(e))
        return None
    
# Add this at the end of helper.py


def fetch_expenses(chat_id, start_date, end_date):
    """
    Fetch expenses for a user between specified start and end dates.
    
    Args:
        chat_id (str): The unique identifier for the user.
        start_date (datetime): The start date for fetching expenses.
        end_date (datetime): The end date for fetching expenses.
    
    Returns:
        list: A list of expenses within the specified date range.
    """
    user_data = getUserData(chat_id)  # Assuming this retrieves user data
    
    if not user_data or "data" not in user_data:
        print("No user data found.")
        return []  # Return an empty list if no data found

    expenses = user_data["data"]

    # Ensure expenses is a list
    if not isinstance(expenses, list):
        print("Expected expenses to be a list, but got:", type(expenses))
        return []

    filtered_expenses = []
    
    for expense_str in expenses:
        try:
            date_str, category, amount_str = expense_str.split(',')
            expense_date = datetime.strptime(date_str, "%d-%b-%Y")  # Adjust date format as needed
            amount = float(amount_str)

            # Check if the expense falls within the specified date range
            if start_date <= expense_date <= end_date:
                filtered_expenses.append({
                    'date': expense_date,
                    'category': category,
                    'amount': amount
                })
        except ValueError as e:
            print(f"Error parsing expense: {expense_str} -> {e}")
            continue

    return filtered_expenses






def validate_entered_amount(amount_entered):
    """
    validate_entered_amount(amount_entered): Takes 1 argument, amount_entered.
    It validates this amount's format to see if it has been correctly entered by the user.
    """
    if amount_entered is None:
        return 0
    if re.match("^[1-9][0-9]{0,14}\\.[0-9]*$", amount_entered) or re.match(
        "^[1-9][0-9]{0,14}$", amount_entered
    ):
        amount = round(float(amount_entered), 2)
        if amount > 0:
            return str(amount)
    return 0

def getUserHistory(chat_id):
    """
    getUserHistory(chat_id): Takes 1 argument chat_id and uses this to get the relevant user's historical data.
    """
    data = getUserData(chat_id)
    if data is not None:
        return data["data"]
    return None

def getUserHistoryByCategory(chat_id, category):
    data = getUserHistory(chat_id)
    previous_expenses = []
    for record in data:
        if f",{category}," in record:
            previous_expenses.append(record)
    return previous_expenses

def getUserHistoryDateExpense(chat_id):
    data = getUserHistory(chat_id)
    cat_spend_dict = {}
    for record in data:
        split_vals = record.split(",")
        cat_spend_dict[split_vals[0]] = split_vals[2]
    return cat_spend_dict

def getUserData(chat_id):
    user_list = read_json()
    if user_list is None:
        return None
    if str(chat_id) in user_list:
        return user_list[str(chat_id)]
    return None

def throw_exception(e, message, bot, logging):
    logging.exception(str(e))
    bot.reply_to(message, "Oh no! " + str(e))

def createNewUserRecord():
    return data_format

def getOverallBudget(chatId):
    data = getUserData(chatId)
    if data is None or data == {}:
        return None
    return data["budget"]["overall"]

def getCategoryBudget(chatId):
    data = getUserData(chatId)
    if data is None:
        return None
    return data["budget"]["category"]

def getCategoryBudgetByCategory(chatId, cat):
    if not isCategoryBudgetByCategoryAvailable(chatId, cat):
        return None
    data = getCategoryBudget(chatId)
    return data[cat]

def canAddBudget(chatId):
    overall_budget = getOverallBudget(chatId)
    category_budget = getCategoryBudget(chatId)
    return (overall_budget is None and overall_budget != '0') and (category_budget is None and category_budget != {})

def isOverallBudgetAvailable(chatId):
    overall_budget = getOverallBudget(chatId)
    if overall_budget is not None and overall_budget != '0':
        return True
    return False

def isCategoryBudgetAvailable(chatId):
    category_budget = getCategoryBudget(chatId)
    if category_budget is not None and category_budget != {}:
        return True
    return False

def isCategoryBudgetByCategoryAvailable(chatId, cat):
    data = getCategoryBudget(chatId)
    if data is None or data == {}:
        return False
    return cat in data.keys()

def get_uncategorized_amount(chatId, amount):
    overall_budget = float(amount)
    category_budget_data = getCategoryBudget(chatId)
    if category_budget_data is None or category_budget_data == {}:
        return amount
    category_budget = 0
    for c in category_budget_data.values():
        category_budget += float(c)
    uncategorized_budget = overall_budget - category_budget
    return str(round(uncategorized_budget,2))

def display_remaining_budget(message, bot, cat):
    print("inside")
    chat_id = message.chat.id
    display_remaining_category_budget(message, bot, cat)
    display_remaining_overall_budget(message, bot)

def display_remaining_overall_budget(message, bot):
    print("here")
    chat_id = message.chat.id
    remaining_budget = calculateRemainingOverallBudget(chat_id)
    print("here", remaining_budget)
    if remaining_budget >= 0:
        msg = "\nRemaining Overall Budget is $" + str(remaining_budget)
    else:
        msg = (
            "\nBudget Exceded!\nExpenditure exceeds the budget by $" + str(remaining_budget)[1:]
        )
    bot.send_message(chat_id, msg)

def calculateRemainingOverallBudget(chat_id):
    budget = getOverallBudget(chat_id)
    history = getUserHistory(chat_id)
    query = datetime.now().today().strftime(getMonthFormat())
    queryResult = [value for _, value in enumerate(history) if str(query) in value]
    return float(budget) - calculate_total_spendings(queryResult)

def calculate_total_spendings(queryResult):
    total = 0
    for row in queryResult:
        s = row.split(",")
        total = total + float(s[2])
    return total

def calculateRemainingCategoryBudgetPercent(chat_id, cat):
    budget = getCategoryBudgetByCategory(chat_id, cat)
    if not budget or float(budget) == 0:  # Check if budget is None or zero
        return 0  # Return 0 percent if budget is zero to avoid division error
    history = getUserHistory(chat_id)
    query = datetime.now().today().strftime(getMonthFormat())
    queryResult = [value for _, value in enumerate(history) if str(query) in value]
    return (calculate_total_spendings_for_category(queryResult, cat) / float(budget)) * 100


def calculateRemainingCategoryBudget(chat_id, cat):
    budget = getCategoryBudgetByCategory(chat_id, cat)
    history = getUserHistory(chat_id)
    query = datetime.now().today().strftime(getMonthFormat())
    queryResult = [value for _, value in enumerate(history) if str(query) in value]
    return float(budget) - calculate_total_spendings_for_category(queryResult, cat)

def calculateRemainingCateogryBudgetPercent(chat_id, cat):
    budget = getCategoryBudgetByCategory(chat_id, cat)
    history = getUserHistory(chat_id)
    query = datetime.now().today().strftime(getMonthFormat())
    queryResult = [value for _, value in enumerate(history) if str(query) in value]
    return (calculate_total_spendings_for_category(queryResult, cat)/float(budget))*100

def calculate_total_spendings_for_category(queryResult, cat):
    total = 0
    for row in queryResult:
        s = row.split(",")
        if cat == s[1]:
            total = total + float(s[2])
    return total

def calculate_total_spendings_for_cateogory_chat_id(chat_id, cat):
    history = getUserHistory(chat_id)
    query = datetime.now().today().strftime(getMonthFormat())
    queryResult = [value for _, value in enumerate(history) if str(query) in value]
    return calculate_total_spendings_for_category(queryResult, cat)

def updateBudgetCategory(chatId, category):
    user_list = read_json()
    user_list[str(chatId)]["budget"]["category"][category] = str(0)
    write_json(user_list)

def getAvailableCategories(history):
    available_categories = set()
    for record in history:
        available_categories.add(record.split(',')[1])
    return available_categories

def getCategoryWiseSpendings(available_categories, history):
    category_wise_history = {}
    for cat in available_categories:
        for record in history:
            if cat in record:
                if cat in category_wise_history.keys():
                    category_wise_history[cat].append(record)
                else:
                    category_wise_history[cat] = [record]
    return category_wise_history

def getFormattedPredictions(category_predictions):
    category_budgets = ""
    for key,value in category_predictions.items():
        if type(value) == float:
            category_budgets += str(key) + ": $" + str(value) + "\n"
        else:
            category_budgets += str(key) + ": " + value + "\n"
    predicted_budget = "Here are your predicted budgets"
    predicted_budget += " for the next month \n"
    predicted_budget += category_budgets
    return predicted_budget

#getters
def getSpendCategories():
    """
    getSpendCategories(): This functions returns the spend categories used in the bot. These are defined the same file.
    """
    return spend_categories

def getSpendDisplayOptions():
    """
    getSpendDisplayOptions(): This functions returns the spend display options used in the bot. These are defined the same file.
    """
    return spend_display_option

def getSpendEstimateOptions():
    return spend_estimate_option

def getCommands():
    """
    getCommands(): This functions returns the command options used in the bot. These are defined the same file.
    """
    return commands

def getDateFormat():
    """
    getCommands(): This functions returns the command options used in the bot. These are defined the same file.
    """
    return dateFormat

def getTimeFormat():
    """
    def getTimeFormat(): This functions returns the time format used in the bot.
    """
    return timeFormat

def getMonthFormat():
    """
    def getMonthFormat(): This functions returns the month format used in the bot.
    """
    return monthFormat

def getChoices():
    return choices

def getBudgetOptions():
    return budget_options

def getBudgetTypes():
    return budget_types

def getUpdateOptions():
    return update_options

def getAnalyticsOptions():
    return analytics_options