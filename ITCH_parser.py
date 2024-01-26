# -*- coding: utf-8 -*-
"""parser.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1c5cQyf1tye1MFPaQSMrQot_98te0x9bp
"""

#Author : Mohammad Anas Khan
#Email: anaskhan9455363866@gmail.com
#Phone Number: +918769885746
from google.colab import drive
drive.mount('/content/drive')

#Parser for NASDAQ ITCH 50 data file to calculate VWAP( Volume Weighted Average Price)

#Defining the offset of all types of messages in the order book ( size - 1 ) as include size except the first character
offset_map = dict()
#messages related to stock a.k.a related to VWAP
offset_map["R"] = 38 # Stock Directory
offset_map["A"] = 35 # Added orders with attribution message
offset_map["F"] = 39 # Added orders without attribution message
offset_map["E"] = 30 # Executed orders with links to previously added orders
offset_map["C"] = 35 # Executed orders without links to previous added orders
offset_map["U"] = 34 # Modifications to previous  orders
offset_map["P"] = 43 # Undisplayable non-cross orders executed

#messages not related to VWAP
#cross trades are not included in VWAP calculations
offset_map["S"] = 11
offset_map["H"] = 24
offset_map["Y"] = 19
offset_map["L"] = 25
offset_map["V"] = 34
offset_map["W"] = 11
offset_map["K"] = 27
offset_map["J"] = 34
offset_map["h"] = 20
offset_map["X"] = 22
offset_map["D"] = 18
offset_map["Q"] = 39
offset_map["B"] = 18
offset_map["I"] = 49
offset_map["N"] = 19
offset_map["O"] = 47

#Zipping the file
import gzip
fileName = '/content/drive/MyDrive/01302019.NASDAQ_ITCH50.gz'
file = gzip.open(fileName, 'rb')
print("Start Parsing the file: %s", fileName )

#Using the struct module for dealing with byte order data
import struct
open = 0
stock_name = dict() #To store names of stocks
price_of_orders = dict() #To store price of orders with respect to their reference numbers
#Not maintaining number of stocks per order as it will be given at the time of execute message
settled_orders = []
msg_type = file.read(1) #To read the type of messages
ParsedSize = 0
ParsedMessages = 0

#Formatting used to unpack the messages:
# 'H',   int of length 2 bytes
# 'I',   unsigned int of length of 4 bytes
# '6s',  int of length 6 bytes, as character array and convert later
# 'Q',   unsigned long int of length 8 bytes
# 'Xs',  character array of lenght X bytes


def getTime(time):
    nbytes = struct.pack('>ss6s',b'\x00', b'\x00', time )
    ntimestamp = struct.unpack('>Q', nbytes)
    return ntimestamp[0]

