# auto_message_bot.py
import logging
# from turtle import update
from scalecodec import Null
from telegram.ext import ApplicationBuilder, ContextTypes, JobQueue

from telegram import Update
from telegram.ext import CommandHandler


import threading
import bittensor as bt

init_flag = [0] * 126

NETUID = []
for i in range (1, 127):
    NETUID.append(i)

owner_i = [0] * 126
last_owner_i = [-1] * 126
sub_name = [" "] * 126
sub_emission = [0] * 126

def get_info_owner_burn():
    global owner_i, sub_name, sub_emission, init_flag
    while (True):
        for i in range (1,129):
            
            sub = bt.Subtensor(network="finney")
            subnet = sub.subnet(netuid = i)
            metagraph = sub.metagraph(netuid = i)
            print("threading 1")
            print ("Subnet UID", i)
            print (f"Subnet owner hotkey: {subnet.owner_hotkey}")
            # print (f"Subnet incentives: {metagraph.I}")

            for uid, hotkey in enumerate(metagraph.hotkeys):
                if subnet.owner_hotkey == hotkey:
                    print (f"Subnet owner UID: {uid}")
                    print (f"Subnet owner Incentive: {metagraph.I[uid]}")
                    owner_i[i-1] = metagraph.I[uid]*100
                    sub_name[i-1] = metagraph.name
                    sub_emission[i-1] = float(subnet.tao_in_emission) * 200
                    print(float(subnet.tao_in_emission))
                    break
            if init_flag[i-1] < 2:
                init_flag[i-1] = init_flag[i-1]+1

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
    for i in NETUID:
        chat_id = context.job.chat_id
        if init_flag[i-1] == 1:
            if (last_owner_i[i-1] != owner_i[i-1]):
                await context.bot.send_message(chat_id=chat_id, text=f" SN {i} {sub_name[i-1]} E: {sub_emission[i-1]:.2f}% BURN: {owner_i[i-1]:.2f}%")
                last_owner_i[i-1] = owner_i[i-1]
        if init_flag[i-1] == 2:
            if (last_owner_i[i-1] != owner_i[i-1]):   
                await context.bot.send_message(chat_id=chat_id, text=f" SN {i} {sub_name[i-1]} E: {sub_emission[i-1]:.2f}%  BURN: {last_owner_i[i-1]:.2f} -> {owner_i[i-1]:.2f}%")
                last_owner_i[i-1] = owner_i[i-1]
# Optional: command to start the auto messages

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    print (chat_id)
    # Schedule repeating job every 3 seconds
    context.job_queue.run_repeating(send_message, interval=3, first=0, chat_id=chat_id, name=str(chat_id))
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