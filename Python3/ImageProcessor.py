import numpy as np
import cv2
from tkinter import *
from tkinter import messagebox
from graphics import *
import math
from enum import Enum

class ORIENTATION(Enum):
    LEFT = 1
    RIGHT = 2
    UNKNOWN = 3

img = cv2.imread('C:\\Users\\alexandruflavian.ta\\Desktop\\IMG_0437.PNG', 0)
move_along_x = 53.4
TRIANGLE_SIZE = (2 * move_along_x)/math.sqrt(3)
OFFSET_X = -1
OFFSET_Y = -2

edges = cv2.Canny(img, 500, 500)

cv2.imwrite('C:\\Users\\alexandruflavian.ta\\Desktop\\result.PNG',img)

window = GraphWin("KAMI 2 Puzzle Recreation Tool", len(img[0]), len(img))
image = PhotoImage(file = 'C:\\Users\\alexandruflavian.ta\\Desktop\\result.PNG')
window.create_image(0, 0, image = image, anchor = NW)

def drawTriangle(startingPoint, orientation):
    p1 = startingPoint
    if orientation == ORIENTATION.RIGHT:
        p2 = Point(startingPoint.x + move_along_x, startingPoint.y + TRIANGLE_SIZE/2)
    else:
        p2 = Point(startingPoint.x - move_along_x, startingPoint.y + TRIANGLE_SIZE/2)
    p3 = Point(startingPoint.x, startingPoint.y + TRIANGLE_SIZE)

    window.create_polygon([p1.x, p1.y, p2.x, p2.y, p3.x, p3.y], dash=(1,), outline='red', fill='', width=1)

BOARD_SIZE_X = len(img[0])
SIZE_OF_BAR = 50
BOARD_SIZE_Y = len(img) - SIZE_OF_BAR


def drawBoardForFirstTime():
    startPosY = 0
    headerPosX = 0
    while headerPosX <= BOARD_SIZE_X:
        drawTriangle(Point(headerPosX + OFFSET_X, startPosY - TRIANGLE_SIZE/2 + OFFSET_Y), ORIENTATION.RIGHT)
        drawTriangle(Point(headerPosX + move_along_x * 2 + OFFSET_X, startPosY - TRIANGLE_SIZE/2 + OFFSET_Y), ORIENTATION.LEFT)
        headerPosX += move_along_x * 2

    while startPosY <= BOARD_SIZE_Y - TRIANGLE_SIZE:
        startPosX = move_along_x
        while startPosX <= BOARD_SIZE_X - move_along_x:
            drawTriangle(Point(startPosX + OFFSET_X, startPosY + OFFSET_Y), ORIENTATION.LEFT)
            drawTriangle(Point(startPosX + OFFSET_X, startPosY + OFFSET_Y), ORIENTATION.RIGHT)
            startPosX += move_along_x * 2
        startPosX = 0
        while startPosX <= BOARD_SIZE_X - move_along_x * 2:
            drawTriangle(Point(startPosX + OFFSET_X, startPosY + TRIANGLE_SIZE/2 + OFFSET_Y), ORIENTATION.RIGHT)
            drawTriangle(Point(startPosX + OFFSET_X + move_along_x * 2, startPosY + TRIANGLE_SIZE/2 + OFFSET_Y), ORIENTATION.LEFT)
            startPosX += move_along_x * 2
        startPosY += TRIANGLE_SIZE

#window.create_polygon([OFFSET_X + 3 * move_along_x, OFFSET_Y + TRIANGLE_SIZE, OFFSET_X + 4 * move_along_x, OFFSET_Y + TRIANGLE_SIZE * 1.5, OFFSET_X + 3 * move_along_x, OFFSET_Y + TRIANGLE_SIZE * 2], dash=(1,), outline='red', fill='', width=1)

drawBoardForFirstTime()

#window.mainloop()
