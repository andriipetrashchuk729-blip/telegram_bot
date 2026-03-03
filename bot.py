# auto_message_bot.py
import logging
# from turtle import update
from scalecodec import Null
from telegram.ext import ApplicationBuilder, ContextTypes, JobQueue

from telegram import Update
from telegram.ext import CommandHandler


import threading
import bittensor as bt

NETUID = []
for i in range(1, 127):
    NETUID.append(i)


owner_i = [0] * 126
last_owner_i = [0] * 126
sub_name = [" "] * 126
sub_emission = [0] * 126

def get_info_owner_burn():
    global owner_i, sub_name, sub_emission
    while (True):
        sub = bt.Subtensor(network="finney")
        subnet = sub.subnet(netuid = NETUID)
        metagraph = sub.metagraph(netuid = NETUID)
        print (f"Subnet owner hotkey: {subnet.owner_hotkey}")
        # print (f"Subnet incentives: {metagraph.I}")

        for uid, hotkey in enumerate(metagraph.hotkeys):
            if subnet.owner_hotkey == hotkey:
                print (f"Subnet owner UID: {uid}")
                print (f"Subnet owner Incentive: {metagraph.I[uid]}")
                owner_i = metagraph.I[uid]
                sub_name = metagraph.name
                sub_emission = float(subnet.tao_in_emission) * 200
                print(float(subnet.tao_in_emission))
                break

t = threading.Thread(target = get_info_owner_burn)
t.start()


# Logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Function to send the repeated message
async def send_message(context: ContextTypes.DEFAULT_TYPE):
    global owner_i, last_owner_i, sub_name, sub_emission
    if (last_owner_i != owner_i):
        last_owner_i = owner_i
        chat_id = context.job.chat_id  # chat ID where the message is sent
        await context.bot.send_message(chat_id=chat_id, text=f" Subnet UID: {NETUID} \n Emission: {sub_emission:.2f}% \n Name: {sub_name} \n Owner's Incentive: {last_owner_i:.2f}")


# Optional: command to start the auto messages

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    print (chat_id)
    # Schedule repeating job every 3 seconds
    context.job_queue.run_repeating(send_message, interval=5, first=0, chat_id=chat_id, name=str(chat_id))
    await update.message.reply_text("Auto messages when the owner's incentive is changed.")

# Optional: command to stop auto messages
async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    jobs = context.job_queue.get_jobs_by_name(str(chat_id))
    if not jobs:
        await update.message.reply_text("No auto messages running.")
        return
    for job in jobs:
        job.schedule_removal()
    await update.message.reply_text("Auto messages stopped.")

# Main function
def main():
    BOT_TOKEN = "8685413310:AAEkXOsb8M7V_oFbI3BzYmmiHMWtnjacoyw"  # Replace with your bot token

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Command handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stop", stop))

    # Run bot
    app.run_polling()

if __name__ == "__main__":
    main()