import os, sys
import random
import string

def sendNotification(message):
	os.system(f'notify-send "firectl" "{message}"')

def uuid(length=8):
	# Create a list of all possible characters
	characters = string.ascii_lowercase + string.digits

	# Generate a random string by selecting random characters from the list
	random_string = "".join(random.choice(characters) for _ in range(length))

	return random_string

def printError(message):
	RED = '\033[91m'
	END = '\033[0m'

	error_msg = f"{RED}Error: {message}{END}"

	print(error_msg, file=sys.stderr)

	sendNotification(f"Error: {message}")