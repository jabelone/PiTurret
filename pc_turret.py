'''
This is an open source object tracking turret.  It has a sad, pessimistic  turret that activates and fires when it's
targets come within range.  It's released under the GNU GPL v3 or later license.

Copyright (C) 2016 Jaimyn Mayer (Known as "Jabelone" online)

This file is part of PortalTurret.

    PortalTurret is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    PortalTurret is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with PortalTurret.  If not, see <http://www.gnu.org/licenses/>.
'''

import random  # needed to pick a "random" audio file to play
import time  # keep track of things
import cv2  # We kind of need this for cv
import pygame.mixer  # We use a function in this to play the audio
import KalmanFilter  # stops my terrible algorithm from being so glitchy
import configparser #  To store our settings
import os.path
import subprocess


################################################## USER CONFIGURATION ##################################################
########################################################################################################################
#  All of the user configuration should be done in the "config.ini" file in the same directory as this program.
searchAudioFiles = ["audio/turret_autosearch_6.wav",
                    "audio/turret_autosearch_5.wav",
                    "audio/turret_autosearch_4.wav",
                    "audio/turret_autosearch_3.wav",
                    "audio/turret_autosearch_2.wav",
                    "audio/turret_search_4.wav",
                    "audio/turret_search_2.wav",
                    "audio/turret_search_1.wav"]

fireAudioFiles = ["audio/turret_active_6.wav",
                  "audio/turret_active_5.wav",
                  "audio/turret_active_4.wav",
                  "audio/turret_active_3.wav",
                  "audio/turret_active_2.wav",
                  "audio/turret_active_1.wav",
                  "audio/turret_deploy_6.wav",
                  "audio/turret_deploy_5.wav",
                  "audio/turret_deploy_4.wav",
                  "audio/turret_deploy_3.wav",
                  "audio/turret_deploy_2.wav",
                  "audio/turret_deploy_1.wav",
                  "audio/turret_retire_3.wav",
                  "audio/turret_retire_5.wav",
                  "audio/turret_retire_7.wav"]
########################################################################################################################
################################################ END USER CONFIGURATION ################################################

##################################################### START SETUP ######################################################
########################################################################################################################

# Apparently this lies.  It does not start the servo blaster process properly so start it yourself.
# I have no idea why as this same code snippet worked on another project and at the moment it is low priority.

output = subprocess.getoutput('ps -A')
if 'servod' in output:
    print("Servo Blaster process found.")
else:
    print("Servo Blaster process not found. Starting it now.")
    os.system("echo pi | sudo service servoblaster start")

# Let's init all the things
xFilter = KalmanFilter.KalmanFilter(50, 500)  # A kalman filter for x values
yFilter = KalmanFilter.KalmanFilter(50, 500)  # A kalman filter for y values, because *why* not? ;)
pygame.mixer.init()  # Required to initiliase pygame
config = configparser.ConfigParser()
cap = cv2.VideoCapture(0)  # Required to initialise the videocapture
time.sleep(0.1)  # Allow the camera to warm before doing anything else

#################### Load or create a config file ####################
if os.path.isfile("config.ini") == False:  # If we don't have a config file then we should make one
    print("\nNo config file was found. I just tried to make one and load it with defaults.\n")
    config['Settings'] = {'targetFoundMessage': 'TARGET AQUIRED. Dispensing product.',
                          'targetLostMessage': 'TARGET LOST. Auto Search Mode Activated.',
                          'mainWindowTitle': 'Portal Turret v1',
                          'NORMAL': '1',
                          'FPS': '1',
                          'PiCam-Manual-Settings': 'False',  # True or False to use manual pi camera options
                          'cascade-path': 'faces.xml'
                          }

    config['Camera'] = {'cam-xres': '300',
                        'cam-yres': '300',
                        'cam-framerate': '30',
                        'cam-xres': '300',
                        'cam-rotation:': '0',
                        'cam-awb:': 'off',
                        'cam-awb-gains1:': '1.65',
                        'cam-awb-gains2:': '1.45',
                        'cam-saturation:': '-35',
                        'cam-exposure:': '0',
                        'cam-shutterspeed:': '20000',
                        'cam-iso:': '600',
                        'cam-contrast:': '50',
                        'cam-brightness:': '60'}

    config['Webcam'] = {'webcam-xres': '1280',
                        'webcam-yres': '720',}

    with open('config.ini', 'w') as configfile:
        config.write(configfile)
else:
    config.read('config.ini')
    if "Settings" in config:
        print("\nValid settings file found.  I will load the settings now.\n")

cap.set(3, float(config['Webcam']['webcam-xres']))
cap.set(4, float(config['Webcam']['webcam-yres']))

#################### END loading config file and setting camera options ####################

faceCascade = cv2.CascadeClassifier(config['Settings']['cascade-path'])  # Create an instance of our cascade classifier

# These are just normal variables for holding all the things, don't touch if you want the program to run
lastTime = 0  # Last time we stored the time of the frame (for FPS calculations)
lastSeen = 0  # Keep track of when we saw the target
fps = 1  # Things break if a default value isn't set and you disable FPS calculations
searchLastPlayed = 0  # When a "searching" phrase was last played
playGunSound = False  # Used to start the gun sound after we play a random phrase
filteredX, filteredY = 0, 0  # These variables will store the value of the x,y cords passed through the kalman filter
faceX, faceW = 0,2 # We may get a division by zero error if there are no faces

