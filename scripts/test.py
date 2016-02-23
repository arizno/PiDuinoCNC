# -*- coding: utf-8 -*-

# Imports
import time
import sys
sys.path.append("/home/pi/WebIOPi-0.7.1/CNC/scripts")   #Change this to the folder where script.py is
import webiopi
import lcd

# Initialize LCD display
lcd.__init__()

# Retrieve GPIO lib
GPIO = webiopi.GPIO

# RGB LED GPIO pins
RED = 11
GREEN = 9
BLUE = 10

# Sets LCD display text color
def setColor(rgb):
    GPIO.pwmWrite(RED, rgb[0])
    GPIO.pwmWrite(GREEN, rgb[1])
    GPIO.pwmWrite(BLUE, rgb[2])


# Called by WebIOPi when service starts
def setup():
    webiopi.debug("Script with macros - Setup")
    # Setup GPIOs
    GPIO.setFunction(RED, GPIO.PWM)
    GPIO.setFunction(GREEN, GPIO.PWM)
    GPIO.setFunction(BLUE, GPIO.PWM)


# Looped by WebIOPi
def loop():
    try:
        #LCD background white
        GPIO.pwmWrite(RED, 0.0)
        GPIO.pwmWrite(GREEN, 0.6)
        GPIO.pwmWrite(BLUE, 0.8)
        lcd.lcd_byte(lcd.LCD_LINE_1, lcd.LCD_CMD)
        lcd.lcd_string("openbuilds.com")
        lcd.lcd_byte(lcd.LCD_LINE_2, lcd.LCD_CMD)
        lcd.lcd_string("Build Anything")
        time.sleep(2)

        GPIO.pwmWrite(RED, 1.0)
        GPIO.pwmWrite(GREEN, 1.0)
        GPIO.pwmWrite(BLUE, 0.0)
        lcd.lcd_byte(lcd.LCD_LINE_1, lcd.LCD_CMD)
        lcd.lcd_string("Dream It")
        lcd.lcd_byte(lcd.LCD_LINE_2, lcd.LCD_CMD)
        lcd.lcd_string("")
        time.sleep(1)

        GPIO.pwmWrite(RED, 0.0)
        GPIO.pwmWrite(GREEN, 1.0)
        GPIO.pwmWrite(BLUE, 1.0)
        lcd.lcd_byte(lcd.LCD_LINE_1, lcd.LCD_CMD)
        lcd.lcd_string("Build It")
        lcd.lcd_byte(lcd.LCD_LINE_2, lcd.LCD_CMD)
        lcd.lcd_string("")
        time.sleep(1)

        GPIO.pwmWrite(RED, 1.0)
        GPIO.pwmWrite(GREEN, 0.0)
        GPIO.pwmWrite(BLUE, 1.0)
        lcd.lcd_byte(lcd.LCD_LINE_1, lcd.LCD_CMD)
        lcd.lcd_string("Share It")
        lcd.lcd_byte(lcd.LCD_LINE_2, lcd.LCD_CMD)
        lcd.lcd_string("")
        time.sleep(2)

        GPIO.pwmWrite(RED, 1.0)
        GPIO.pwmWrite(GREEN, 1.0)
        GPIO.pwmWrite(BLUE, 1.0)
        lcd.lcd_byte(lcd.LCD_LINE_1, lcd.LCD_CMD)
        lcd.lcd_string("")
        lcd.lcd_byte(lcd.LCD_LINE_2, lcd.LCD_CMD)
        lcd.lcd_string("")
    finally:
        webiopi.sleep(5)
