import numpy as np
import csv
import telegram_send
# import keyboard
import time

print("hi")

time.sleep(100)

telegram_send.send(messages=["Error: Training Failed after 1023 Epochs", "Average Score = 32.43, Average Entropy = 0.52"])

time.sleep(10)

telegram_send.send(messages=["Rerunning Model"])
