"""
File: pdf.py
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
from matplotlib import pyplot as plt
from fpdf import FPDF
import graphing
import os

# === Documentation of pdf.py ===

def run(message, bot):
    """
    run(message, bot): This is the main function used to implement the pdf save feature.
    """
    try:
        helper.read_json()
        chat_id = message.chat.id
        user_history = helper.getUserHistory(chat_id)
        msg = "Alright. I just created a pdf of your expense history!"
        bot.send_message(chat_id, msg)
        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)
        top = 0.8
        if len(user_history) == 0:
            plt.text(
                0.1,
                top,
                "No record found!",
                horizontalalignment="left",
                verticalalignment="center",
                transform=ax.transAxes,
                fontsize=20,
            )
        for rec in user_history:
            date, category, amount = rec.split(",")
            print(date, category, amount)
            rec_str = f"{amount}$ {category} expense on {date}"
            plt.text(
                0,
                top,
                rec_str,
                horizontalalignment="left",
                verticalalignment="center",
                transform=ax.transAxes,
                fontsize=14,
                bbox=dict(facecolor="red", alpha=0.3),
            )
            top -= 0.15
        plt.axis("off")
        plt.savefig("expense_history.png")
        plt.close()

        if helper.isOverallBudgetAvailable(chat_id) and helper.isCategoryBudgetByCategoryNotZero(chat_id):
            if helper.isCategoryBudgetAvailable(chat_id):
                category_budget = {}
                categories = helper.getSpendCategories()
                for cat in categories:
                    if helper.isCategoryBudgetByCategoryAvailable(chat_id, cat):
                        category_budget[cat] = helper.getCategoryBudgetByCategory(chat_id, cat)
                graphing.overall_split(category_budget)

            category_spend = {}
            categories = helper.getSpendCategories()
            for cat in categories:
                spend = helper.calculate_total_spendings_for_category_chat_id(chat_id,cat)
                if spend != 0:
                    category_spend[cat] = spend
            if category_spend != {}:
                graphing.spend_wise_split(category_spend)

            if helper.isCategoryBudgetAvailable(chat_id):
                category_spend_percent = {}
                categories = helper.getSpendCategories()
                for cat in categories:
                    if helper.isCategoryBudgetByCategoryAvailable(chat_id, cat):
                        percent = helper.calculateRemainingCategoryBudgetPercent(chat_id, cat)
                        category_spend_percent[cat] = percent
                graphing.remaining(category_spend_percent)

            if helper.getUserHistory(chat_id):
                cat_spend_dict = helper.getUserHistoryDateExpense(chat_id)
                graphing.time_series(cat_spend_dict)
            
            list_of_images = ["overall_split.png","remaining.png","time_series.png"]
            pdf = FPDF()
            pdf.add_page()
            x_coord = 20
            y_coord = 30
            for image in list_of_images:
                pdf.image(image,x=x_coord,y=y_coord,w=70,h=50)
                x_coord += 80
                if x_coord > 100:
                    x_coord = 20
                    y_coord += 60
            pdf.output("expense_report.pdf", "F")
            bot.send_document(chat_id, open("expense_report.pdf", "rb"))
            for image in list_of_images:
                os.remove(image)
        else:
            bot.send_message(chat_id, "Oh no! Set your corresponding category wise budgets using the /budget command to generate the expense report")

    except Exception as e:
        logging.exception(str(e))
        bot.reply_to(message, "Oops!" + str(e))

def create_summary_pdf(chat_id):
    """
    Creates a summary PDF of the user's expenses and returns the file path.
    """
    try:
        # Placeholder: Path where the PDF will be saved
        file_path = f"{chat_id}_expenses_summary.pdf"
        
        # Create a PDF object
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()

        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="Expenses Summary", ln=True, align='C')

        # Fetch user data to populate the PDF
        user_history = helper.getUserHistory(chat_id)
        total_expense = 0
        for rec in user_history:
            date, category, amount = rec.split(",")
            amount = float(amount)  # Ensure amount is treated as a float
            total_expense += amount
            pdf.cell(200, 10, txt=f"Date: {date}, Category: {category}, Amount: ${amount:.2f}", ln=True)

        # Add total expense to the PDF
        pdf.cell(200, 10, txt=f"Total Expense: ${total_expense:.2f}", ln=True)

        # Save the PDF to the specified file path
        pdf.output(file_path)

        return file_path
    except Exception as e:
        logging.error("Error while creating PDF: " + str(e))
        return None        
