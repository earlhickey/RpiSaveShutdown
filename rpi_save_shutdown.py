#!/usr/bin/env python3
""" This shuts down a Raspberry Pi when power was cut """

import os
import time
import threading
from RPi import GPIO

# Setup
GPIO.setwarnings(False)  # Disable warnings
GPIO.setmode(GPIO.BCM)   # Use BCM pin numbering
GPIO.setup(18, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Pin 18 as input with pull-up resistor

SHUTDOWN_PENDING = False  # Flag to indicate if shutdown is pending
SHUTDOWN_TIMER = None      # Timer reference

def shutdown_pi():
    """Shutdown the Raspberry Pi."""
    print("Flushing data to disk...")
    os.system('sync')  # Ensure all data is written to disk
    print("Shutting down...")
    os.system("shutdown -h now")  # Execute shutdown command

def start_shutdown_timer():
    """Start a timer for 10 seconds before shutting down."""
    global SHUTDOWN_PENDING
    SHUTDOWN_PENDING = True
    time.sleep(10)  # Wait for 10 seconds
    if SHUTDOWN_PENDING:  # Check if shutdown is still pending
        shutdown_pi()  # Call shutdown function

def gpio_callback():
    """Callback for GPIO pin state change."""
    global SHUTDOWN_TIMER, SHUTDOWN_PENDING

    if GPIO.input(18) == GPIO.HIGH:
        # Power dropped, initiate shutdown
        print("Power dropped! Shutting down in 10 seconds...")
        SHUTDOWN_TIMER = threading.Thread(target=start_shutdown_timer)
        SHUTDOWN_TIMER.start()  # Start the shutdown timer in a new thread
    else:
        # Power restored, cancel any shutdown
        print("Power restored! Canceling shutdown.")
        SHUTDOWN_PENDING = False  # Mark shutdown as not pending

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
