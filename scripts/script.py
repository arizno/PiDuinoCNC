# -*- coding: utf-8 -*-

# Author : arizno
# 
# Date   : 02/14/2016

# Imports
import webiopi
import datetime
import time
from webiopi import deviceInstance
import sys
sys.path.append("/home/pi/WebIOPi-0.7.1/CNC/scripts")
import lcd

import os
# Initialize LCD display
lcd.__init__()

# Enable debug output
webiopi.setDebug()

# Retrieve GPIO lib
GPIO = webiopi.GPIO

BUTTON1 = 26
BUTTON2 = 19
BUTTON3 = 13
BUTTON4 = 6

# Temperature thresholds
COLD_shop = 69.9
HOT_shop = 79.0
COLD_gpu = 50
HOT_gpu = 100
COLD_cpu = 50
HOT_cpu = 90

# RGB LED GPIO's
RED = 11
GREEN = 9
BLUE = 10

# Switch GPIO
# Next version of WebIOPi should support interrupts (better approach)
SWITCH = 18

#set Colors
def red():
    GPIO.pwmWrite(RED, 0.0)
    GPIO.pwmWrite(GREEN, 1.0)
    GPIO.pwmWrite(BLUE, 1.0)

def blue():
    GPIO.pwmWrite(RED, 1.0)
    GPIO.pwmWrite(GREEN, 1.0)
    GPIO.pwmWrite(BLUE, 0.0)

def green():
    GPIO.pwmWrite(RED, 1.0)
    GPIO.pwmWrite(GREEN, 0.0)
    GPIO.pwmWrite(BLUE, 1.0)

def white():
    GPIO.pwmWrite(RED, 0.5)
    GPIO.pwmWrite(GREEN, 0.0)
    GPIO.pwmWrite(BLUE, 0.0)

#do CPU ad GPU temperature calculations
def get_cpu_temp():
    cTemp = os.popen('vcgencmd measure_temp').readline()
    rawC = cTemp.replace("temp=","").replace("'C\n","")
    rawC2 = float(rawC)
    return float(1.8*rawC2)+32
 
def get_gpu_temp():
    gTemp = os.popen("/opt/vc/bin/vcgencmd measure_temp").readline()
    rawG = gTemp.replace("temp=","").replace("'C\n","")
    rawG2 = float(rawG)
    return float(1.8*rawG2)+32

# Set temperature sensor (specified in WebIOPi config)
t = deviceInstance("Shop")

# Initialize temperature range variables
tShopLow = t.getFahrenheit()
tShopHigh = t.getFahrenheit()
tGpuHigh = float(get_gpu_temp())
tGpuLow = float(get_gpu_temp())
tCpuHigh = float(get_cpu_temp())
tCpuLow = float(get_cpu_temp())

# Called by WebIOPi at script loading
def setup():
    webiopi.debug("Script with macros - Setup")
    # Setup GPIOs
    GPIO.setFunction(RED, GPIO.PWM)
    GPIO.setFunction(GREEN, GPIO.PWM)
    GPIO.setFunction(BLUE, GPIO.PWM)
    GPIO.setup(SWITCH, GPIO.IN, pull_up_down=GPIO.PUD_UP)  
    # set the GPIO used by the Button #1
    GPIO.setFunction(BUTTON1, GPIO.OUT)
    GPIO.setFunction(BUTTON2, GPIO.OUT)
    GPIO.setFunction(BUTTON3, GPIO.OUT)
    GPIO.setFunction(BUTTON4, GPIO.OUT)

