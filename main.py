#!/usr/bin/env python3
import threading
import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
import telnetlib
import time
import re
from threading import *
import socket
from datetime import datetime

kivy.require('2.0.0')
class MyRoot(BoxLayout):
    def __init__(self):
        super(MyRoot, self).__init__()
        self.volumeSlider.bind(value=self.change_volume)
    
    def connect(self):
        tn.close()
        hostname = self.txtbox_input.text.split()
        if len(hostname) == 2:
            ip = hostname[0]
            port = hostname[1]
        elif len(hostname) == 1:
            ip = hostname[0]
            port = 23
        else:
            ip = "192.168.0.117"
            port = 69
        try:
            tn.open(ip, port)
            
        except:
            self.add_text("Unable to connect\nTelnet server: " + ip + " Port: " + str(port))
            return
        tn.set_debuglevel(1000)
        self.add_text("Connected to " + ip + " Port: " + str(port))

    def add_text(self, text):
        if len(self.outputLabel.text) > 1000:
            self.outputLabel.text = ""
        self.outputLabel.text += "{}\n".format(text)
        self.outputLabel.scroll_y = 0

    def send_command(self):
        usrmsg = self.txtInput_Command.text
        try:
            tn.write((""+ usrmsg + "\r").encode('utf-8'))
            time.sleep(.1)
            result = tn.read_eager().decode("utf-8")
            self.add_text(result)
        except:
            self.add_text("Unable to send command.\nTry connecting again.")

    def change_volume(self, instance, value):
        #volume = int(self.volumeSlider.value)
        
        volume = int(value)
        if volume < 100 and volume > 9:
            volume = str("0" + str(volume))
        elif volume < 10:
            volume = str("00" + str(volume))
        else:
            volume = str(volume)
        try:
            tn.write("{}vl\r".format(volume).encode('utf-8'))
            result = tn.read_eager().decode("utf-8")
            self.add_text("" + result + "\nVolume set at {}".format(volume))
        except:
            self.add_text("Unable to send volume command.\nAre you connected?")

    

    def change_input(self, instance):
        command = selection[instance.text]
        try:
            tn.write("{}fn\r".format(command).encode('utf-8'))
            result = tn.read_eager().decode("utf-8")
            self.add_text("" + result + "\nInput selected: {}".format(instance.text))
        except:
            self.add_text("Unable to send input command.\nAre you connected?")

    def toggle_mute(self, instance):
        self.print_output()
        try:
            if instance.state == "down":
                tn.write("mo\r".encode('utf-8'))
                self.add_text("Mute on")
            else:
                tn.write("mf\r".encode('utf-8'))
                self.add_text("Mute off")
        except:
            self.add_text("Unable to send Mute command.")
        
    def toggle_power(self, instance):
        self.print_output()
        try:
            if instance.state == "down":
                tn.write("po\r".encode('utf-8'))
                self.add_text("Power on")
            else:
                tn.write("pf\r".encode('utf-8'))
                self.add_text("Power off")
        except:
            self.add_text("Unable to send Power command.")
        
    
    def print_output(self):
        result = tn.read_eager().decode("utf-8")
        self.add_text(result)

    def get_power_state(self):
        try:
            tn.write("?p\r".encode('utf-8'))
            time.sleep(.1)
            result = tn.read_eager().decode('utf-8').strip()
            if result == "PWR0":
                return "down"
            elif result == "PWR1":
                return "normal"
        except:
            return "normal"
    def get_mute_state(self):
        try:
            tn.write("?m\r".encode('utf-8'))
            time.sleep(.1)
            result = tn.read_eager().decode('utf-8').strip()
            if "MUT0" in result :
                return "down"
            elif "MUT1" in result:
                return "normal"
        except:
            return "normal"        
    def get_volume_level(self):
        try:
            tn.write("?v\r".encode('utf-8'))
            time.sleep(.1)
            result = tn.read_eager().decode('utf-8').strip()
            volume = re.search(r"(\d{3})", result)
            return volume[1]
        except:
            return "0"
    def get_input_source(self, instance):
        label = instance.text
        try:
            tn.write("?f\r".encode('utf-8'))
            time.sleep(.1)
            result = tn.read_eager().decode('utf-8').strip()
            source = re.search(r"(\d{2})", result)
            for k, v in selection.items():
                if v in source[1]:
                    if k in label:
                        return "down"
            return "normal"
        except:
            return "normal"

class PioneerRemote(App):
    def build(self):
        return MyRoot()

def scan():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))

    ipv4, poooort = s.getsockname()
    network = ipv4.split(".")
    prefix = "{}.{}.{}.".format(network[0], network[1], network[2])
    target = socket.gethostbyname("{}0".format(prefix))


    print("-" * 50)
    print("Scanning network: {}".format(target))
    print("Scanning started at: {}".format(str(datetime.now())))
    print("-" * 50)


    try:
        for address in range(0, 255):
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            socket.setdefaulttimeout(.01)

            result = s.connect_ex((prefix + str(address), 8102))
            if result == 0:
                print("\nAddress {} is open".format(address))
                return prefix + str(address)
            s.close()
            
        
    except KeyboardInterrupt:
        print("\nExiting program")
    except socket.gaierror:
        print("\nHostname could not be resolved")
    except socket.error:
        print("\nserver not responding")

ip = scan()
tn = telnetlib.Telnet()
connected = False
def connection():
    global connected
    global ip
    if connected:
        try:
            tn.write("\r".encode('utf-8'))
            print("Connection is alive")
        except:
            connected = False
            print("Connection has failed")
    else:
        try:
            tn.open(ip, 8102)
            connected = True
            print("Connected to {} port 8102".format(ip))
        except:
            connected = False
            print("Connection has failed")
    threading.Timer(30, connection).start()

T1 = Thread(target=connection)
T1.daemon = True
T1.start()
time.sleep(.1)
selection = {"Chromecast":"04", "Bluetooth":"33","PC":"06","Spotify":"53","TV":"01", "PS4":"05"}
pioneerRemote = PioneerRemote()
pioneerRemote.run()