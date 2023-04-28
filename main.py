import os
import sys


from dotenv import load_dotenv

from brains.sys_brain import SysBrain

load_dotenv()

sysbrain = SysBrain()

print('Loading GPT based sysadmin assistant...')

if len(sys.argv) > 1:
  os.environ["TARGET_USER"], os.environ["TARGET_SERVER"] = sys.argv[1].split("@")
  sysbrain.run("connect to " + os.environ["TARGET_SERVER"])
  sysbrain.run("find which linux distribution is running on this server.")

while True:
    try:
        message = input("\n\nHUMAN: ")
        sysbrain.run(message)
    except (KeyboardInterrupt, EOFError):
        print("\n\nBye! Pleasure to serve you.")
        break
