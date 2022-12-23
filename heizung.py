# Testprogramm Viessmann Heizung V200KW1
# verbunden über Optilink Kabel (USB)
# Mark König, Nov. 2022


import serial
# pip install pyserial

import paho.mqtt.client as mqtt
import sys
import time
import json
import ssl
#pip install paho-mqtt

import traceback

MQTT_USER = 'fritz'
MQTT_PASSWORD = '***'
MQTT_SERVER = '192.168.178.156'

topic1 = "homeassistant/sensor/vm-kesseltemperatur"
payload1 = {"unique_id": "vm-kesseltemperatur",
               "device_class": "temperature",
               "name": "Kesseltemperatur",
               "state_topic": "homeassistant/sensor/vm-kesseltemperatur/state",
               "unit_of_measurement": "°C",
               "icon": "mdi:heat-wave",
               "value_template": "{{ value_json.temperature }}" }
topic2 = "homeassistant/sensor/vm-aussentemperatur"
payload2 = {"unique_id": "vm-aussentemperatur",
               "device_class": "temperature",
               "name": "Aussentemperatur",
               "state_topic": "homeassistant/sensor/vm-aussentemperatur/state",
               "unit_of_measurement": "°C",
               "icon": "mdi:thermometer",
               "value_template": "{{ value_json.temperature }}" }
topic3 = "homeassistant/sensor/vm-brennerstarts"
payload3 = {"unique_id": "vm-brennerstarts",
               "name": "Brennerstarts",
               "state_topic": "homeassistant/sensor/vm-brennerstarts/state",
               "icon": "mdi:counter",
               "value_template": "{{ value_json.counter }}" }
topic4 = "homeassistant/sensor/vm-pumpe_m1"
payload4 = {"unique_id": "vm-pumpe_m1",
                "name": "Pumpe M1",
                "icon": "mdi:heat-pump-outline",
                "state_topic": "homeassistant/sensor/vm-pumpe_m1/state",
                "value_template": "{{ value_json.pump }}" }
topic5 = "homeassistant/sensor/vm-pumpe_speicher"
payload5 = {"unique_id": "vm-pumpe_speicher",
                "name": "Pumpe Speicher",
                "icon": "mdi:heat-pump-outline",
                "state_topic": "homeassistant/sensor/vm-pumpe_speicher/state",
                "value_template": "{{ value_json.pump }}" }
topic6 = "homeassistant/sensor/vm-speichertemperatur"
payload6 = {"unique_id": "vm-speichertemperatur",
               "device_class": "temperature",
               "name": "Speichertemperatur",
               "state_topic": "homeassistant/sensor/vm-speichertemperatur/state",
               "unit_of_measurement": "°C",
               "icon": "mdi:heat-wave",
               "value_template": "{{ value_json.temperature }}" }
topic7 = "homeassistant/sensor/vm-brennerstatus"
payload7 = {"unique_id": "vm-brennerstatus",
               "name": "Brennerstatus",
               "state_topic": "homeassistant/sensor/vm-brennerstatus/state",
               "icon": "mdi:state-machine",
               "value_template": "{{ value_json.state }}" }
topic8 = "homeassistant/sensor/vm-datum_uhrzeit"
payload8 = {"unique_id": "vm-datum_uhrzeit",
               "name": "Systemzeit",
               "state_topic": "homeassistant/sensor/vm-datum_uhrzeit/state",
               "icon": "mdi:home-clock",
               "value_template": "{{ value_json.clock }}" }

def twos_complement(hexstr):

    bits = 16

    value = int(hexstr,bits)
    if value & (1 << (bits-1)):
        value -= 1 << bits
    return value

# ----------------------------------------------------------------------

# callback for CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

# callback for received messages
def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))

def on_disconnect(client, userdata, flags, rc):
    print("Diconnected with result code "+str(rc))

# ----------------------------------------------------------------------

