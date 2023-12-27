# -*- coding: utf-8 -*-

import subprocess
import os
import json
import pathlib as pl
import socket
import time

####################################
# PARAMETERS
####################################
networkId = round(time.time())%10000
print(f"setting up new network with id {networkId}")
size = int(input("number of nodes besides sealing node?"))
pyFolderPath = pl.Path("../py")
keyfilePath = pl.Path("./data/keystore")

####################################
# CREATE SEALING NODE
####################################
# create folder
subprocess.run(f"mkdir node{(0)}", shell=True)
os.chdir(f".\\node{(0)}")
subprocess.run(f"xcopy {pyFolderPath} .\\py\\ /E")
subprocess.run("mkdir config", shell=True)
# create pw file
with open(pl.Path("./config/password.txt"), "w") as file:
    file.write(f"node{(0)}")
# create acount
subprocess.run('geth --datadir ./data account new --password ./config/password.txt', shell=True)
# get account address
keyfileList = os.listdir(keyfilePath)
with open(pl.Path(f"./{keyfilePath}/{keyfileList[0]}"), "r") as keyfile:
    content = json.loads(keyfile.read())
    address = f'0x{content["address"]}'
with open(pl.Path("./config/pubkey.txt"), "w") as pkf:
    pkf.write(address)
with open(pl.Path("./config/discport.txt"), "w") as dpf:
    discport = 30303
    dpf.write(str(discport))
with open(pl.Path("./config/httpport.txt"), "w") as hpf:
    httpport = 8545
    hpf.write(str(httpport))
    
###################################
# CREATE GENESIS
###################################
with open(pl.Path("../referenceGenesis.json"), "r") as genesisFile:
    genesis = json.load(genesisFile)

genesis["config"]["chainId"] = networkId
genesis["timestamp"] = hex(round(time.time()))
genesis["extraData"] = f'0x0000000000000000000000000000000000000000000000000000000000000000{address[-len(address)+2:]}0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000'

with open(pl.Path("../genesis.json"), "w") as genesisFile:
    json.dump(genesis, genesisFile)

###################################
# START SEALING NODE
###################################
# initialize with genesis file
subprocess.run("geth --datadir ./data init ../genesis.json", shell=True)
# generate and store launchcommand
launchcommand = f'geth --networkid {networkId} --datadir ./data --lightkdf --miner.gastarget 20000000 --miner.gasprice 0 --port 30303 --ipcdisable --syncmode full --snapshot=false --http --allow-insecure-unlock --http.corsdomain "*" --http.port 8545 --http.api personal,web3,eth,net,admin,clique --unlock {address} --password ./config/password.txt --mine console'
with open("startnode.cmd", "w") as sncmd:
    sncmd.write(launchcommand)
# hostname = socket.gethostname()
# local_ip = socket.gethostbyname(hostname)
local_ip = '10.97.30.77'
enode = subprocess.check_output(f"bootnode --nodekey {pl.Path('./data/geth/nodekey')} -writeaddress")
enode = f'enode://{str(enode)[2:-3]}@{local_ip}:30303'
print(enode)


###################################
# SET UP REMAINING NODES
###################################

count = 0
for count in range(size):
    os.chdir("..\\")
    subprocess.run(f"mkdir node{(count+1)}", shell=True)
    os.chdir(f".\\node{(count+1)}")
    subprocess.run(f"xcopy {pyFolderPath} .\\py\\ /E")
    subprocess.run("mkdir config", shell=True)
    with open(pl.Path("./config/password.txt"), "w") as file:
        file.write(f"node{(count+1)}")
    subprocess.run('geth --datadir ./data account new --password ./config/password.txt', shell=True)
    keyfileList = os.listdir(keyfilePath)
    with open(pl.Path(f"./{keyfilePath}/{keyfileList[0]}"), "r") as keyfile:
        content = json.loads(keyfile.read())
        address = f'0x{content["address"]}'
    with open(pl.Path("./config/pubkey.txt"), "w") as pkf:
        pkf.write(address)
    with open(pl.Path("./config/discport.txt"), "w") as dpf:
        discport = 30304+count
        dpf.write(str(discport))
    with open(pl.Path("./config/httpport.txt"), "w") as hpf:
        httpport = 8546+count
        hpf.write(str(httpport))
    with open(pl.Path("./config/logicport.txt"), "w") as lpf:
        logicport = 48174+count
        lpf.write(str(logicport))
    subprocess.run("geth --datadir ./data init ../genesis.json", shell=True)
    launchcommand = f'geth --networkid {networkId} --datadir ./data --bootnodes {enode} --lightkdf --port {discport} --ipcdisable --syncmode full --snapshot=false --http --allow-insecure-unlock --http.corsdomain "*" --http.port {httpport} --http.api personal,web3,eth,net,admin,clique --unlock {address} --password ./config/password.txt console' #--netrestrict "127.0.0.1/8"
    with open("startnode.cmd", "w") as sncmd:
        sncmd.write(launchcommand)
    #subprocess.run(launchcommand, shell=True)
    count += 1
