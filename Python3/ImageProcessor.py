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

img = cv2.imread('C:\\Users\\atataru\\Desktop\\IMG_0437.PNG', 1)

IMG_SIZE_HOR = len(img[0])/2
IMG_SIZE_VER = len(img)/2

resized_image = cv2.resize(img, (int(IMG_SIZE_HOR), int(IMG_SIZE_VER))) 

move_along_x = IMG_SIZE_HOR/10
TRIANGLE_SIZE = (2 * move_along_x)/math.sqrt(3)
OFFSET_X = -1
OFFSET_Y = -2
NR_COLORS = 5

edges = cv2.Canny(resized_image, 500, 500)

cv2.imwrite('C:\\Users\\atataru\\Desktop\\result.PNG', resized_image)

window = GraphWin("KAMI 2 Puzzle Recreation Tool", IMG_SIZE_HOR, IMG_SIZE_VER)
image = PhotoImage(file = 'C:\\Users\\atataru\\Desktop\\result.PNG')
window.create_image(0, 0, image = image, anchor = NW)

def drawTriangle(startingPoint, orientation):
    p1 = startingPoint
    if orientation == ORIENTATION.RIGHT:
        p2 = Point(startingPoint.x + move_along_x, startingPoint.y + TRIANGLE_SIZE/2)
    else:
        p2 = Point(startingPoint.x - move_along_x, startingPoint.y + TRIANGLE_SIZE/2)
    p3 = Point(startingPoint.x, startingPoint.y + TRIANGLE_SIZE)

    window.create_polygon([p1.x, p1.y, p2.x, p2.y, p3.x, p3.y], outline='red', fill='', width=1)

BOARD_SIZE_X = IMG_SIZE_HOR
SIZE_OF_BAR = IMG_SIZE_VER - 14 * TRIANGLE_SIZE
BOARD_SIZE_Y = IMG_SIZE_VER - SIZE_OF_BAR

def drawBoardForFirstTime():
    startPosY = 0
    headerPosX = 0
    while headerPosX <= BOARD_SIZE_X - TRIANGLE_SIZE:
        drawTriangle(Point(headerPosX + OFFSET_X, startPosY - TRIANGLE_SIZE/2 + OFFSET_Y), ORIENTATION.RIGHT)
        drawTriangle(Point(headerPosX + move_along_x * 2 + OFFSET_X, startPosY - TRIANGLE_SIZE/2 + OFFSET_Y), ORIENTATION.LEFT)
        headerPosX += move_along_x * 2

    while startPosY <= BOARD_SIZE_Y:
        startPosX = move_along_x
        while startPosX <= BOARD_SIZE_X - move_along_x + 10:
            drawTriangle(Point(startPosX + OFFSET_X, startPosY + OFFSET_Y), ORIENTATION.LEFT)
            drawTriangle(Point(startPosX + OFFSET_X, startPosY + OFFSET_Y), ORIENTATION.RIGHT)
            startPosX += move_along_x * 2
        startPosX = 0
        while startPosX <= BOARD_SIZE_X - move_along_x * 2 + 10:
            drawTriangle(Point(startPosX + OFFSET_X, startPosY + TRIANGLE_SIZE/2 + OFFSET_Y), ORIENTATION.RIGHT)
            drawTriangle(Point(startPosX + OFFSET_X + move_along_x * 2, startPosY + TRIANGLE_SIZE/2 + OFFSET_Y), ORIENTATION.LEFT)
            startPosX += move_along_x * 2
        startPosY += TRIANGLE_SIZE

def drawColorMarkings():
    FULL_COLOR_PALLE_WIDTH = IMG_SIZE_HOR - move_along_x * 4
    COLOR_PALLETE_WIDTH = FULL_COLOR_PALLE_WIDTH / NR_COLORS
    COLOR_PALLETE_HEIGHT = SIZE_OF_BAR

    sulcX = IMG_SIZE_HOR - FULL_COLOR_PALLE_WIDTH
    sulcY = IMG_SIZE_VER - COLOR_PALLETE_HEIGHT
    for i in range(0, NR_COLORS):
        topLeftPoint = Point(sulcX, sulcY)
        bottomRightPoint = Point(sulcX + COLOR_PALLETE_WIDTH, IMG_SIZE_VER)

        averageColor = [0, 0, 0]
        samples = 0
        STEP_H = COLOR_PALLETE_WIDTH/4
        STEP_V = COLOR_PALLETE_HEIGHT/4
        ROW_RANGE_START = sulcX + STEP_H
        ROW_RANGE_END = sulcX + STEP_H * 3
        COLUMN_RANGE_START = sulcY + STEP_V
        COLUMN_RANGE_END = sulcY + STEP_V * 3
        for column in range(int(ROW_RANGE_START), int(ROW_RANGE_END)):
            for row in range(int(COLUMN_RANGE_START), int(COLUMN_RANGE_END)):
                averageColor[0] += resized_image[row][column][0]
                averageColor[1] += resized_image[row][column][1]
                averageColor[2] += resized_image[row][column][2]
                samples += 1

        averageColor[0] /= samples
        averageColor[1] /= samples
        averageColor[2] /= samples

        print(averageColor)
        
        window.create_polygon([sulcX, sulcY, sulcX + COLOR_PALLETE_WIDTH, sulcY, sulcX + COLOR_PALLETE_WIDTH, IMG_SIZE_VER, sulcX, IMG_SIZE_VER], outline='yellow', fill='', width=2)
        sulcX += COLOR_PALLETE_WIDTH

if __name__ == "__main__":
    drawBoardForFirstTime()
    drawColorMarkings()
    window.mainloop()