# Looped by WebIOPi
def loop():

    print ("GPIO 21 = ", GPIO.digitalRead(26) )
    print ("GPIO 24 = ", GPIO.digitalRead(19) )
    print ("GPIO 21 = ", GPIO.digitalRead(13) )
    print ("GPIO 24 = ", GPIO.digitalRead(6) )

    # Run every 3 seconds
    try:
        global tShopHigh
        global tShopLow
        global tGpuHigh
        global tGpuLow
        global tCpuHigh
        global tCpuLow

        # Get current Shop temperature
        fahrenheit = t.getFahrenheit()
        webiopi.debug("Shop: %0.1f°F" % fahrenheit)
        
    # Get GPU temperature
        GPUfahrenheit = float(get_gpu_temp())
        webiopi.debug("GPU Temp: %0.1f°F" % GPUfahrenheit)
        
        # Get CPU temperature
        CPUfahrenheit = float(get_cpu_temp())
        webiopi.debug("CPU Temp: %0.1f°F" % CPUfahrenheit)
        
        # Set high & low for GPU
        if GPUfahrenheit > tGpuHigh:
            tGpuHigh = GPUfahrenheit
        elif GPUfahrenheit < tGpuLow:
            tGpuLow = GPUfahrenheit
    
        if CPUfahrenheit > tCpuHigh:
            tCpuHigh = CPUfahrenheit
        elif CPUfahrenheit < tCpuLow:
            tCpuLow = CPUfahrenheit
        
        if fahrenheit > tShopHigh:
            tShopHigh = fahrenheit
        elif fahrenheit < tShopLow:
            tShopLow = fahrenheit
        webiopi.debug("GPU Low:     %0.1f°F" % tGpuLow)
        webiopi.debug("GPU High:    %0.1f°F" % tGpuHigh)
        webiopi.debug("CPU Low:     %0.1f°F" % tCpuLow)
        webiopi.debug("CPU High:    %0.1f°F" % tCpuHigh)
        webiopi.debug("Shop Low:     %0.1f°F" % tShopLow)
        webiopi.debug("Shop High:    %0.1f°F" % tShopHigh)

        # Temperature thresholds
        webiopi.debug("Shop Cold Threshold:    %0.1f°F" % COLD_shop)
        webiopi.debug("Shop Hot Threshold:     %0.1f°F" % HOT_shop)
        webiopi.debug("GPU Cold Threshold:    %0.1f°F" % COLD_gpu)
        webiopi.debug("GPU Hot Threshold:     %0.1f°F" % HOT_gpu)
        webiopi.debug("CPU Cold Threshold:    %0.1f°F" % COLD_cpu)
        webiopi.debug("CPU Hot Threshold:     %0.1f°F" % HOT_cpu)

        readouts = ['shopTemp', 'shopRange', 'GPUtemp', 'GPUrange', 'CPUtemp', 'CPUrange']
        for output in readouts:       
            if GPIO.digitalRead(SWITCH) == GPIO.LOW:
                # Reset switch pressed
                tShopHigh = fahrenheit
                tShopLow = fahrenheit
                tGpuHigh = GPUfahrenheit
                tGpuLow = GPUfahrenheit
                tCpuHigh = CPUfahrenheit
                tCpuLow = CPUfahrenheit
                # LCD background white
                GPIO.pwmWrite(RED, 0.0)
                GPIO.pwmWrite(GREEN, 0.6)
                GPIO.pwmWrite(BLUE, 0.8)
                lcd.lcd_byte(lcd.LCD_LINE_1, lcd.LCD_CMD)
                lcd.lcd_string("")
                lcd.lcd_byte(lcd.LCD_LINE_2, lcd.LCD_CMD)
                lcd.lcd_string("Temp Ranges Reset")

            elif output == 'shopTemp':
                # LCD background for Shop state
                if fahrenheit >= HOT_shop:
                    red()
                elif fahrenheit <= COLD_shop:
                    blue()
                else:
                    green()
                # Display Shop temp
                lcd.lcd_byte(lcd.LCD_LINE_1, lcd.LCD_CMD)
                lcd.lcd_string("Shop Temperature")
                lcd.lcd_byte(lcd.LCD_LINE_2, lcd.LCD_CMD)
                lcd.lcd_string("     %0.1f" % (fahrenheit)  + chr(223) + "F")

            elif output == 'shopRange':
                # LCD background for Shop range state
                if fahrenheit >= HOT_shop:
                    red()
                elif fahrenheit <= COLD_shop:
                    blue()
                else:
                    white()
                # Display Shop range
                lcd.lcd_byte(lcd.LCD_LINE_1, lcd.LCD_CMD)
                lcd.lcd_string("Shop Low: %0.1f" % (tShopLow)  + chr(223) + "F")
                lcd.lcd_byte(lcd.LCD_LINE_2, lcd.LCD_CMD)
                lcd.lcd_string("    High: %0.1f" % (tShopHigh)  + chr(223) + "F")

            elif output == 'GPUtemp':
                # LCD background for GPU state
                if GPUfahrenheit >= HOT_gpu:
                    red()
                elif GPUfahrenheit <= COLD_gpu:
                    blue()
                else:
                    green()
                # Display GPU temp
                lcd.lcd_byte(lcd.LCD_LINE_1, lcd.LCD_CMD)
                lcd.lcd_string("GPU Temperature")
                lcd.lcd_byte(lcd.LCD_LINE_2, lcd.LCD_CMD)
                lcd.lcd_string("    %0.1f" % (GPUfahrenheit)  + chr(223) + "F")

            elif output == 'GPUrange':
                # LCD background for Shop range state
                if GPUfahrenheit >= HOT_gpu:
                    red()
                elif GPUfahrenheit <= COLD_gpu:
                    blue()
                else:
                    white()
                # Display Shop range
                lcd.lcd_byte(lcd.LCD_LINE_1, lcd.LCD_CMD)
                lcd.lcd_string("GPU Low: %0.1f" % (tGpuLow)  + chr(223) + "F")
                lcd.lcd_byte(lcd.LCD_LINE_2, lcd.LCD_CMD)
                lcd.lcd_string("   High: %0.1f" % (tGpuHigh)  + chr(223) + "F")

            elif output == 'CPUtemp':
                # LCD background for Shop state
                if CPUfahrenheit >= HOT_cpu:
                    red()
                elif CPUfahrenheit <= COLD_cpu:
                    blue()
                else:
                    green()
                # Display CPU temp
                lcd.lcd_byte(lcd.LCD_LINE_1, lcd.LCD_CMD)
                lcd.lcd_string("CPU Temperature")
                lcd.lcd_byte(lcd.LCD_LINE_2, lcd.LCD_CMD)
                lcd.lcd_string("    %0.1f" % (CPUfahrenheit)  + chr(223) + "F")

            else:
                if output == 'CPUrange':
                # LCD background for CPU range state
                    if CPUfahrenheit >= HOT_cpu:
                        red()
                    elif CPUfahrenheit <= COLD_cpu:
                        blue()
                    else:
                        white()
                    # Display CPU range
                    lcd.lcd_byte(lcd.LCD_LINE_1, lcd.LCD_CMD)
                    lcd.lcd_string("CPU Low: %0.1f" % (tCpuLow)  + chr(223) + "F")
                    lcd.lcd_byte(lcd.LCD_LINE_2, lcd.LCD_CMD)
                    lcd.lcd_string("   High: %0.1f" % (tCpuHigh)  + chr(223) + "F")

            webiopi.sleep(1)

    except:     
        webiopi.debug("error: " + str(sys.exc_info()[0]))
        

