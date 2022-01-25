from network import LoRa
from machine import Pin
import socket
import time
import ubinascii
import struct
import machine

# Initialise LoRa in LORAWAN mode .
lora = LoRa(mode=LoRa.LORAWAN)
# create an ABP authentication params
dev_addr = struct.unpack(">l", ubinascii.unhexlify('260BDD0D'))[0]
nwk_swkey = ubinascii.unhexlify('C932E44328ABF60E86103B4A8DD72F07')
app_swkey = ubinascii.unhexlify('53B74EC05B1702948391D4A57E7FB64B')

# join a network using ABP (Activation By Personalization)
lora.join(activation=LoRa.ABP, auth=(dev_addr, nwk_swkey, app_swkey))

# wait until the module has joined the network
while not lora.has_joined():
    time.sleep(2.5)
print('Not yet joined... ')
print('Joined ')

# create a LoRa socket
s = socket.socket(socket.AF_LORA, socket.SOCK_RAW)
# set the LoRaWAN data rate
s.setsockopt(socket.SOL_LORA, socket.SO_DR, 5)
gpio = Pin('G23', mode = Pin.OUT)
ledOn = False

# para ler o pin da adc
adc = machine.ADC()                                 # create an ADC object
apin = adc.channel(pin='P16', attn=adc.ATTN_11DB)   # create an analog pin on P16

def check_downlink():
    try:
        data = s.recv(64)
    except OSError as e:
        print("Receiving data ERROR: ")
        print(e)

    if not data :
        return

    print(data)
    return data

while True : 
    if(lora.has_joined()):
        try:
            val = apin.voltage()                                # read an analog value in milivolts
            tmpVal = int((val * 100) / 3300)
            print("Temp: " + str(tmpVal))
            s.send(bytes([tmpVal]))
            print(lora.stats())
        except OSError as e:
            print("Receiving data ERROR: ")
            print(e)

        print(gpio.value())

        # make the socket non - blocking
        s.setblocking(False)
        # get any data received

        timeRX = 0
        for i in range(1,10) :
            data = check_downlink() 
            if data != None:
                print("Time reception: " + str(timeRX))
            if(data == b'\x01'):
                ledOn = True
            elif (data == b'\x02'):
                ledOn = False
            
            # Change the gpio value
            if(ledOn):
                gpio.value(1)
            else:
                gpio.value(0)
            
            time.sleep(1)
            timeRX = timeRX + 1
 


        
        

        