'''
This is a blob tracker.  It's a very basic algorithm and is just an example on how you could track something using
OpenCV's built in blob detector.  It's released under the GNU GPL v3 or later license.

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

import numpy as np
import cv2

#Make a class for capturing video
cap = cv2.VideoCapture(0)

while (True):

    # Capture each frame
    ret, frame = cap.read()

    # Convert the frame to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Setup parameters for the blob detector
    params = cv2.SimpleBlobDetector_Params()

    # Set threshold values (below is all grayscale values)
    params.minThreshold = 80
    params.maxThreshold = 150

    # Filter by the area of blobs (so it doesn't pick up lots of noise)
    params.filterByArea = True
    params.minArea = 200
    params.maxArea = 100000

    # Setup the detector with all the parameters we set
    detector = cv2.SimpleBlobDetector_create(params)

    # Try to detect the blobs
    keypoints = detector.detect(gray)

    #Draw blobs that we detects as red circles
    im_with_keypoints = cv2.drawKeypoints(gray, keypoints, np.array([]), (0, 0, 255),
                                          cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)

    # Show all the blobs on the video
    cv2.imshow("Detected Blobs", im_with_keypoints)

    # Press the "q" button to quite while running
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()