# Called by WebIOPi at server shutdown
def destroy():
    webiopi.debug("Script with macros - Destroy")
    # Reset GPIO functions
    GPIO.setFunction(RED, GPIO.IN)
    GPIO.setFunction(GREEN, GPIO.IN)
    GPIO.setFunction(BLUE, GPIO.IN)
    GPIO.setFunction(SWITCH, GPIO.IN)
    GPIO.digitalWrite(BUTTON1, GPIO.LOW)
    GPIO.digitalWrite(BUTTON2, GPIO.LOW)
    GPIO.digitalWrite(BUTTON3, GPIO.LOW)
    GPIO.digitalWrite(BUTTON4, GPIO.LOW)

@webiopi.macro
def getGtemp():
    gTemp = os.popen("/opt/vc/bin/vcgencmd measure_temp").readline()
    rawG = gTemp.replace("temp=","").replace("'C\n","")
    rawG2 = float(rawG)
    return float(1.8*rawG2)+32

@webiopi.macro
def toggle_output1():
    val1 = not GPIO.digitalRead(BUTTON1)
    GPIO.digitalWrite(BUTTON1, val1)
    return val1

@webiopi.macro
def toggle_output2():
    val2 = not GPIO.digitalRead(BUTTON2)
    GPIO.digitalWrite(BUTTON2, val2)
    return val2

@webiopi.macro
def toggle_output3():
    val3 = not GPIO.digitalRead(BUTTON3)
    GPIO.digitalWrite(BUTTON3, val3)
    return val3

@webiopi.macro
def toggle_output4():
    val4 = not GPIO.digitalRead(BUTTON4)
    GPIO.digitalWrite(BUTTON4, val4)
    return val4

@webiopi.macro
def read_pin_states():
    btn1_output = GPIO.digitalRead(BUTTON1)
    btn2_output = GPIO.digitalRead(BUTTON2)  
    btn3_output = GPIO.digitalRead(BUTTON3)
    btn4_output = GPIO.digitalRead(BUTTON4)    
    return ("%s,%s,%s,%s" % (btn1_output,btn2_output,btn3_output,btn4_output))

# A macro to reset temperature range from web
@webiopi.macro
def ResetTempRange():
    webiopi.debug("Reset All Temp Range Macro...")
    global tShopHigh
    global tShopLo
    global tGpuHigh
    global tGpuLow
    global tCpuHigh
    global tCpuLow
    fahrenheit = t.getFahrenheit()
    GPUfahrenheit = float(get_gpu_temp())
    CPUfahrenheit = float(get_cpu_temp())
    tShopHigh = fahrenheit
    tShopLow = fahrenheit
    tGpuHigh = GPUfahrenheit
    tGpuLow = GPUfahrenheit
    tCpuHigh = CPUfahrenheit
    tCpuLow = CPUfahrenheit
    # LCD Background Cyan
    GPIO.pwmWrite(RED, 1.0)
    GPIO.pwmWrite(GREEN, 0.0)
    GPIO.pwmWrite(BLUE, 0.0)
    # Display current temperature on LCD display
    lcd.lcd_byte(lcd.LCD_LINE_1, lcd.LCD_CMD)
    lcd.lcd_string("Temp Ranges Reset")
    lcd.lcd_byte(lcd.LCD_LINE_2, lcd.LCD_CMD)
    lcd.lcd_string("( HTTP Request )")

