import re
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

# ⚙️ Parametrlər
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"  # @BotFather-dan aldığın token
A_CHANNEL = -100123456789           # Mənbə kanal ID
B_CHANNEL = -100987654321           # Hədəf kanal ID

# --- Mesajı analiz edən funksiya ---
def check_conditions(text: str) -> bool:
    text_lower = text.lower()
    mc_match = re.search(r"mc[:\s]*\$?([\d.,]+)k?", text_lower)
    dev_match = re.search(r"dev\s*hold[:\s]*([\d.,]+)%", text_lower)
    holders_match = re.search(r"holders[:\s]*([\d.,]+)", text_lower)
    top10_match = re.search(r"top\s*10\s*holders[:\s]*([\d.,]+)%", text_lower)
    multiplier_match = re.search(r"\b(\d+)x\b", text_lower)

    # Şərtlər
    if mc_match:
        val = float(mc_match.group(1).replace(",", ""))
        if "k" in text_lower:
            val *= 1000
        if val > 15000:
            return True

    if dev_match:
        val = float(dev_match.group(1).replace(",", ""))
        if val < 3:
            return True

    if holders_match:
        val = float(holders_match.group(1).replace(",", ""))
        if val > 30:
            return True

    if top10_match:
        val = float(top10_match.group(1).replace(",", ""))
        if val < 20:
            return True

    if multiplier_match:
        return True

    return False


# --- Yeni mesajlarda işləyən funksiya ---
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.channel_post:
        return
    if update.channel_post.chat_id != A_CHANNEL:
        return

    text = update.channel_post.text or ""
    if check_conditions(text):
        # “Follow” sətrlərini sil
        clean_text = "\n".join(
            [line for line in text.splitlines() if "follow" not in line.lower()]
        )
        await context.bot.send_message(chat_id=B_CHANNEL, text=clean_text)


# --- Botun işə salınması ---
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.ALL, message_handler))
    print("✅ Bot işə düşdü...")
    app.run_polling()


if __name__ == "__main__":
    main()