###################################################### END SETUP #######################################################
########################################################################################################################



while True:
    ret, frame = cap.read()  # capture a new frame

    final = frame  # create the variable to hold our final frame
    thisTime = int(time.time() * 1000)  # record when we capture the new frame for fps calculations

    if config['Settings']['FPS']:  # If we are doing FPS calculations
        fps = thisTime - lastTime  # Work out time between this and the last frame
        lastTime = thisTime  # Store what time this frame was at
        fps = 1000 / fps  # Conver the time to FPS
    else:
        fps = 1  # If we aren't doing fps calculations set to 1 or things break

    #################### Process the frame ####################
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # Convert to gray

    faces = faceCascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(30, 30),
        flags=cv2.CASCADE_SCALE_IMAGE
    )

    for (x, y, w, h) in faces:
        global faceX, faceW

        cv2.rectangle(final, (x, y), (x + w, y + h), (0, 255, 0), 2)
        # print("Face Detected at:", x + (w / 2))
        faceX, faceW = x, w

    if len(faces) < 1:
        faceX = 0

    if faceX < 1:  # If there isn't any contours (targets) deteceted
        if thisTime - lastSeen > 100:  # If it's been at least 1 second since last time
            if thisTime - searchLastPlayed > 5000:  # If it's been at least 5 seconds since last time
                searchLastPlayed = int(round(time.time() * 1000))  # Record the current time
                pygame.mixer.music.load(searchAudioFiles[random.randint(0, 7)])  # Select a phrase at random
                pygame.mixer.music.play()  # Play the randomly selected phrase
                scanningMode = True
                print("\r\x1b[2K" + config['Settings']['targetlostmessage'] + " FPS: " + str(int(fps)),
                      end="")  # Print target lost message and the FPS
        final = cv2.circle(final, (int(filteredX), 10), 10, (0, 0, 255),
                           -1)  # Draw a circle representing servo position

    else:  # If a contour has been detected

        if thisTime - lastSeen > 1000:  # If it's been at least 1 second since last time
            activeLastPlayed = int(round(time.time() * 1000))  # Record the current time
            print("\r" + config['Settings']['targetfoundmessage'] + " FPS: " + str(int(fps)),
                  end="")  # Print the target found message and FPS
            pygame.mixer.music.load(fireAudioFiles[random.randint(0, 14)])  # Load a randomly selected phrase
            pygame.mixer.music.play()  # Play the randomly selected phrase
            scanningMode = False

        # Filter and return the xValue
        xFilter.input_latest_noisy_measurement(faceX + faceW / 2)  # x is the unfiltered value
        filteredX = xFilter.get_latest_estimated_measurement()  # request the filtered value

        # Filter and return the yValue
        # Left here in case someone wants to track in the Y direction also
        # yFilter.input_latest_noisy_measurement(y)  # y is the unfiltered value
        # filteredY = yFilter.get_latest_estimated_measurement()  # request the filtered value

        printVals = "Filtered X: " + str(int(filteredX)) + " Filtered Y: " + str(int(filteredY))
        print("\r\x1b[2K" + printVals + " FPS: " + str(int(fps)), end="")  # Print the filtered values and FPS

        # Un comment the following print statements for debugging
        '''if filteredX < 120:
            servo.servo_set(16, "+40us")
            # print("Servo +40us")

        elif filteredX < 140:
            servo.servo_set(16, "+40us")
            # print("Servo +40us")

        elif filteredX > 180:
            servo.servo_set(16, "-40us")
            # print("Servo -40us")

        elif filteredX > 165:
            servo.servo_set(16, "-10us")
            # print("Servo -10us")
        '''

        final = cv2.circle(final, (int(filteredX), 10), 10, (0, 255, 0),
                           -1)  # Draw a circle representing servo position
        lastSeen = int(round(time.time() * 1000))  # Store when we last saw the target
        if pygame.mixer.music.get_busy() == True:  # If music is already playing
            playGunSound = False  # Don't play music
        else:  # If music isn't already playing
            playGunSound = True  # Set the flag to play the gun sound
            pygame.mixer.music.load("audio/turret_fire_4x_01.wav")  # (pre)load the firing sounds

    if playGunSound:  # If the play gun sound flag has been set
        pygame.mixer.music.play()  # Play the firing sounds
        playGunSound = False  # Set to false cause we just played it

    cv2.imshow(config['Settings']['mainWindowTitle'], final)  # Draw the filtered x cord onto the bottom, mimicking the servo output

    key = cv2.waitKey(1) & 0xFF

    if key == ord("q"):  # If the "q" key is pressed
        time.sleep(1)
        pygame.mixer.music.load("audio/turret_disabled_4.wav")  # Load the closing down sound
        pygame.mixer.music.play()  # Play the closing sounds
        while pygame.mixer.music.get_busy() == True:
            continue
        break  # Quit the loop and program

cv2.destroyAllWindows()