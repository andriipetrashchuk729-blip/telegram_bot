import bittensor as bt

NETUID = 85
# Connect to mainnet (Finney)
sub = bt.Subtensor(network="finney")
subnet = sub.subnet(netuid = NETUID)
subnet_info = sub.get_
print(subnet_info)
print(subnet)
metagraph = sub.metagraph(netuid = NETUID)
print (f"Subnet owner hotkey: {subnet.owner_hotkey}")
print (f"Subnet incentives: {metagraph.I}")

for uid, hotkey in enumerate(metagraph.hotkeys):
    if subnet.owner_hotkey == hotkey:
        print (f"Subnet owner UID: {uid}")
        print (f"Subnet owner Incentive: {metagraph.I[uid]}")
        print (subnet.emission)
        break

# Don't forget to close when done (good practice)
sub.close()
