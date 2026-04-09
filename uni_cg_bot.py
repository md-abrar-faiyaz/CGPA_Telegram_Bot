import os
from threading import Thread

from dotenv import load_dotenv
from flask import Flask
from waitress import serve

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# Replace 'YOUR_TOKEN_HERE' with the token from BotFather
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

# --- FLASK SETUP ---
app = Flask('')

@app.route('/')
def home():
    return "I am alive!"

def run_flask():
    port = int(os.environ.get("PORT", 5000))
    serve(app, host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_flask)
    t.start()
# -------------------


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! I am your CGPA calculator. Are you afraid about your CGPA? Don't worry, I got you. "
                                    "I will help you decide how much you need to study for your exams by letting you know "
                                    "what will be your CGPA according to the approximate GPA of the courses you provide for the current semester. "
                                    "Type /help to learn the initial command.")


# async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     await update.message.reply_text(update.message.text)

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("To get started, provide the number of credits completed and your current CGPA. "
                                    "Then provide the number of courses you took this semester, number of your current semester courses credit and the GPA you wish to get from these courses."
                                    "Format: credits_completed current_CGPA number_of_courses course1_credit GPA course2_credit GPA ......."
                                    "Example: 57 3.5 4 3 3.5 3 3.75 3 4 3 3.25"
                                    )

async def calculate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        text = update.message.text
        parts = text.split()

        if not all(p.replace('.', '', 1).isdigit() for p in parts):
            await update.message.reply_text("Please enter numbers only. Example: 57 3.5 4...")
            return


        seq = list(map(float, text.split()))
        credits_completed = seq[0]
        prev_cg = seq[1]
        curr_courses = seq[2]
        credits = seq[3::2]
        gpas = seq[4::2]

        size = len(credits)
        numerator = float()
        denominator = float()
        for i in range(size):
            denominator += credits[i]
            numerator += gpas[i] * credits[i]

        result = (credits_completed * prev_cg + numerator) / (credits_completed + denominator)

        await update.message.reply_text(f"Your projected total CGPA is: {result:.2f}")
    except Exception as e:
        await update.message.reply_text("Oops! Make sure you used the right format. See /help.")
        print(f"Error: {e}")


if __name__ == '__main__':
    keep_alive()
    app = ApplicationBuilder().token(TOKEN).build()

    # Add a handler for the /start command
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help))

    # Add a handler to echo back text messages
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), calculate))

    print("Bot is running...")
    app.run_polling()