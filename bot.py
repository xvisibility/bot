import logging
import os
import sqlite3
from pathlib import Path
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Get BOT_TOKEN from environment variable (Render)
BOT_TOKEN = os.environ.get('BOT_TOKEN')

# Check if token is available
if not BOT_TOKEN:
    logger.error("No BOT_TOKEN found in environment variables!")
    raise ValueError("BOT_TOKEN environment variable is required")

# Initialize database with absolute path
db_path = Path(__file__).parent / 'bot.db'
conn = sqlite3.connect(db_path, check_same_thread=False)
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, balance REAL DEFAULT 0.0)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS orders (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, service TEXT, amount INTEGER, status TEXT)''')
conn.commit()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message with the main menu when the command /start is issued."""
    keyboard = [
        [InlineKeyboardButton("💰 Wallet", callback_data='wallet')],
        [InlineKeyboardButton("📈 Buy X Followers Real", callback_data='buy_followers')],
        [InlineKeyboardButton("❤️ Buy X Likes Real", callback_data='buy_likes')],
        [InlineKeyboardButton("➕ Add X Account", callback_data='add_account')],
        [InlineKeyboardButton("🔗 Referral", callback_data='referral')],
        [InlineKeyboardButton("🚀 Boost Volume", callback_data='boost_volume')],
        [InlineKeyboardButton("🛡️ Hire Mods", callback_data='hire_mods')],
        [InlineKeyboardButton("⚔️ Hire Raiders", callback_data='hire_raiders')],
        [InlineKeyboardButton("💻 Hire Dev", callback_data='hire_dev')],
        [InlineKeyboardButton("🌐 Get a Website", callback_data='get_website')],
        [InlineKeyboardButton("🎨 Graphics Design", callback_data='graphics_design')],
        [InlineKeyboardButton("💬 Real Comments", callback_data='real_comments')],
        [InlineKeyboardButton("📱 Real TG", callback_data='real_tg')],
        [InlineKeyboardButton("🛒 Orders", callback_data='orders')],
        [InlineKeyboardButton("📝 Subscribe", callback_data='subscribe')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Welcome to X VisibilityBot! Choose a service:', reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle button clicks."""
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == 'wallet':
        user_id = query.from_user.id
        cursor.execute("SELECT balance FROM users WHERE user_id=?", (user_id,))
        result = cursor.fetchone()
        balance = result[0] if result else 0.0
        await query.edit_message_text(f"Your wallet balance: ${balance:.2f}")
    elif data == 'buy_followers':
        await query.edit_message_text("Buy X Followers Real: Select quantity (e.g., 100 for $5). Reply with /buy 100 followers")
    # Add similar handlers for other buttons (buy_likes, add_account, etc.)
    # For now, placeholder for others
    else:
        await query.edit_message_text(f"Coming soon: {data.replace('_', ' ').title()}")

def main() -> None:
    """Start the bot."""
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))
    
    # Check if running on Render (use webhooks) or locally (use polling)
    if os.environ.get('RENDER'):
        # Webhook configuration for Render
        port = int(os.environ.get('PORT', 8443))
        webhook_url = f"https://{os.environ.get('RENDER_EXTERNAL_HOSTNAME')}/{BOT_TOKEN}"
        
        logger.info(f"Starting webhook on port {port}")
        application.run_webhook(
            listen="0.0.0.0",
            port=port,
            url_path=BOT_TOKEN,
            webhook_url=webhook_url
        )
    else:
        # Polling for local development
        logger.info("Starting polling for local development")
        application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
