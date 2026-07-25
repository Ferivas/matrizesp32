import machine
from machine import Pin,SPI


#Declaracion de pines y constantes
LEDPIN=5
led=Pin(LEDPIN,Pin.OUT)

LEDBUG=18
ledbug=Pin(LEDBUG,Pin.OUT)

NUMMATRIZ=1
LONGBUF=NUMMATRIZ*8
datocero=0b00000000
buffram=[]
for i in range(LONGBUF+1):
    buffram.append(datocero)

oe = 27
oePin = machine.Pin(oe, machine.Pin.OUT)
#Config HW
data = 26;    # pin connected to the serial input of the MAX7219 (DIN)
load = 33;    # pin for loading data (CS)
clk  = 25;    # pin for the clock of the serial link (CLK)
miso=15 #notused
# Initialize the pins as outputs
dataPin = machine.Pin(data, machine.Pin.OUT)
loadPin = machine.Pin(load, machine.Pin.OUT)
clkPin  = machine.Pin(clk, machine.Pin.OUT)
misoPin = machine.Pin(miso, machine.Pin.OUT)
# Set them to level 0
dataPin.off()
loadPin.off()
clkPin.off()

spi = machine.SPI(-1, sck = clkPin, mosi = dataPin, miso = misoPin)

columnas=[0b00000001,0b00000010,0b00000100,0b00001000,0b00010000,0b00100000,0b01000000,0b10000000]
tblposdig=[1,10,19,27,25,31]
coldata = bytearray(columnas)
datocolumna=bytearray(1)
ptrcol=0
def handleInterrupt(timer):
    global interruptCounter
    global datocolumna
    global ptrcol
    global datodat
    interruptCounter = False
    oePin.on()
    datocolumna=coldata[ptrcol]
    datodat=buffram[ptrcol]
    ptrcol=ptrcol+1
    ptrcol=ptrcol%8
    serialWrite(datocolumna,datocero)
    serialWrite(datocolumna,datodat)
    oePin.off() 
    interruptCounter=True

interruptCounter = False
#totalInterruptsCounter = 0
timer = machine.Timer(1)
timer.init(period=2, mode=machine.Timer.PERIODIC, callback=handleInterrupt) #Ints cada 2 ms
tled=0
 
# Send a byte bit by bit to the MAX7219, most significant bit first
def serialShiftByte(data):
    # Set the clock to 0 in order to be able to make a rising edge later
    clkPin.off()
    # Shift the 8 bits of data
    spi.write(data)
# Write some data in a register of the MAX7219.
buffer = bytearray(2)
def serialWrite(address, data):
    # Set CS to 0 to create a rising edge later
    buffer[0] = address
    buffer[1] = data    
    loadPin.off()
    # Send the address of the register first
    spi.write(buffer)
    # then the data
    # make a rising edge on CS to load the transmitted data into the register
    loadPin.on()
    loadPin.off()
# Send a byte bit by bit to the MAX7219, most significant bit first

def gendig(valdig,posdig):
    ptrdig=valdig*6
    ptrpos=tblposdig[posdig]
    #print("Ptrpos>",ptrpos)
    for i in range(6):
        ptr=ptrdig+i
        #print("ptr>",ptr)
        datadig=TBLDIG[ptr]
        ptr2=ptrpos+i-1
        buffram[ptr2]=datadig
        #print("ptr2>",ptr2)
    

TBLDIG=[0B01111110,
0B11111111,
0B10000001,
0B10000001,
0B11111111,
0B01111110,
0B00000000,
0B00000001,
0B11111111,
0B11111111,
0B01000001,
0B00100000,
0B01100001,
0B11110001,
0B10010001,
0B10010001,
0B10011111,
0B10001111,
0B01101110,
0B11111111,
0B10010001,
0B10010001,
0B10010001,
0B10000001,
0B11111111,
0B11111111,
0B00001000,
0B00001000,
0B11111000,
0B11110000,
0B10001110,
0B10011111,
0B10010001,
0B10010001,
0B11110001,
0B11110001,
0B00001110,
0B10011111,
0B10010001,
0B10010001,
0B11111111,
0B01111110,
0B11000000,
0B11100000,
0B10110000,
0B10011000,
0B10001111,
0B10000111,
0B01101110,
0B11111111,
0B10010001,
0B10010001,
0B11111111,
0B01101110,
0B01111110,
0B11111111,
0B10010001,
0B10010001,
0B11110001,
0B01100000,
0B00000000,
0B00000000,
0B00000000,
0B00000000,
0B00000000,
0B00000000,
]

print("uPython Matrix")
ptrcol=0
datocero=0b00000000
datodat=0b001000100
print("Gen1")
gendig(4,0)
tick=0
newdig=False
cntrdig=0
while True:
  if interruptCounter:
    interruptCounter = False
    tled=tled+1
    tled=tled%1600
    if tled <100:
      led.value(1)
    else:
      led.value(0)
    tick=tick+1
    tick=tick%1000
    if tick==0:
        newdig=True
  if newdig:
      newdig=False
      print("C>",cntrdig)
      #tmpdig=10-cntrdig
      gendig(cntrdig,0)
      cntrdig=cntrdig+1
      cntrdig=cntrdig%10
print("FIN tst Timer")      


