# -*- coding: cp1252 -*-
import FileDialog
import serial
import time
import sys
sys.path.append("/cc2500_testtool")
import random
import numpy as np
import matplotlib.pyplot as plt
import Tkinter as tk
from PIL import Image, ImageTk
import datetime
from datetime import date
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import tkFileDialog as tk_file
import tkSimpleDialog
import tkMessageBox


"""
Message structure for CC2500 is as follows:
first 3 bytes are allways the beacon:

0x21
0x23
0x21

Then comes message type in 1 byte
next two bytes are message length (bytes(
then comes message (x bytes)
CRC check sum 2 bytes

"""

class MainWindow(object):
    def __init__(self,master):
        #create some frame
        self.root=master
        #self.datarate=1000000
        self.packet_errors=0
        self.lost_packets=0
        self.packets=200
        self.mainframe=tk.Frame(master)
        self.mainframe.grid(row=0,column=0)
        #self.root.iconbitmap('favicon.ico')
        self.root.geometry("%dx%d%+d%+d" % (800, 450, 20, 20))
        """
        self.left_column=tk.Frame(self.mainframe,width=400,height=450,bd=1,relief=tk.GROOVE)
        self.left_column.grid(row=0,column=0,pady=5)
        self.left_column.grid_propagate(False)

        self.right_column=tk.Frame(self.mainframe,width=400,height=450,bd=1,relief=tk.GROOVE)
        self.right_column.grid(row=0,column=1,pady=5)
        self.right_column.grid_propagate(False)
        """
        self.root.title("COM PORT TESTER")
        

        #COMPORT LIST FOR TX
        self.left_frame=tk.Frame(self.mainframe,width=150,height=100,bd=1,relief=tk.GROOVE) 
        self.left_frame.grid(row=0,column=0)
        #self.left_frame.grid_propagate(False)
        
        
        self.right_frame=tk.Frame(self.mainframe,width=150,height=100,bd=1,relief=tk.GROOVE)
        self.right_frame.grid(row=0,column=1)
        
        self.info_frame=tk.Frame(self.mainframe,width=150,height=300,bd=0,relief=tk.GROOVE)
        self.info_frame.grid(row=0,column=2)
        #self.right_frame.grid_propagate(False)
        
        #Some test buttons
        
        self.button1=tk.Button(self.right_frame,text="CONFIGURE MODULE",command=self.config_module)
        self.button1.grid(row=0,column=0,pady=5,padx=5)
        
        
        
        
        

        ports=self.serial_ports() #gets a list of com ports available
        print(len(ports))
        print("Awailable ports:%s"%ports)
        
        #headlines for com list
        self.left_COM_list_label=tk.Label(self.left_frame,text="available ports")
        self.left_COM_list_label.grid(row=0,column=0)
        
        
        
        #list awailable comports and insert them into the listbox TX
        self.TX_comlist=tk.Listbox(self.left_frame)
        for n in range (0,len(ports)):
            self.TX_comlist.insert(n,ports[n])
        self.TX_comlist.grid(row=1,column=0)
        self.TX_comlist.bind('<<ListboxSelect>>', self.on_tx_com_select)        
        
    
    def config_module(self):
         name=tkSimpleDialog.askstring("Bluetooth friendly name","What name is given to module",parent=self.mainframe) #ask friendly name for Bluetooth
         
        
         #configure module
         print("reset module to factory defaults")
         self.ser_tx.write("AT&F*\r")
         time.sleep(0.5)
         self.read_and_print()
         self.ser_tx.reset_input_buffer()
         #close port for power recycle
         self.ser_tx.close()
         time.sleep(0.5)
         #power cycle ask
         tkMessageBox.showinfo("Power cycle !","Power cycle module")
         self.ser_tx.open()
         time.sleep(0.5)
         
         #change other settings
         print("Echo disable")
         self.ser_tx.write("ATs506=0\r")
         time.sleep(0.5)
         self.read_and_print()
         
         #change latency setting
         
         print("Set latency setting")
         self.ser_tx.write("ATs9084=3\r")
         time.sleep(0.5)
         self.read_and_print()
         
         print("Disable debug messages")
         self.ser_tx.write("ATs504=1\r")
         time.sleep(0.5)
         self.read_and_print()
         
         print("Change bluetooth name")
         self.ser_tx.write("AT+BTN=\"%s\"\r"%name)
         time.sleep(0.5)
         self.read_and_print()
         
         #change pin code to 1234
         
         print("Change PIN code to 1234")
         self.ser_tx.write("AT+BTK=\"1234\"\r")
         time.sleep(0.5)
         self.read_and_print()
         
         #change baudrate
         print("set baudrate")
         self.ser_tx.write("ATs9240=115200\r")
         time.sleep(0.5)
         self.read_and_print()
         
         #store settings
         
         print("store settings")
         self.ser_tx.write("AT&W\r")
         time.sleep(1)
         self.read_and_print()
         
         self.ser_tx.close()
         time.sleep(1)
         
         tkMessageBox.showinfo("Power cycle !","Power cycle module")
         print("Checking that it works")
         self.datarate=115200
         self.ser_tx=serial.Serial(self.portname,self.datarate, timeout=0) #serial port open
         time.sleep(1)
         self.ser_tx.write("AT\r")
         time.sleep(1)
         self.read_and_print()
         self.ser_tx.close()
         time.sleep(1)
         #echo out
         
         
         
         
         
         
         
         
         #power
        
    def read_and_print(self): #reads and prints serial port
    
        n=self.ser_tx.in_waiting
        print("Bytes waiting:%d"%n)
        txt=self.ser_tx.read(n)
        print(txt)
        
    
    def set_packets(self):
        self.packets=tkSimpleDialog.askinteger("Packets","How many packets ?",parent=self.mainframe)
        
    def set_packet_size(self):
        self.packet_size=tkSimpleDialog.askinteger("Packets","Size of packet (bytes) ?",parent=self.mainframe)
        a="a"
        self.payload=self.packet_size*a

    def on_tx_com_select(self,a):
        self.datarate=tkSimpleDialog.askinteger("Baud rate","What baudrate?",parent=self.mainframe)
        self.datarate=9600
        a=self.TX_comlist.curselection()
        text=self.TX_comlist.get(a)
        self.portname=text
        self.ser_tx=serial.Serial(text,self.datarate, timeout=0) #serial port open
        self.ser_tx.reset_input_buffer()
    

    def serial_ports(self):
        """ Lists serial port names

            :raises EnvironmentError:
                On unsupported or unknown platforms
            :returns:
                A list of the serial ports available on the system
        """
        if sys.platform.startswith('win'):
            ports = ['COM%s' % (i + 1) for i in range(256)]
        elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
            # this excludes your current terminal "/dev/tty"
            ports = glob.glob('/dev/tty[A-Za-z]*')
        elif sys.platform.startswith('darwin'):
            ports = glob.glob('/dev/tty.*')
        else:
            raise EnvironmentError('Unsupported platform')

        result = []
        for port in ports:
            try:
                s = serial.Serial(port)
                s.close()
                result.append(port)
            except (OSError, serial.SerialException):
                pass
        return result

    def on_select(self,a):
        a=self.listbox.curselection()
        if (a==(0,)):
            print("setting modem to 500kbps")
            self.set_master_500kbps(self.ser2)

        if (a==(1,)):
            print("setting modem to 25kbps")
            self.set_master_250kbps(self.ser2)

        if (a==(2,)):
            print("setting modem to 100kbps")
            self.set_master_100kbps(self.ser2)

        if (a==(3,)):
            print("setting modem to 50kbps")
            self.set_master_50kbps(self.ser2)

