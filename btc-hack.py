# BTC-Hack
# Made by David Gilbert
# https://github.com/DavidMGilbert/btc-hack
# https://www.davidmgilbert.com

try:
    import sys
    import os
    import time
    import hashlib
    import binascii
    import multiprocess
    from multiprocess import Process, Queue
    from multiprocess.pool import ThreadPool
    import threading
    import base58
    import ecdsa
    import requests

# If required imports are unavailable, we will attempt to install them!

except ImportError: 
    import subprocess
    subprocess.check_call(["python3", '-m', 'pip', 'install', 'base58==1.0.0'])
    subprocess.check_call(["python3", '-m', 'pip', 'install', 'ecdsa==0.13'])
    subprocess.check_call(["python3", '-m', 'pip', 'install', 'requests==2.19.1'])
    import base58
    import ecdsa
    import requests

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
def get_balance_alternate(address):
    try:
        response = requests.get("https://blockstream.info/api/address/" + str(address))
        funded_txo_sum = response.json()['chain_stats']["funded_txo_sum"]
        spent_txo_sum = response.json()['chain_stats']["spent_txo_sum"]
        balance = int(funded_txo_sum) - int(spent_txo_sum)
        return balance
    except:
        try:
            time.sleep(5)
            response = requests.get("https://blockstream.info/api/address/" + str(address))
            funded_txo_sum = response.json()['chain_stats']["funded_txo_sum"]
            spent_txo_sum = response.json()['chain_stats']["spent_txo_sum"]
            balance = int(funded_txo_sum) - int(spent_txo_sum)
            return balance
            # balance = get_balance(address)
            # return balance
        except:
            return -1
        
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
    if sys.platform == "darwin":
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

def worker(queue):
    while True:
        if not queue.empty():
            data = queue.get(block = True)
            balance = get_balance_alternate(data[1])
            process(data, balance)

def process(data, balance):
    private_key = data[0]
    address = data[1]
    if (balance == 0):
        print("{:<34}".format(str(address)) + ": " + str(balance))
    if (balance > 0):
        file = open("found.txt","a")
        file.write("address: " + str(address) + "\n" +
                   "private key: " + str(private_key) + "\n" +
                   "WIF private key: " + str(private_key_to_WIF(private_key)) + "\n" +
                   "public key: " + str(private_key_to_public_key(private_key)).upper() + "\n" +
                   "balance: " + str(balance) + "\n\n")
        file.close()
        displayNotification("FOUND", "FOUND", "FOUND", "Alarm")

def thread(iterator):
    processes = []
    data = Queue()
    data_factory = Process(target = data_export, args = (data,))
    data_factory.daemon = True
    processes.append(data_factory)
    data_factory.start()
    work = Process(target = worker, args = (data,))
    work.daemon = True
    processes.append(work)
    work.start()
    data_factory.join()

if __name__ == '__main__':
    try:
        pool = ThreadPool(processes = multiprocess.cpu_count()*2)

        pool.map(thread, range(0, 1)) # Limit to single CPU thread as we can only query 300 addresses per minute
    except:
        pool.close()
        exit()
