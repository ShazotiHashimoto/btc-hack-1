# BTC-Hack
# Made by David Gilbert
# https://github.com/DavidMGilbert/btc-hack
# https://www.davidmgilbert.com

import hashlib
import os
import hashlib
import binascii
import requests
import ecdsa
import base58
import webbrowser
from json import (load as jsonload, dump as jsondump)
from os import path
import json
import logging
import time

def generate_private_key():
    return binascii.hexlify(os.urandom(32)).decode('utf-8')

def private_key_to_WIF(private_key):
    var80 = "80" + str(private_key) 
    var = hashlib.sha256(binascii.unhexlify(hashlib.sha256(binascii.unhexlify(var80)).hexdigest())).hexdigest()
    return str(base58.b58encode(binascii.unhexlify(str(var80) + str(var[0:8]))), 'utf-8')

def private_key_to_public_key(private_key):
    sign = ecdsa.SigningKey.from_string(binascii.unhexlify(private_key), curve = ecdsa.SECP256k1)
    return ('04' + binascii.hexlify(sign.verifying_key.to_string()).decode('utf-8'))

def public_key_to_address(public_key):
    alphabet = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
    count = 0; val = 0
    var = hashlib.new('ripemd160')
    var.update(hashlib.sha256(binascii.unhexlify(public_key.encode())).digest())
    doublehash = hashlib.sha256(hashlib.sha256(binascii.unhexlify(('00' + var.hexdigest()).encode())).digest()).hexdigest()
    address = '00' + var.hexdigest() + doublehash[0:8]
    for char in address:
        if (char != '0'):
            break
        count += 1
    count = count // 2
    n = int(address, 16)
    output = []
    while (n > 0):
        n, remainder = divmod (n, 58)
        output.append(alphabet[remainder])
    while (val < count):
        output.append(alphabet[0])
        val += 1
    return ''.join(output[::-1])

def get_balance(address):
    time.sleep(0.2) #This is to avoid over-using the API and keep the program running indefinately.
    try:
        response = requests.get("https://api.blockcypher.com/v1/btc/main/addrs/" + str(address) + "/balance")
        return float(response.json()['balance']) 
    except:
        return -1

def data_export(queue):
    while True:
        private_key = generate_private_key()
        public_key = private_key_to_public_key(private_key)
        address = public_key_to_address(public_key)
        data = (private_key, address)
        queue.put(data, block = False)

def displayNotification(message,title=None,subtitle=None,soundname=None):
	"""
		Display an OSX notification with message title an subtitle
		sounds are located in /System/Library/Sounds or ~/Library/Sounds
	"""
	titlePart = ''
	if(not title is None):
		titlePart = 'with title "{0}"'.format(title)
	subtitlePart = ''
	if(not subtitle is None):
		subtitlePart = 'subtitle "{0}"'.format(subtitle)
	soundnamePart = ''
	if(not soundname is None):
		soundnamePart = 'sound name "{0}"'.format(soundname)

	appleScriptNotification = 'display notification "{0}" {1} {2} {3}'.format(message,titlePart,subtitlePart,soundnamePart)
	os.system("osascript -e '{0}'".format(appleScriptNotification))

def get_balance(address):
    time.sleep(0.2) #This is to avoid over-using the API and keep the program running indefinately.
    try:
        response = requests.get("https://api.blockcypher.com/v1/btc/main/addrs/" + str(address) + "/balance")
        return response.json()['balance']
    except:
        balance = check_BTC_balance(address)
        return balance

def get_balance_alternate(address):
    try:
        response = requests.get("https://blockstream.info/api/address/" + str(address))
        funded_txo_sum = response.json()['chain_stats']["funded_txo_sum"]
        spent_txo_sum = response.json()['chain_stats']["spent_txo_sum"]
        balance = int(funded_txo_sum) - int(spent_txo_sum)
        return balance
    except:
        balance = get_balance(address)
        return balance
    
def check_BTC_balance(address, retries=3, delay=5):
    # Check the balance of the address
    for attempt in range(retries):
        try:
            response = requests.get(f"https://blockchain.info/balance?active={address}")
            data = response.json()
            print(data)
            balance = data[address]["final_balance"]
            # return balance / 100000000  # Convert satoshi to bitcoin
            return balance
        except Exception as e:
            balance = get_balance(address)
            return balance

if __name__ == '__main__':
        while True:
            private_key = generate_private_key()
            public_key = private_key_to_public_key(private_key)
            address = public_key_to_address(public_key)
            data = (private_key, address)
            balance = get_balance_alternate(data[1])
            private_key = data[0]
            address = data[1]
            if (balance == 0):
                print("Address: " + "{:<34}".format(str(address)) + "\n" +
                   "Private key: " + str(private_key) + "\n" +
                   "WIF private key: " + str(private_key_to_WIF(private_key)) + "\n" +
                   "Public key: " + str(private_key_to_public_key(private_key)).upper() + "\n" +
                   "Balance: " + str(balance) + "\n\n")
            elif (balance != 0):
                
                file = open("found.txt","a")
                file.write("Address: " + str(address) + "\n" +
                   "Private key: " + str(private_key) + "\n" +
                   "WIF private key: " + str(private_key_to_WIF(private_key)) + "\n" +
                   "Public key: " + str(private_key_to_public_key(private_key)).upper() + "\n" +
                   "Balance: " + str(balance) + "\n\n")
                file.close()
                displayNotification("FOUND", "FOUND", "FOUND", "Alarm")
                print("Address: " + "{:<34}".format(str(address)) + "\n" +
                   "Private key: " + str(private_key) + "\n" +
                   "WIF private key: " + str(private_key_to_WIF(private_key)) + "\n" +
                   "Public key: " + str(private_key_to_public_key(private_key)).upper() + "\n" +
                   "Balance: " + str(balance) + "\n\n")