#############################
##TX To RX
            
    def test_TX_RX(self):#send n times 50bytes packet and log latency
        latencies=[]
        self.lost_packets=0
        self.packet_errors=0
        packets=self.packets
        self.received_bytes=0
        self.start_time=time.time()
        for n in range (0,packets):
            #empty buffers
            self.ser_tx.reset_input_buffer()
            self.ser_rx.reset_input_buffer()
            
            self.send_something()
            if (self.delay!=None):
                latencies.append(self.delay) #delay from latest packet
        self.stop_time=time.time()
        self.total_time=self.stop_time-self.start_time
        print("Bytes %d"%self.received_bytes)
        print("Time: %.2f"%self.total_time)
        bit_rate=(8*self.received_bytes/self.total_time)/1000
        print("Bit rate:%.2f"%bit_rate)
        self.speed_label.config(text="%.2f kbps"%bit_rate)
        latencies=np.asarray(latencies)
        #convert to ms
        latencies=latencies*1000
        #print(latencies)
        print("Packet errors:%d"%self.packet_errors)
        self.lost_label.config(text="LOST PACKETS:%d"%self.lost_packets)
        self.error_label.config(text="BAD PACKETS:%d"%self.packet_errors)
        #n, bins, patches = plt.hist(latencies, 50, density=True, facecolor='g', alpha=0.75)
        plt.hist(latencies)
        plt.xlabel('latency (ms)')
        plt.ylabel('Packets')
        #text="Errors:%d"%self.packet_errors
        #x_coord=15
        #y_coord=50
        #plt.text(x_coord,y_coord,text)
        #plt.plot(latencies)
        plt.show()
            
    
    def send_something(self):
        
        a=self.payload
        self.packet_length=len(a)
        self.tx_timestamp=time.time()
        self.ser_tx.write(a)
        self.read_something()
        
    
   
    
    def read_something(self):#read something from rx
        timer=100000 #amount of trials
        index=0
        l=self.packet_length
        while(1):
            if (self.ser_rx.in_waiting>=l):
                a=self.ser_rx.read(l)
                rx_timestamp=time.time()
                if(a==self.payload):
                    #print("Success")
                    self.delay=rx_timestamp-self.tx_timestamp
                    self.received_bytes=self.received_bytes+len(a)
                    break
                else:
                    self.packet_errors=self.packet_errors+1
                    self.delay=None
            index=index+1
            if (index>timer):#timeout
                self.lost_packets=self.lost_packets+1
                print("No receive")
                self.delay=None
                break
        
