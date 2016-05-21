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

################################################## USER CONFIGURATION ##################################################
########################################################################################################################
# You may wish to configure the value of any of the variables below.
thresholdLower = (170, 190, 140)  # The lower threshold for thresholding
thresholdUpper = (180, 210, 170)  # The upper threshold for thresholding
targetLostMessage = "TARGET LOST. Auto Search Mode Activated. "  # What the console should say when it's in search mode
targetFoundMessage = "TARGET AQUIRED. Dispensing product."  # What the console should say when it's in firing mode
HSV = False  # Set to True to display a window with HSV colours, double click to print a pixel's HSV value to console
FPS = True  # Set to True to print out the estimated FPS

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
import random  # needed to pick a "random" audio file to play
import time  # keep track of things
import cv2  # We kind of need this for computer vision
import pygame  # We use a function in this to play the audio
import KalmanFilter  # stops my terrible algorithm from being so glitchy

# Let's init all the things
xFilter = KalmanFilter.KalmanFilter(50, 500)  # A kalman filter for x values
yFilter = KalmanFilter.KalmanFilter(50, 500)  # A kalman filter for y values, because *why* not? ;)
pygame.mixer.init()  # Required to initiliase pygame
cap = cv2.VideoCapture(0)  # Required to initialise the videocapture

# These are just normal variables for holding all the things, don't touch if you want the program to run
areaArray = []  # For storing the area of our countours
lastTime = 0  # Last time we stored the time of the frame (for FPS calculations)
lastSeen = 0  # Keep track of when we saw the target
fps = 1  # Things break if a default value isn't set and you disable FPS calculations
searchLastPlayed = 0  # When a "searching" phrase was last played
playGunSound = False  # Used to start the gun sound after we play a random phrase
filteredX, filteredY = 0, 0  # These vairables will store the value of the x,y cords passed through the kalman filter

# Callback function for mouse, prints HSV values to console
def print_hsv(event, x, y, flags, param):
    global hsv, frame, xi, yi

    if event == cv2.EVENT_LBUTTONDBLCLK:  # If it was a double left click
        xi, yi = x, y  # Make the cords into the global variables
        frame = cv2.circle(frame, (xi, yi), 10, (0, 0, 0), -1)  # Draw green circle on click position
        # Prints colour of pixel, remember these are HSV, not RGB values
        print("H,S,V: " + str(hsv.item(y, x, 0)) + "," + str(hsv.item(y, x, 1)) + "," + str(hsv.item(y, x, 2)))

# Should we setup the HSV window?
if HSV:
    cv2.namedWindow('HSV')  # Setup a blank window
    cv2.setMouseCallback('HSV', print_hsv)  # Attach the mouse callback funciton

###################################################### END SETUP #######################################################
########################################################################################################################

while True:
    global xi, yi

    ret, frame = cap.read()  # capture a new frame
    thisTime = int(time.time() * 1000)  # record when we capture the new frame for fps calculations

    if FPS:  # If we are doing FPS calculations
        fps = thisTime - lastTime  # Work out time between this and the last frame
        lastTime = thisTime  # Store what time this frame was at
        fps = 1000 / fps  # Conver the time to FPS
    else:
        fps = 1  # If we aren't doing fps calculations set to 1 or things break

    final = frame  # create the variable to hold our final frame

    ##### Process the frame #####
    blurred = cv2.GaussianBlur(frame, (11, 11), 0)  # Blur the frame to remove high frequency noise
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)  # Convert frame to the HSV colorspace
    mask = cv2.inRange(hsv, thresholdLower, thresholdUpper)  # Do the actual thresholding

    # To be honest these next two functions don't do much and decrease fps by about 20%
    mask = cv2.erode(mask, None, iterations=3) # Do some more filtering
    mask = cv2.dilate(mask, None, iterations=3) # Do some even more filtering

    _, contours, _ = cv2.findContours(mask.copy(), 1, 2)  # Find the contours

    if not contours:  # If there isn't any contours (targets) detected
        if thisTime - lastSeen > 100:  # If it's been at least 1 second since last time
            if thisTime - searchLastPlayed > 5000:  # If it's been at least 5 seconds since last time
                searchLastPlayed = int(round(time.time() * 1000))  # Record the current time
                pygame.mixer.music.load(searchAudioFiles[random.randint(0, 7)])  # Select a phrase at random
                pygame.mixer.music.play()  # Play the randomly selected phrase
                scanningMode = True
            print("\r" + targetLostMessage + " FPS: " + str(fps), end="")  # Print target lost message and the FPS
        final = cv2.circle(final, (int(filteredX), 470), 10, (0, 0, 255), -1)  # Draw a circle representing servo position

    else:  # If a contour has been detected

        if thisTime - lastSeen > 1000:  # If it's been at least 1 second since last time
            activeLastPlayed = int(round(time.time() * 1000))  # Record the current time
            print("\r" + targetFoundMessage + " FPS: " + str(fps), end="")  # Print the target found message and FPS
            pygame.mixer.music.load(fireAudioFiles[random.randint(0, 14)])  # Load a randomly selected phrase
            pygame.mixer.music.play()  # Play the randomly selected phrase
            scanningMode = False

        # Find the area of each contour
        for i, c in enumerate(contours):  # Loop over every contour
            area = cv2.contourArea(c)  # Calculated the area
            areaArray.append(area)  # Store it in the list

        # Find the largest contour
        sorteddata = sorted(zip(areaArray, contours), key=lambda x: x[0], reverse=True)  # Sort the list
        largestcontour = sorteddata[0][1]  # Largest contour is the first one in the list
        x, y, w, h = cv2.boundingRect(largestcontour)  # Store the data about it

        # Filter and return the xValue
        xFilter.input_latest_noisy_measurement(x)  # x is the unfiltered value
        filteredX = xFilter.get_latest_estimated_measurement()  # request the filtered value

        # Filter and return the yValue
        yFilter.input_latest_noisy_measurement(y)  # y is the unfiltered value
        filteredY = yFilter.get_latest_estimated_measurement()  # request the filtered value

        printVals = "Filtered X: " + str(int(filteredX)) + " Filtered Y: " + str(int(filteredY))
        print("\r" + printVals + " FPS: " + str(fps), end="")  # Print the filtered values and FPS
        final = cv2.circle(final, (int(filteredX), 470), 10, (0, 255, 0),
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



    cv2.imshow("Cool Things", final)  # Draw the filtered x cord onto the bottom, mimicking the servo output

    if HSV:  # If we should draw the HSV window
        cv2.imshow("HSV", hsv)  # Enable and double click anywhere on screen to print HSV values to console

    key = cv2.waitKey(1) & 0xFF

    if key == ord("q"):  # If the "q" key is pressed
        time.sleep(1)
        pygame.mixer.music.load("audio/turret_disabled_4.wav")  # Load the closing down sound
        pygame.mixer.music.play()  # Play the closing sounds
        while pygame.mixer.music.get_busy() == True:
            continue
        break  # Quit the loop and program

cv2.destroyAllWindows()
