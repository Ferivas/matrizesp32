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

# Configuración del pin OE (Output Enable)
oe = 27
oePin = machine.Pin(oe, machine.Pin.OUT)
oePin.off() # Habilitado por defecto (bajo)

# Configuración PWM (se inicializará solo si DEMO_MODE==3)
pwm_oe = None

def set_brightness(duty):
    global pwm_oe
    # duty: 0 (min brillo) a 1023 (max brillo)
    if pwm_oe:
        # OE activo bajo, invertimos para que mayor duty signifique mas brillo
        pwm_oe.duty(1023 - duty)
    else:
        # Si no hay PWM, mantenemos encendido (low)
        oePin.off()

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
# Pre-allocate SPI buffers for each of the 8 columns
# Each buffer stores the 2 bytes required for a MAX7219 command (address, data)
spi_col_buffers = [bytearray(2) for _ in range(8)]

def update_spi_buffers():
    """Pre-calculates the SPI buffers for all columns."""
    for i in range(8):
        spi_col_buffers[i][0] = coldata[i]
        spi_col_buffers[i][1] = buffram[i]

# Inicializar buffers
update_spi_buffers()

def handleInterrupt(timer):
    global interruptCounter
    global ptrcol
    interruptCounter = False
    
    # 1. Apagar la matriz antes de actualizar (Blanking)
    if pwm_oe:
        # En modo PWM, poner duty a 1023 (LEDs OFF)
        pwm_oe.duty(1023)
    else:
        oePin.value(1) # Apagar digitalmente (OE activo bajo)
    
    # 2. Enviar comando de apagado a la columna anterior para limpiar residuos
    prev_col_addr = coldata[(ptrcol - 1) % 8]
    serialWrite(prev_col_addr, 0x00)
    
    # 3. Actualizar el dato para la columna actual
    spi_col_buffers[ptrcol][1] = buffram[ptrcol]
    
    # 4. Enviar datos de la nueva columna
    loadPin.off()
    spi.write(spi_col_buffers[ptrcol])
    loadPin.on()
    loadPin.off()
    
    # 5. Avanzar puntero
    ptrcol = (ptrcol + 1) % 8
    
    # 6. Encender la matriz
    if pwm_oe:
        # Restaurar el brillo PWM
        pwm_oe.duty(1023 - brightness)
    else:
        oePin.value(0) # Encender digitalmente
    
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

# --- CONFIGURACION DE ANIMACIONES & DEMOS ---
# 0: Demo original de digitos rotativos (0-9)
# 1: Demo de cuadrado de 2x2 pixeles moviéndose aleatoriamente (Caminata Aleatoria)
# 2: Demo de línea barredora (Fila que baja, se convierte en columna, se mueve a la derecha, etc.)
# 3: Demo de círculo pulsante con brillo variable (PWM en OE)
DEMO_MODE = 2

import urandom

# Configuración del pin OE (Output Enable)
oe = 27
oePin = machine.Pin(oe, machine.Pin.OUT)
oePin.off() # Habilitado por defecto

# Configuración PWM (se inicializará solo si DEMO_MODE==3)
pwm_oe = None

def set_brightness(duty):
    global pwm_oe
    # duty: 0 (min brillo) a 1023 (max brillo)
    if pwm_oe:
        # OE activo bajo, invertimos para que mayor duty signifique mas brillo
        pwm_oe.duty(1023 - duty)
    else:
        # Si no hay PWM, mantenemos encendido (low)
        oePin.off()

# Posicion inicial del cuadrado de 2x2 pixeles (DEMO_MODE = 1)
sq_x = 3
sq_y = 3

# Variables para la animacion de linea barredora (DEMO_MODE = 2)
# line_state -> 0: fila hacia abajo, 1: columna hacia la derecha, 2: fila hacia arriba, 3: columna hacia la izquierda
line_state = 0
line_pos = 0

# Variables para circulo pulsante (DEMO_MODE = 3)
brightness = 0
b_dir = 1

def clear_buffer():
    for i in range(8):
        buffram[i] = 0

def draw_square(x, y):
    clear_buffer()
    # Un cuadrado de 2x2 pixeles en (x, y) activa las filas y, y+1 en las columnas x, x+1
    mask = (1 << y) | (1 << (y + 1))
    buffram[x] = mask
    buffram[x+1] = mask