########################################

#############################
##RX To TX
            
    def test_RX_TX(self):#send n times 50bytes packet and log latency
        latencies=[]
        self.lost_packets=0
        self.packet_errors=0
        packets=self.packets
        self.received_bytes=0
        self.start_time=time.time()
        for n in range (0,packets):
            #empty buffers
            self.ser_tx.reset_input_buffer()
            self.ser_rx.reset_input_buffer()
            self.send_something_RXTX()
            if (self.delay!=None):
                latencies.append(self.delay) #delay from latest packet
        self.stop_time=time.time()
        self.total_time=self.stop_time-self.start_time
        print("Bytes %d"%self.received_bytes)
        print("Time: %.2f"%self.total_time)
        bit_rate=(8*self.received_bytes/self.total_time)/1000
        print("Bit rate:%.2f"%bit_rate)
        self.speed_label.config(text="%.2f kbps"%bit_rate)    
        latencies=np.asarray(latencies)
        #convert to ms
        latencies=latencies*1000
        #print(latencies)
        self.lost_label.config(text="LOST PACKETS:%d"%self.lost_packets)
        self.error_label.config(text="BAD PACKETS:%d"%self.packet_errors)
        print("Packet errors:%d"%self.packet_errors)
        print("Lost packets:%d"%self.lost_packets)
        #n, bins, patches = plt.hist(latencies, 50, density=True, facecolor='g', alpha=0.75)
        plt.hist(latencies)
        plt.xlabel('latency (ms)')
        plt.ylabel('Packets')
        #text="Errors:%d"%self.packet_errors
        #x_coord=15
        #y_coord=50
        #plt.text(x_coord,y_coord,text)
        #plt.plot(latencies)
        plt.show()
            
    
    def send_something_RXTX(self):
        a="asdlkjfa aösldkjfaölskdjföals 2093840293 akasdifuasd0 asodifjas9 öaoisduföalskd aösldkjfaösd89 aoösidfjalöksd öalsidf9089234 aöokjdfp098akls"
        a=self.payload
        self.packet_length=len(a)
        self.tx_timestamp=time.time()
        self.ser_rx.write(a)
        self.read_something_RXTX()
        
    
   
    
    def read_something_RXTX(self):#read something from rx
        timer=100000 #amount of trials
        index=0
        l=self.packet_length
        while(1):
            if (self.ser_tx.in_waiting>=l):
                a=self.ser_tx.read(l)
                rx_timestamp=time.time()
                if(a==self.payload):
                    #print("Success")
                    self.delay=rx_timestamp-self.tx_timestamp
                    self.received_bytes=self.received_bytes+len(a)
                    break
                else:
                    self.packet_errors=self.packet_errors+1
                    self.delay=None
            index=index+1
            if (index>timer):#timeout
                self.lost_packets=self.lost_packets+1
                print("No receive")
                self.delay=None
                break
    
########################################
   

def on_closing():
    print("byebye")
    try:
        app.ser_tx.close()
        app.ser_rx.close()
        root.destroy()
    except:
        root.destroy()
        


if __name__ == "__main__":
    root = tk.Tk()
    #root.iconbitmap(default='inband_icon.ico')
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.geometry("800x600")
    app = MainWindow(root)
    root.mainloop()


"""
#foo()
#ser1 = serial.Serial('COM14', 500000, timeout=0)
#ser2 = serial.Serial('COM15', 500000, timeout=0)
#ser1.reset_input_buffer()
#ser2.reset_input_buffer()
#time.sleep(0.1)
#set_master()
#time.sleep(0.1)
#send 10 one byte packages
for x in range (0,10):
    send_dummy_package()
    time.sleep(0.1)
    

#get_HF_stats() #ask for HF stats
#time.sleep(0.1)
#read_something()
#ser2.close()
"""
