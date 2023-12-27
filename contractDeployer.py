import pathlib as pl
import time
import json
from os import chdir
from web3.auto.gethdev import Web3
from web3.middleware import geth_poa_middleware
from solcx import compile_source, install_solc
install_solc("0.8.1")   #install language version

def b32(val):
        return Web3.toHex(Web3.toBytes(val).rjust(32, b'\0'))

contractPath = pl.Path("./contracts/DoubleAuction.sol")
with open(pl.Path("./node0/config/pubkey.txt"), "r") as file:
    timer = Web3.toChecksumAddress(file.read())
    print(f"timer: {timer}")
node = "http://127.0.0.1:8545"
with open(pl.Path("./node0/config/password.txt"), "r") as pwfile:
    nodePw = pwfile.read()

###################################
# PREP W3 AND ACCOUNT
###################################

w3 = Web3(Web3.HTTPProvider(node))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)
retVal = w3.geth.personal.unlockAccount(w3.eth.accounts[0], nodePw, 200)
print(f'unlocked account: {w3.eth.accounts[0]}: {retVal}')

###################################
# DEPLOY CONTRACT
###################################

with open(contractPath, "r") as contract1:
    contract1Compiled = compile_source(contract1.read())
# from https://web3py.readthedocs.io/en/stable/contracts.html
# retrieve the contract interface
contract_id, contract_interface = contract1Compiled.popitem()
# get bytecode / bin
bytecode = contract_interface['bin']
# get abi
abi = contract_interface['abi']

contract1 = w3.eth.contract(abi=abi, bytecode=bytecode)
# Submit the transaction that deploys the contract
tx_hash = contract1.constructor(timer).transact({"from": w3.eth.accounts[0]})
# Wait for the transaction to be mined, and get the transaction receipt
time.sleep(4)
tx_receipt = w3.eth.getTransactionReceipt(b32(tx_hash))
contract1 = w3.eth.contract(address=tx_receipt.contractAddress, abi=abi)
print(f'deployed {contractPath} sucessfully')

###################################
# distribute files
###################################
rootdir = pl.Path('./')
# For absolute paths instead of relative the current dir
directory_list = [d for d in rootdir.resolve().glob('**/*') if d.is_dir() and d.name=="config"]
for node in directory_list:
    chdir(node)
    with open(pl.Path("./contractAbi.json"), "w") as file:
        json.dump(abi, file)
    with open(pl.Path("./contractAddress.txt"), "w") as file:
        file.write(tx_receipt.contractAddress)