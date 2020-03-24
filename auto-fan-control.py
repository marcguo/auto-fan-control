'''
The idea is to run this script every 5 minutes to find out if the system is overheating.
The fan should be on until the temperature falls under the lower bound limit. Then we exit
from the script.
This script can be run using an auto-scheduler.
'''

# For issuing shell commands.
import subprocess
# For controlling GPIO pins.
from gpiozero import OutputDevice
# For parsing temperature from the command output.
import re
# For the sleep method, used to keeping the fan on.
import time
# For removing the old log.
import os
# For logging the current time at the beginning of the log.
import datetime

# This is the GPIO pin that's connected to the transistor.
GPIO_PIN = 17
# This is the GPIO control for the fan.
FAN = OutputDevice(GPIO_PIN)
# This defines the high (trigger for on) temperature.
HIGH = 55
# This defines the low (trigger for off) temperature.
LOW = 45
# This defines a minute in seconds, used for timing the fan on time.
MINUTE = 60
# This defines the file name of the local log file.
FILE_NAME = 'log.txt'

# Method to automatic control the fan on the board.
def auto_fan_control():
    # Remove the existing log file.
    try:
        os.remove(FILE_NAME)
    except OSError:
        pass

    # Log the starting time.
    log(str(datetime.datetime.now()))

    # Read the current temperature.
    temp = read_temp()
    # If it's too hot, turn the fan on.
    if is_too_hot(temp):
        info = "The fan was turned on because the Pi's current temperature exceeds the trigger value of " + str(HIGH) + "'C."
        print(info)
        log(info)
        
        # Track the duration that the fan has been on.
        start_time = time.time()

        cool_down()

        end_time = time.time()
        duration = end_time - start_time

        info = 'The fan was on for ' + str(duration) + ' seconds.'
        print(info)
        log(info)
    else:
        info = 'The current board temperature is not hot enough to turn on the fan.'
        print(info)
        log(info)

        info = 'The triggering temp value is: ' + str(HIGH) + "'C."
        print(info)
        log(info)

# Method to run the fan until the board temperature is below the lower bound limit.
def cool_down():
    # Set the temp to HIGH just so that the while loop does not quit before the code
    # even runs...
    temp = HIGH

    while not is_cool_enough(temp):
        fan_on()
        time.sleep(MINUTE)
        temp = read_temp()
    
    # When the while loop exits, we know that the board temp is below the lower bound limit.
    fan_off()
    
    info = "The fan was turned off because the Pi's current temperature is below the trigger value of " + str(LOW) + "'C."
    print(info)
    log(info)

# Function to read and output the Pi's current temperature.
def read_temp():
    # First, read the temperature of the board.
    cmd = ['/opt/vc/bin/vcgencmd', 'measure_temp']
    # Issue the command.
    proc = subprocess.Popen(cmd, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
    # Get the output and error messages.
    o, e = proc.communicate()

    # Output the command output status.
    # Debug:
    #print('Output: ' + o)
    #print('Error: '  + e)
    #print('Code: ' + str(proc.returncode))

    # The output's format is:
    # Output: temp=47.0'C
    # Let's parse this output string to get the temperature info that we want.
    # Note: Regex's findall function returns a list of strings, so we need to convert
    # the first element in the list to a float.
    temp_array = re.findall(r'[-+]?\d*\.\d+|\d+', o)
    temp = float(temp_array[0])
    
    info = 'The current temp is: ' + str(temp)
    print(info)
    log(info)
    return temp

# Function that determines if the passed in temperature is too hot so that we need
# to turn on the fan.
def is_too_hot(temp):
    return temp >= HIGH

# Function that determines if the passed in temperature is cool enough so that we 
# can turn off the fan.
def is_cool_enough(temp):
    return temp <= LOW

# Method to turn the fan on (to set the GPIO bit to high).
def fan_on():
    FAN.on()

# Method to turn the fan off (to set the GPIO bit to low).
def fan_off():
    FAN.off()

# Method to write to the local log file.
def log(content):
    with open(FILE_NAME, 'a') as file:
        file.write(content + '\n')

# Execute the method.
auto_fan_control()