def move_square():
    global sq_x, sq_y
    # Obtenemos todos los movimientos posibles (8 vecinos + quedarse quieto si se desea,
    # pero preferimos movimiento constante para mayor dinamismo)
    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            new_x = sq_x + dx
            new_y = sq_y + dy
            # El cuadrado de 2x2 ocupa de x a x+1 y de y a y+1, por lo que las esquinas superiores
            # izquierdas validas estan en el rango [0, 6] en una matriz de 8x8.
            if 0 <= new_x <= 6 and 0 <= new_y <= 6:
                moves.append((new_x, new_y))
    if moves:
        idx = urandom.randint(0, len(moves) - 1)
        sq_x, sq_y = moves[idx]

def draw_line(state, pos):
    clear_buffer()
    if state == 0 or state == 2:  # Fila horizontal (todos los bits en la posicion 'pos' de cada columna)
        mask = 1 << pos
        for i in range(8):
            buffram[i] = mask
    elif state == 1 or state == 3:  # Columna vertical (todos los bits activos en la columna 'pos')
        buffram[pos] = 0xFF

def move_line():
    global line_state, line_pos
    if line_state == 0:  # Fila hacia abajo
        if line_pos < 7:
            line_pos += 1
        else:
            line_state = 1
            line_pos = 0
    elif line_state == 1:  # Columna hacia la derecha
        if line_pos < 7:
            line_pos += 1
        else:
            line_state = 2
            line_pos = 7
    elif line_state == 2:  # Fila hacia arriba
        if line_pos > 0:
            line_pos -= 1
        else:
            line_state = 3
            line_pos = 7
    elif line_state == 3:  # Columna hacia la izquierda
        if line_pos > 0:
            line_pos -= 1
        else:
            line_state = 0
            line_pos = 0

def draw_circle():
    clear_buffer()
    # Dibujo aproximado de circulo 8x8 en el centro
    buffram[2] = 0b00111100
    buffram[3] = 0b01111110
    buffram[4] = 0b01111110
    buffram[5] = 0b00111100

def update_brightness():
    global brightness, b_dir
    brightness += b_dir * 50
    if brightness >= 1023 or brightness <= 0:
        b_dir *= -1
        brightness = max(0, min(1023, brightness))
    set_brightness(brightness)

# Inicializacion de los demos
if DEMO_MODE == 0:
    print("Iniciando Demo de Digitos")
    gendig(4, 0)
elif DEMO_MODE == 1:
    print("Iniciando Demo de Cuadrado Movil")
    draw_square(sq_x, sq_y)
elif DEMO_MODE == 2:
    print("Iniciando Demo de Linea Barredora")
    draw_line(line_state, line_pos)
elif DEMO_MODE == 3:
    print("Iniciando Demo de Circulo Pulsante")
    # Inicializar PWM solo si es necesario (Aumentando frecuencia a 5000Hz)
    pwm_oe = machine.PWM(machine.Pin(oe), freq=5000)
    draw_circle()
    set_brightness(brightness)

tick=0
update_demo=False
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
    
    # Ajustamos la frecuencia de actualizacion de cada demo
    if DEMO_MODE == 0:
        # Los digitos cambian cada 1000 ticks (2000 ms = 2 segundos)
        tick=tick%1000
    elif DEMO_MODE == 1:
        # El cuadrado se mueve cada 100 ticks (200 ms) para una animacion fluida
        tick=tick%200
    elif DEMO_MODE == 2:
        # La linea se barre cada 75 ticks (150 ms) para un movimiento de velocidad media
        #tick=tick%75
        tick=tick%150
    elif DEMO_MODE == 3:
        # El brillo se actualiza cada 25 ticks (50 ms) para una pulsacion fluida
        tick=tick%25
        
    if tick==0:
        update_demo=True
        
  if update_demo:
      update_demo=False
      if DEMO_MODE == 0:
          print("C>",cntrdig)
          gendig(cntrdig,0)
          cntrdig=cntrdig+1
          cntrdig=cntrdig%10
      elif DEMO_MODE == 1:
          move_square()
          draw_square(sq_x, sq_y)
          print("Cuadrado pos: ({}, {})".format(sq_x, sq_y))
      elif DEMO_MODE == 2:
          move_line()
          draw_line(line_state, line_pos)
          print("Linea - Estado: {}, Pos: {}".format(line_state, line_pos))
      elif DEMO_MODE == 3:
          update_brightness()
          print("Brillo: {}".format(brightness))
print("FIN tst Timer")      


