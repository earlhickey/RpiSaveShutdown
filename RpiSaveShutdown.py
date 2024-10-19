#!/usr/bin/env python3

import RPi.GPIO as GPIO
import os
import time
import threading

# Setup
GPIO.setwarnings(False)  # Disable warnings
GPIO.setmode(GPIO.BCM)   # Use BCM pin numbering
GPIO.setup(18, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Pin 18 as input with pull-up resistor

shutdown_pending = False  # Flag to indicate if shutdown is pending
shutdown_timer = None      # Timer reference

def shutdown_pi():
    """Shutdown the Raspberry Pi."""
    print("Flushing data to disk...")
    os.system('sync')  # Ensure all data is written to disk
    print("Shutting down...")
    os.system("shutdown -h now")  # Execute shutdown command

def start_shutdown_timer():
    """Start a timer for 10 seconds before shutting down."""
    global shutdown_pending
    shutdown_pending = True
    time.sleep(10)  # Wait for 10 seconds
    if shutdown_pending:  # Check if shutdown is still pending
        shutdown_pi()  # Call shutdown function

def gpio_callback(channel):
    """Callback for GPIO pin state change."""
    global shutdown_timer, shutdown_pending

    if GPIO.input(18) == GPIO.HIGH:
        # Power dropped, initiate shutdown
        print("Power dropped! Shutting down in 10 seconds...")
        shutdown_timer = threading.Thread(target=start_shutdown_timer)
        shutdown_timer.start()  # Start the shutdown timer in a new thread
    else:
        # Power restored, cancel any shutdown
        print("Power restored! Canceling shutdown.")
        shutdown_pending = False  # Mark shutdown as not pending

# Event detection
GPIO.add_event_detect(18, GPIO.BOTH, callback=gpio_callback, bouncetime=1000)

try:
    print("Monitoring GPIO pin 18 for state changes...")
    while True:
        time.sleep(1)  # Keep the script running

except KeyboardInterrupt:
    print("Script interrupted by user.")

finally:
    GPIO.cleanup()  # Clean up GPIO settings
    print("GPIO cleanup complete. Exiting.")
