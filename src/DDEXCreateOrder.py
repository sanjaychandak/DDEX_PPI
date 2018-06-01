import requests
import json
import configparser
from datetime import datetime
from web3.auto import w3
from eth_account.messages import defunct_hash_message

print("Automate piedpipercoin (PPI-ETH)")
print("-----------------------------------")

# Read configuration (ETH Address and PrivateKey)
print("-----------------------------------")
config = configparser.ConfigParser()
config.read('config.ini')
address= config.get('DDEX', 'eth_address')
private_key=config.get('DDEX', 'private_key')
print("Properties Loaded....", config.__len__())
print("-----------------------------------")

# Get time in milliseconds from current Date
def dt_to_ms(dt):
    epoch = datetime.utcfromtimestamp(0)
    delta = dt - epoch
    return int(delta.total_seconds() * 1000)

# Sign Unsigned Order (text)
def buildUnsignedOrder(message):
    #print("message: ", message)
    message_hash = defunct_hash_message(text=message)
    signed_msg = w3.eth.account.signHash(message_hash, private_key=private_key)
    signed_msg = signed_msg.signature
    signature = w3.toHex(signed_msg)
    return  signature

# Sign Signed Order (hexstr)
def buildsignedOrder(orderId):
    #print("orderId: ", orderId)
    message_hashOrder = defunct_hash_message(hexstr=orderId)
    signed_msgOrder = w3.eth.account.signHash(message_hashOrder, private_key=private_key)
    signed_msgOrder = signed_msgOrder.signature
    signatureOrder = w3.toHex(signed_msgOrder)
    return signatureOrder

# Set current date time
now = datetime.utcnow()
timeinms = str(dt_to_ms(now))
message = 'HYDRO-AUTHENTICATION@' + timeinms

# build Unsigned Order
print("Start buildUnsignedOrder:")
url = 'https://api.ddex.io/v2/orders/build'

unsigned_payload = {
  "amount": config.get('CREATE_ORDER', 'amount'),
  "price": config.get('CREATE_ORDER', 'price'),
  "side": config.get('CREATE_ORDER', 'side'),
  "marketId": config.get('CREATE_ORDER', 'marketId')
}

# Hydro-Authentication: {Address}#{Message}#{Signature}
signature = buildUnsignedOrder(message)
#print('signature: ',signature)

headers = {'content-type': 'application/json',
           'Hydro-Authentication': address+'#'+message+'#'+signature}
#print('Hydro-Authentication : ' +address+'#'+message+'#'+signature)


unsigned_payload = requests.post(url, data=json.dumps(unsigned_payload), headers=headers)
print(unsigned_payload.content)
order=json.loads(unsigned_payload.content)

orderId=order['data']['order']['id']
print('OrderId: ', orderId)
print("Stop buildUnsignedOrder:")
print("-----------------------------------")


print("Start buildsignedOrder:")

signatureOrder=buildsignedOrder(orderId)

payload_order = {
  "orderId": orderId,
  "signature": signatureOrder
}

#print('signatureOrder: ',signatureOrder)
url_order= 'https://api.ddex.io/v2/orders'
print('OrderId: ', orderId)
signedorder = requests.post(url_order, data=json.dumps(payload_order), headers=headers)
print("Order sent: ", signedorder.content)
print("Status: ", signedorder.status_code) #200 OK, other than that order is not executed.

print("Stop buildsignedOrder:")
print("-----------------------------------")

#Get your order
getorder= requests.get('https://api.ddex.io/v2/orders/'+orderId, headers=headers)
print(getorder.content)
print("-----------------------------------")