while msg_type:
    msg_type = msg_type.decode() #Decoding the bytes object to character object
    if msg_type in offset_map.keys():
        stride = offset_map[msg_type]
        msg = file.read(stride)
        ParsedSize += stride
        if msg_type == "S":
            message = struct.unpack('>HH6ss',msg)
            cur_time = getTime(message[2])
            if message[3].decode() == "Q": #To track the market time
                open = cur_time
                print("Market opened at %d: " % cur_time)
            else:
                pass
        elif msg_type == "R": #Stock Directory message
            message = struct.unpack('>HH6s8sssIss2ssssssIs', msg )
            name = message[3].decode().strip()
            stockID = message[0]
            stock_name[stockID] = name
        elif msg_type == "H": #Stock Trading Action ( not affecting VWAP )
            pass
        elif msg_type == "Y": #Reg SHO Short Sale Price Test RestrictedIndicator( not affecting VWAP )
            pass
        elif msg_type == "L": #Market Participant Position ( not affecting VWAP )
            pass
        elif msg_type == "V": #MWCB Decline Level Message ( not affecting VWAP )
            pass
        elif msg_type == "W": #MWCB Status Message ( not affecting VWAP )
            pass
        elif msg_type == "K": #Quoting Period Update ( not affecting VWAP )
            pass
        elif msg_type == "J": #Limit Up – Limit Down (LULD) Auction Collar( not affecting VWAP )
            pass
        elif msg_type == "h": #Operational Halt ( not affecting VWAP )
            pass
        elif msg_type == "A": #Add order message
            message = struct.unpack('>HH6sQsI8sI', msg )
            reference_no = message[3]
            price = message[7]
            price_of_orders[reference_no] = price
        elif msg_type == "F": #Add order with mpid
            message = struct.unpack('>HH6sQsI8sI4s', msg )
            reference_no = message[3]
            price = message[7]
            price_of_orders[reference_no] = price
        elif msg_type == "E": #Order Executed withour price message
            message = struct.unpack('>HH6sQIQ', msg )
            stock = message[0]
            quantity = message[4]
            price = price_of_orders[reference]
            reference_no = message[3]
            cur_time = getTime(message[2])
            orderTuple = (stock,price,quantity,cur_time)
            settled_orders.append(orderTuple)
        elif msg_type == "C": #Order Executed with price message
            message = struct.unpack('>HH6sQIQsI', msg )
            include = message[6]
            if include.decode() == "Y": #To be displayed
                stock = message[0]
                quantity = message[4]
                price = message[7]
                reference_no = message[3]
                cur_time = getTime(message[2])
                orderTuple = (stock,price,quantity,cur_time)
                settled_orders.append(orderTuple)
            else: #Not to be displayed
                pass
        elif msg_type == "X": #Order Cancel Message ( not affecting VWAP )
            pass
        elif msg_type == "D": #Order Delete Message ( not affecting VWAP )
            pass
        elif msg_type == "U": #Order Replace message
            message = struct.unpack('>HH6sQQII', msg )
            reference = message[4] # New reference number created
            price = message[6]
            price_of_orders[reference] = price
        elif msg_type == "P": #Non displayable non cross message
            message = struct.unpack('>HH6sQsIQIQ',msg)
            stock = message[0]
            quantity = message[5]
            price = message[7]
            cur_time = getTime(message[2])
            orderTuple = (stock ,price,quantity,cur_time)
            settled_orders.append(orderTuple)
        elif msg_type == "Q": #Cross Trade message ( not to be included in VWAP calculation)
            pass
        elif msg_type == "B": #Broken Trade message ( not affecting VWAP )
            pass
        elif msg_type == "I": #Net Order Imbalance Indicator (NOII)Message ( not affecting VWAP )
            pass
        elif msg_type == "N": #Retail Price Improvement Indicator(RPII) ( not affecting VWAP )
            pass
        elif msg_type == "O": # Direct Listing with Capital Raise (DLCR) securities ( not affecting VWAP )
            pass
    ParsedSize += 1
    ParsedMessages += 1
    msg_type = file.read(1)

assert open == 34200000036157 #Market should open at 9:30
print("Order book formed")

#Calcaulating the typical price volume and typical volume of the stocks by the hour
ns_time_hour = 3600000000000 #Nanosecond time per hour
pv = dict() #To maintian price volume of trades by the hour
v = dict() #To maintain volume of the trades by the hour
#Initializing
for stock_id in stock_name.keys():
    stock_pv = dict()
    stock_v = dict()
    for hour in range(10,17): #10 am to 4 pm are the hours which are relevant
      stock_pv[hour] = 0
      stock_v[hour] = 0
    pv[stock_id] = stock_pv
    v[stock_id] = stock_v

#Calculating Price volume and volume
for order in settled_orders:
    stock_id , price , quantity , time = order
    if time < open:
        continue
    cur_hour = ( time + ns_time_hour - 1 ) // ns_time_hour
    pv[stock_id][cur_hour] += price * quantity
    v[stock_id][cur_hour] += quantity

#VWAP = (Cumulative typical price x volume)/cumulative volume
vwap = dict()
for stock_id in stock_name.keys():
    stock_vwap = dict()
    cum_typ_price_volume = 0 #To track cummulative typ price volume
    cum_volume = 0 #To track cummulative volume
    for hour in range(10,17):
        cum_typ_price_volume += pv[stock_id][hour]
        cum_volume += v[stock_id][hour]
        if cum_volume > 0:
          stock_vwap[hour] = cum_typ_price_volume / cum_volume
        else:
          stock_vwap[hour] = 0
    vwap[stock_id] = stock_vwap

#Using pandas to output to store VWAP
import pandas as pd
output = pd.DataFrame()


st = []
vwap_output = dict()
for hour in range(10,17):
    this_hour = []
    vwap_output[hour] = this_hour
for stock_id in stock_name.keys():
    st.append(stock_name[stock_id])
    for hour in range(10,17):
        vwap_output[hour].append(vwap[stock_id][hour])

output["Stock Names"] = st
for hour in range(10,17):
    display_hour = "{}:00".format(hour)
    output[display_hour] = vwap_output[hour]

output.to_csv( "vwap.csv")
print("File Parsing Success")