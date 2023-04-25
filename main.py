import os
import sys


from dotenv import load_dotenv

from brains.general_brain import GeneralBrain
from brains.sys_brain import SysBrain

load_dotenv()
os.environ["TARGET_USER"], os.environ["TARGET_SERVER"] = sys.argv[1].split("@")

print('Loading GPT based sysadmin assistant...')
print('Managing server ' + os.environ["TARGET_SERVER"])
print('Using key ' + os.environ["SSH_KEY"])

gbrain = GeneralBrain()
sysbrain = SysBrain()

while True:
    try:
        message = input("\n\nHUMAN: ")

        type = gbrain.run(message)

        if type == "instruction":
            sysbrain.run(message)
        else:
            if message != "":
                sysbrain.addContext(message)
                print("BOT: Gotcha, I'll remember that.")
    except (KeyboardInterrupt, EOFError):
        print("\n\nBye! Pleasure to serve you.")
        break