mqc=mqtt.Client()
mqc.username_pw_set(username=MQTT_USER,password=MQTT_PASSWORD)
mqc.on_connect=on_connect
mqc.on_disconnect=on_disconnect
mqc.on_message=on_message

mqc.disconnected =True
mqc.connect(MQTT_SERVER,1883,60)

mqc.loop_start()

# init command
command = b'\x04'

# this commands we want to send
cmd=[
    #b'\xF7\x00\xF8\x02',   #Typ
    b'\xF7\x08\x02\x02',    # Kessel Temperatur
    b'\xF7\x08\x04\x02',    # Speicher Temperatur
    b'\xF7\x08\x00\x02',    # Aussentemperatur
    b'\xF7\x08\x8A\x04',    # Brennerstarts
    b'\xF7\x08\x8E\x08',    # Systemzeit
    #b'\xF7\x23\x00\x01',    # Frostschutz
    #b'\xF7\x23\x01\x01',    # Betriebsart
    #b'\xF7\x23\x02\x01',    # Sparbetrieb
    #b'\xF7\x23\x03\x01',    # Partybetrieb
    #b'\xF7\x23\x06\x01',    # Solltemperatur
    b'\xF7\x29\x06\x01',    # Pumpe Heizung
    b'\xF7\x08\x45\x01',    # Pumpe Speicher
    b'\xF7\x55\x1E\x01',    # Brennerstatus
    b'\xF7\x75\x79\x01'     # Fehlercode
    ]    

# counter
cnt = 0;

