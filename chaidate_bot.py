import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from pymongo import MongoClient

# Database connection
client = MongoClient("mongodb+srv://chaidateadmin:Chaidate123@cluster0.wx5xbdp.mongodb.net/")
db = client.chaidate_bot
users = db.users

# Your bot token from BotFather
BOT_TOKEN = "7972020860:AAGXRfKRfNcOPrD3UDKZv-j75_WRUaua5_8"  # Make sure this has your real token!

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(
        f"Hello {user.first_name}! 👋\n\n"
        "Welcome to Chaidate! 💕\n"
        "Let's find your perfect match!\n\n"
        "Use /profile to create your dating profile!"
    )

async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("👦 Male", callback_data="gender_male")],
        [InlineKeyboardButton("👩 Female", callback_data="gender_female")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "Let's create your profile!\n"
        "First, choose your gender:",
        reply_markup=reply_markup
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    if query.data.startswith("gender_"):
        gender = query.data.split("_")[1]
        # Save gender to database
        users.update_one(
            {"user_id": user_id},
            {"$set": {"gender": gender, "step": "age"}},
            upsert=True
        )
        await query.edit_message_text("Great! Now send me your age (just type the number):")
    
    elif query.data == "finish_profile":
        await query.edit_message_text("🎉 Profile completed! Use /find to discover matches!")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text
    
    user_data = users.find_one({"user_id": user_id})
    
    if user_data and user_data.get("step") == "age":
        try:
            age = int(text)
            if 18 <= age <= 100:
                # Save age and ask for name
                users.update_one(
                    {"user_id": user_id},
                    {"$set": {"age": age, "step": "name"}}
                )
                await update.message.reply_text(f"Age {age} saved! 😊 Now what's your name?")
            else:
                await update.message.reply_text("Please enter a valid age between 18-100:")
        except:
            await update.message.reply_text("Please enter a valid number for age:")
    
    elif user_data and user_data.get("step") == "name":
        # Save name and finish profile
        users.update_one(
            {"user_id": user_id},
            {"$set": {"name": text, "step": "complete"}}
        )
        
        keyboard = [[InlineKeyboardButton("🎉 Finish Profile", callback_data="finish_profile")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            f"Nice to meet you, {text}! ✨\n\n"
            "Your profile is ready!\n"
            "• Gender: Saved ✅\n"
            "• Age: Saved ✅\n"
            "• Name: Saved ✅\n\n"
            "Click below to finish:",
            reply_markup=reply_markup
        )

def main():
   app = Application.builder().token(BOT_TOKEN).build()

# Register handlers
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT, handle_message))
app.add_handler(CallbackQueryHandler(button))

print("Bot is running...")
app.run_polling()

    main()
