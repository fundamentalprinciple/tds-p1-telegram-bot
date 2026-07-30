from logger import log_interaction
from telegram import Update
from agent import DataAnalystAgent
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

agent = DataAnalystAgent()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hello! I'm alive."
    )


async def echo(update, context):
    prompt = (
        update.message.text
        or update.message.caption
        or ""
    )
    
    if update.message.document:
        print("Received document:", update.message.document.file_name)
        file = await update.message.document.get_file()
        path = f"data/{update.message.document.file_name}"
        await file.download_to_drive(path)

        prompt += f"\n\nAttached file: {path}"

    chat_id = update.effective_chat.id

    reply = agent.reply(chat_id, prompt)
    
    print(reply)
    await update.message.reply_text(reply)

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(
        MessageHandler(
            (filters.TEXT | filters.Document.ALL) & ~filters.COMMAND, 
            echo,
        )
    )

    print("Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()
