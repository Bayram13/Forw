from fastapi import FastAPI, Request
from telegram import Bot, Update
import re
import os
import uvicorn

BOT_TOKEN = os.environ.get("BOT_TOKEN")
A_CHANNEL = int(os.environ.get("A_CHANNEL"))
B_CHANNEL = int(os.environ.get("B_CHANNEL"))

bot = Bot(token=BOT_TOKEN)
app = FastAPI()

def check_conditions(text: str) -> bool:
    text_lower = text.lower()
    mc_match = re.search(r"mc[:\s]*\$?([\d.,]+)k?", text_lower)
    dev_match = re.search(r"dev\s*hold[:\s]*([\d.,]+)%", text_lower)
    holders_match = re.search(r"holders[:\s]*([\d.,]+)", text_lower)
    top10_match = re.search(r"top\s*10\s*holders[:\s]*([\d.,]+)%", text_lower)
    multiplier_match = re.search(r"\b(\d+)x\b", text_lower)

    if mc_match:
        val = float(mc_match.group(1).replace(",", ""))
        if "k" in text_lower:
            val *= 1000
        if val > 15000:
            return True
    if dev_match and float(dev_match.group(1).replace(",", "")) < 3:
        return True
    if holders_match and float(holders_match.group(1).replace(",", "")) > 30:
        return True
    if top10_match and float(top10_match.group(1).replace(",", "")) < 20:
        return True
    if multiplier_match:
        return True
    return False

@app.post(f"/{BOT_TOKEN}")
async def telegram_webhook(req: Request):
    data = await req.json()
    update = Update.de_json(data, bot)
    message = update.channel_post
    if not message or message.chat.id != A_CHANNEL:
        return {"ok": True}

    text = message.text or ""
    if check_conditions(text):
        clean_text = "\n".join([line for line in text.splitlines() if "follow" not in line.lower()])
        bot.send_message(B_CHANNEL, clean_text)

    return {"ok": True}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