try:

    # serial settings
    ser = serial.Serial (
            port='/dev/ttyUSB0',
            #port='COM5',
            baudrate=4800,
            parity=serial.PARITY_EVEN,
            stopbits=serial.STOPBITS_TWO,
            bytesize=serial.EIGHTBITS,
            #timeout = None
            timeout=0.02
        )

    i = 0

    while True:

        # convert to hex string
        try:
            data = ser.readline().hex()
        except:
            data = []
            
        if(len(data) > 0):

            i = i + 1
            #print(str(i) + " " + data)

            if(len(data) == 2):
                if('05' in data):
                    #request from heating
                    pass
                else:
                    if(command.hex().startswith('f72300')):
                        if(data.startswith('01')):
                           print('Frostschutzwarnung: AN')
                        else:
                           print('Frostschutzwarnung: AUS')
                    elif(command.hex().startswith('f72301')):
                        if(data.startswith('00')):
                            print('Betriebsart: WW')
                        elif(data.startswith('03')):
                            print('Betriebsart: H+WW')
                        elif(data.startswith('05')):
                            print('Betriebsart: Abschaltbetrieb')
                        else:
                            print('Betriebsart: ' + str(data))
                    elif(command.hex().startswith('f72302')):
                        if(data.startswith('01')):
                           print('Sparbetrieb: AN')
                        else:
                           print('Sparbetrieb: AUS')
                    elif(command.hex().startswith('f72303')):
                        if(data.startswith('01')):
                           print('Partybetrieb: AN')
                        else:
                           print('Partybetrieb: AUS')
                    elif(command.hex().startswith('f72306')):
                       print('Soll Temperatur: ' + str(int(data,16)))
                    elif(command.hex().startswith('f72906')):
                        
                       topic = topic4 + '/config'
                       dataW = payload4
                       mqc.publish(topic, json.dumps(dataW))

                       topic = topic4 + '/state'

                       if(data.startswith('01')):
                           print('Pumpe A1M1: AN')
                           dataW = { 'pump':    'ON'}
                           mqc.publish(topic, json.dumps(dataW))
                       else:
                           print('Pumpe A1M1: AUS')
                           dataW = { 'pump':    'OFF'}
                           mqc.publish(topic, json.dumps(dataW))
                           
                    elif(command.hex().startswith('f70845')):
                           
                       topic = topic5 + '/config'
                       dataW = payload5
                       mqc.publish(topic, json.dumps(dataW))

                       topic = topic5 + '/state'

                       if(data.startswith('01')):
                           print('Pumpe Speicher: AN')
                           dataW = { 'pump':    'ON'}
                           mqc.publish(topic, json.dumps(dataW))
                       else:
                           print('Pumpe Speicher: AUS')
                           dataW = { 'pump':    'OFF'}
                           mqc.publish(topic, json.dumps(dataW))
 
                    elif(command.hex().startswith('f7551e')):
                        
                       topic = topic7 + '/config'
                       dataW = payload7
                       mqc.publish(topic, json.dumps(dataW))

                       topic = topic7 + '/state'
                       dataW = { 'state':    '??'}
                       
                       if(data.startswith('00')):
                           print('Brenner: AUS')
                           dataW = { 'state':    'AUS'}
                       elif (data.startswith('01')):
                           print('Brenner: Stufe 1')
                           dataW = { 'state':    'Stufe 1'}
                       elif(data.startswith('02')):
                           print('Brenner: Stufe2')
                           dataW = { 'state':    'Stufe 2'}
                       mqc.publish(topic, json.dumps(dataW))
                    elif(command.hex().startswith('f77579')):
                       print('Störung: ' + str(data))

            if(len(data) == 4):
               hex_str = data[2:] + data[:2]

               #res = int(hex_str,16) /10
               res = twos_complement(hex_str) / 10

               if(command.hex().startswith('f7')):
                   if(command.hex().startswith('f700f8')):
                       print ("------------------------")
                       print ('Typ: ' + data + ' (V200KW1) ')
                   elif(command.hex().startswith('f70802')):
                       print('Kessel: ' + str(res))
                       
                       topic = topic1 + '/config'
                       data = payload1
                       mqc.publish(topic, json.dumps(data))

                       topic = topic1 + '/state'
                       data = { 'temperature': str(res) }
                       mqc.publish(topic, json.dumps(data))               
                       
                   elif(command.hex().startswith('f70804')):
                       print('Speicher: ' + str(res))
                       
                       topic = topic6 + '/config'
                       data = payload6
                       mqc.publish(topic, json.dumps(data))

                       topic = topic6 + '/state'
                       data = { 'temperature': str(res) }
                       mqc.publish(topic, json.dumps(data))
                   elif(command.hex().startswith('f70800')):
                       print('Aussentemperatur: ' + str(res))
                       
                       topic = topic2 + '/config'
                       data = payload2
                       mqc.publish(topic, json.dumps(data))

                       topic = topic2 + '/state'
                       data = { 'temperature': str(res) }
                       mqc.publish(topic, json.dumps(data)) 
                   else:
                       print(str(i) + " " + data)
            if(len(data) == 8):
                hex_str = data[6:] + data[4:6] + data[2:4] + data[0:2]
                
                if(command.hex().startswith('f7088a')):
                   print('Brennerstarts: ' + str(int(hex_str,16)))
                       
                   topic = topic3 + '/config'
                   data = payload3
                   mqc.publish(topic, json.dumps(data))

                   topic = topic3 + '/state'
                   data = { 'counter': str(int(hex_str,16)) }
                   mqc.publish(topic, json.dumps(data)) 
                
            if(len(data) == 16):
                
                dateTime = data[6:8] + '.' + data[4:6] + '.' + data[0:4] + ' ' + data[10:12] + ':' + data[12:14]
                
                print('Datum/Zeit: ' + dateTime)
                
                topic = topic8 + '/config'
                dataW = payload8
                mqc.publish(topic, json.dumps(dataW))

                topic = topic8 + '/state'
                
                dataW = { 'clock':    dateTime }
                mqc.publish(topic, json.dumps(dataW))

            if ('05' in data) and (len(data) == 2):

                # send ACK
                command = b'\x01' #ACK
                ser.write(command)

                # next command to send
                cnt = cnt + 1
                if cnt == len(cmd):
                    cnt = 0

                # send command
                command = cmd[cnt]
                ser.write(command)
                #print("Send " + command.hex())

except:
    print(traceback.format_exc())
    print ("Exception - exit")

print ("end")