# # A macro for Button #1 from web
# @webiopi.macro
# def Button1Macro():
#     webiopi.debug("Button 1 Macro running...")
#     # LCD Background Cyan
#     GPIO.pwmWrite(RED, 1.0)
#     GPIO.pwmWrite(GREEN, 0.0)
#     GPIO.pwmWrite(BLUE, 0.0)
#     # Display current temperature on LCD display
#     lcd.lcd_byte(lcd.LCD_LINE_1, lcd.LCD_CMD)
#     lcd.lcd_string("Button 1 Macro")
#     lcd.lcd_byte(lcd.LCD_LINE_2, lcd.LCD_CMD)
#     lcd.lcd_string("( HTTP Request )")

# # A macro for Button #2 from web
# @webiopi.macro
# def Button2Macro():
#     webiopi.debug("Button 2 Macro running...")
#     # LCD Background Cyan
#     GPIO.pwmWrite(RED, 1.0)
#     GPIO.pwmWrite(GREEN, 0.0)
#     GPIO.pwmWrite(BLUE, 0.0)
#     # Display current temperature on LCD display
#     lcd.lcd_byte(lcd.LCD_LINE_1, lcd.LCD_CMD)
#     lcd.lcd_string("Button 2 Macro")
#     lcd.lcd_byte(lcd.LCD_LINE_2, lcd.LCD_CMD)
#     lcd.lcd_string("( HTTP Request )")

# # A macro for Button #3 from web
# @webiopi.macro
# def Button3Macro():
#     webiopi.debug("Button 3 Macro running...")
#     # LCD Background Cyan
#     GPIO.pwmWrite(RED, 1.0)
#     GPIO.pwmWrite(GREEN, 0.0)
#     GPIO.pwmWrite(BLUE, 0.0)
#     # Display current temperature on LCD display
#     lcd.lcd_byte(lcd.LCD_LINE_1, lcd.LCD_CMD)
#     lcd.lcd_string("Button 3 Macro")
#     lcd.lcd_byte(lcd.LCD_LINE_2, lcd.LCD_CMD)
#     lcd.lcd_string("( HTTP Request )")

# # A macro for Button #4 from web
# @webiopi.macro
# def Button4Macro():
#     webiopi.debug("Button 4 Macro running...")
#     # LCD Background Cyan
#     GPIO.pwmWrite(RED, 1.0)
#     GPIO.pwmWrite(GREEN, 0.0)
#     GPIO.pwmWrite(BLUE, 0.0)
#     # Display current temperature on LCD display
#     lcd.lcd_byte(lcd.LCD_LINE_1, lcd.LCD_CMD)
#     lcd.lcd_string("Button 4 Macro")
#     lcd.lcd_byte(lcd.LCD_LINE_2, lcd.LCD_CMD)
#     lcd.lcd_string("( HTTP Request )")
    
# A macro to get the sensor Shop temperature from web
@webiopi.macro
def GetSensorTemp():
    webiopi.debug("GetSensorTemp Macro...")
    # Get current temperature
    fahrenheit = t.getFahrenheit()
    GPUfahrenheit = round(get_gpu_temp())
    CPUfahrenheit = round(get_cpu_temp())
    # LCD Background Purple
    GPIO.pwmWrite(RED, 0.0)
    GPIO.pwmWrite(GREEN, 1.0)
    GPIO.pwmWrite(BLUE, 0.0)
    
    # Display current temperature on LCD display
    lcd.lcd_byte(lcd.LCD_LINE_1, lcd.LCD_CMD)
    lcd.lcd_string("W: %0.1f" % (fahrenheit)  + chr(223) + "F" + "G: %0.1f" % (GPUfahrenheit)  + chr(223) + "F" + "W: %0.1f" % (CPUfahrenheit)  + chr(223) + "F")
    lcd.lcd_byte(lcd.LCD_LINE_2, lcd.LCD_CMD)
    lcd.lcd_string("( HTTP Request )")
    return "Shop:  %0.1f°F\r\nLow:      %0.1f°F\r\nHigh:     %0.1f°F\r\n'     ***************     '\r\nGraphics Processor:  %0.1f°F\r\nLow:      %0.1f°F\r\nHigh:     %0.1f°F\r\n'     ***************     '\r\nCentral Processor:  %0.1f°F\r\nLow:      %0.1f°F\r\nHigh:     %0.1f°F" % (fahrenheit, tShopLow, tShopHigh, GPUfahrenheit, tGpuLow, tGpuHigh, CPUfahrenheit, tCpuLow, tCpuHigh)
 
