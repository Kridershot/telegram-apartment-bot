import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
from config import TELEGRAM_BOT_TOKEN, RECEIVER_CHAT_ID

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
httpx_logger = logging.getLogger("httpx")
httpx_logger.setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

user_states = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    user_states[user_id] = True    
    logger.info(f'Пользователь {update.effective_user.first_name} (ID: {user_id}) нажал /start')
    await update.message.reply_text(f'Здравствуйте, {update.effective_user.first_name}!\n\nНапишите цель визита и я ее передам владельцу квартиры даже если его нет дома.')

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    if user_states.get(user_id):
        message_text = update.message.text
        logger.info(f'Пользователь {update.effective_user.first_name} (ID: {user_id}) отправил сообщение: {message_text}')
        await send_message_to_owner(context, f'Пользователь {update.effective_user.first_name} оставил сообщение.\n\nЦель визита: {message_text}\n\nСсылка на пользователя: https://t.me/{update.effective_user.username}')
        await update.message.reply_text(f'Хорошо, я передам это сообщение. Хорошего дня!')
        context.application.stop_running()
    else:
        await update.message.reply_text(f'Пожалуйста, введите /start, прежде чем отправлять сообщения.')
    user_states[user_id] = False

async def send_message_to_owner(context: ContextTypes.DEFAULT_TYPE, message: str) -> None:
    await context.bot.send_message(chat_id=RECEIVER_CHAT_ID, text=message)

def main() -> None:
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    try:
        app.run_polling()
    except Exception as e:
        logger.error("Ошибка при запуске бота: %s", e)

if __name__ == "__main__":
    main()