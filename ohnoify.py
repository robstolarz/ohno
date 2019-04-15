#!/usr/bin/env python
import argparse
import math
import os
import sys
import time

import cv2
import numpy as np

# rectifying from https://github.com/opencv/opencv/blob/46353564353e0e6c6d82a47f52283957ddd37e8b/samples/cpp/squares.cpp#L92
rectify = lambda c: cv2.approxPolyDP(c, cv2.arcLength(c, True) * 0.02, True)
distance = lambda origin, xypair: math.sqrt( (xypair[0]-origin[0]) ** 2 + (xypair[1]-origin[1]) ** 2 )
def approxarea(c):
  _, _, w, h = cv2.boundingRect(c)
  return w * h

class DetectionError(ValueError):
  pass

class NotEnoughPanelsError(DetectionError):
  pass

def ohnoify_tryboththresholds(inpath, outpath, debug):
  # remember, findContours may sometimes do better when targets are white and backgrounds are black
  # the assumption here is that most of these comics will have a white, invertible background
  try:
    ohnoify(inpath, outpath, debug, cv2.THRESH_BINARY_INV)
  except NotEnoughPanelsError:
    if debug:
      print("(inverting didn't work, what if we try not inverting it?)")
    ohnoify(inpath, outpath, debug, cv2.THRESH_BINARY)

def ohnoify(inpath, outpath, debug, thresholdtype):
  # get image
  image = cv2.imread(inpath)

  # clean up image
  gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
  blurred = cv2.GaussianBlur(gray, (5, 5), 0)
  _, threshold = cv2.threshold(blurred, 63, 255, thresholdtype)

  allcontours, hierarchy = cv2.findContours(threshold, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
  if debug:
    print(sorted([(len(rectify(c)), approxarea(c)) for c in allcontours], key=lambda t: t[1], reverse=True))
  rectcontours = [c for c in allcontours if len(rectify(c)) == 4 and approxarea(c) > 100]
  if len(rectcontours) < 3 and not debug:
    raise NotEnoughPanelsError(f"this comic ({inpath}) has too few panels, aborting")
  imgbottomright = (image.shape[1], image.shape[0])
  # sort contours by centroid distance from imgbottomright
  # super messy but it's not completely wrong and I just want to ship this tbh
  disted = sorted([(con, min([distance(imgbottomright, pt[0]) for pt in con])) for con in rectcontours], key=lambda t: t[1])
  # desired contour is the one at the top of the list
  thecontour, dist = disted[0]

  # now that we have `thecontour`, we can mask and crop
  # heavily adapted from http://answers.opencv.org/question/37441/how-to-set-transparent-background-to-grabcut-output-image-in-opencv-c/
  # draw the alpha layer so the cutout looks nice
  alpha = np.zeros((image.shape[0], image.shape[1], 1), dtype = "uint8")
  cv2.drawContours(alpha, [thecontour], -1, (255), -1)

  # merge the alpha layer onto the image directly
  b, g, r = cv2.split(image)
  alphafied = cv2.merge((b, g, r, alpha))

  # finally, crop the image down to its content
  # tradeoff: more pixels are processed but because there's no projection the code is simpler
  x, y, w, h = cv2.boundingRect(thecontour)
  croppedalphafied = alphafied[y:y+h, x:x+w]

  if os.path.isdir(outpath):
    outpath = os.path.join(outpath, os.path.basename(inpath))
  cv2.imwrite(outpath, croppedalphafied)

  # debug drawing
  if debug:
    print(f"image had {len(rectcontours)} rectangles.")
    print(f"of these, the closest was {dist} units from the bottom right")
    drawnimage = image.copy()
    cv2.drawContours(drawnimage, allcontours, -1, (0, 85, 0), 3)
    cv2.drawContours(drawnimage, rectcontours, -1, (0, 170, 0), 3)
    cv2.drawContours(drawnimage, [thecontour], -1, (0, 255, 0), 3)
    cv2.imshow('image', drawnimage)

    start_time = time.time()
    while time.time() < start_time + 1:
      cv2.waitKey(0)
    cv2.destroyAllWindows()

    cv2.imshow('image', croppedalphafied)
    start_time = time.time()
    while time.time() < start_time + 1:
      cv2.waitKey(0)
    cv2.destroyAllWindows()

    if len(rectcontours) < 3:
      raise NotEnoughPanelsError(f"this comic ({inpath}) has too few panels, aborting")

if __name__ == "__main__":
  parser = argparse.ArgumentParser(description='Cut the last panel out of a comic with CV.')
  # TODO: add stdin support (filename "-")
  # TODO: consider `nargs='+'` and processing multiple in files?
  parser.add_argument('infile', type=str, help='the input file')
  # TODO: add stdout support when arg not supplied
  parser.add_argument('--outpath', '-o', type=str, help='the output path (file or folder)')
  parser.add_argument('--debug', action='store_true', help='for showing off how totally radical the process is but maybe also debugging')
  args = parser.parse_args()
  # TODO: is there a better way of doing this
  ohnoify_tryboththresholds(args.infile, args.outpath, args.debug)
