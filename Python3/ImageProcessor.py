import numpy as np
import cv2
from tkinter import *
from tkinter import messagebox
from graphics import *
import math
from enum import Enum
import time

class ORIENTATION(Enum):
    LEFT = 1
    RIGHT = 2
    UNKNOWN = 3

img = cv2.imread('C:\\Users\\atataru\\Desktop\\IMG_0437.PNG', -1)

IMG_SIZE_HOR = len(img[0])/2
IMG_SIZE_VER = len(img)/2

resized_image = cv2.resize(img, (int(IMG_SIZE_HOR), int(IMG_SIZE_VER))) 

move_along_x = IMG_SIZE_HOR/10
TRIANGLE_SIZE = (2 * move_along_x)/math.sqrt(3)
OFFSET_X = -1
OFFSET_Y = -2
NR_COLORS = 5

cv2.imwrite('C:\\Users\\atataru\\Desktop\\result.PNG', resized_image)

window = GraphWin("KAMI 2 Puzzle Recreation Tool", IMG_SIZE_HOR, IMG_SIZE_VER)
image = PhotoImage(file = 'C:\\Users\\atataru\\Desktop\\result.PNG')
window.create_image(0, 0, image = image, anchor = NW)

triangles = []
colors = []

def drawTriangle(startingPoint, orientation):
    p1 = startingPoint
    if orientation == ORIENTATION.RIGHT:
        p2 = Point(startingPoint.x + move_along_x, startingPoint.y + TRIANGLE_SIZE/2)
    else:
        p2 = Point(startingPoint.x - move_along_x, startingPoint.y + TRIANGLE_SIZE/2)
    p3 = Point(startingPoint.x, startingPoint.y + TRIANGLE_SIZE)

    #window.create_polygon([p1.x, p1.y, p2.x, p2.y, p3.x, p3.y], outline='red', fill='', width=1)
    triangle = Polygon([p1, p2, p3])
    triangle.setOutline('red')
    triangle.setFill('')
    triangle.setWidth(1)
    triangle.draw(window)

    triangles.append(triangle)

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
                averageColor[0] += resized_image[row][column][2]
                averageColor[1] += resized_image[row][column][1]
                averageColor[2] += resized_image[row][column][0]
                samples += 1

        averageColor[0] /= samples
        averageColor[0] = int(averageColor[0])
        averageColor[1] /= samples
        averageColor[1] = int(averageColor[1])
        averageColor[2] /= samples
        averageColor[2] = int(averageColor[2])

        print(averageColor)
        colors.append(averageColor)
        
        #window.create_polygon([sulcX, sulcY, sulcX + COLOR_PALLETE_WIDTH, sulcY, sulcX + COLOR_PALLETE_WIDTH, IMG_SIZE_VER, sulcX, IMG_SIZE_VER], outline='yellow', fill='', width=2)
        colorPallete = Polygon([Point(sulcX, sulcY), Point(sulcX + COLOR_PALLETE_WIDTH,sulcY), Point(sulcX + COLOR_PALLETE_WIDTH,IMG_SIZE_VER), Point(sulcX,IMG_SIZE_VER)])
        #colorPallete.setOutline('yellow')
        colorPallete.setFill(color_rgb(averageColor[0], averageColor[1], averageColor[2]))
        colorPallete.setWidth(1)
        colorPallete.draw(window)

        for column in range(int(ROW_RANGE_START), int(ROW_RANGE_END)):
            for row in range(int(COLUMN_RANGE_START), int(COLUMN_RANGE_END)):
                resized_image[row][column][0] = averageColor[0]
                resized_image[row][column][1] = averageColor[1]
                resized_image[row][column][2] = averageColor[2]

    
        
        sulcX += COLOR_PALLETE_WIDTH

def centerFromPoints(p1, p2, p3):
    offset = pow(p2.x,2) + pow(p2.y,2);
    bc =   ( pow(p1.x,2) + pow(p1.y,2) - offset )/2.0
    cd =   (offset - pow(p3.x, 2) - pow(p3.y, 2))/2.0
    det =  (p1.x - p2.x) * (p2.y - p3.y) - (p2.x - p3.x)* (p1.y - p2.y)

    idet = 1/det;

    centerx =  (bc * (p2.y - p3.y) - cd * (p1.y - p2.y)) * idet
    centery =  (cd * (p1.x - p2.x) - bc * (p2.x - p3.x)) * idet

    return [int(centerx), int(centery)];

def distance(c1, c2):
    (r1,g1,b1) = c1
    (r2,g2,b2) = c2
    return pow(math.sqrt(r1 - r2),2) + pow((g1 - g2), 2) + pow((b1 - b2),2)

def getColorCode(triangle):
    points = triangle.getPoints()
    centerPoint = centerFromPoints(points[0], points[1], points[2])
    centerColor = resized_image[centerPoint[1]][centerPoint[0]]

    bestMatchingColor = 0
    bestRatio = 255
    for colorIdx in range(0, len(colors)):
        currColor = colors[colorIdx]
        ratio = (abs(currColor[0] - centerColor[2]) + abs(currColor[1] - centerColor[1]) + abs(currColor[2] - centerColor[0])) / 3
        if ratio < bestRatio:
            bestRatio = ratio
            bestMatchingColor = colorIdx

    if bestRatio > 40:
        return -1
    
    return bestMatchingColor

def clasifyTriangles():
    for triangle in triangles:
        time.sleep(0.05)
        colorCode = getColorCode(triangle)
        if colorCode == -1:
            triangle.undraw()
        else:            
            triangleColor = colors[colorCode]
            triangle.setFill(color_rgb(triangleColor[0], triangleColor[1], triangleColor[2]))

def mouseCallback(clickedPoint):
    print('x: ' + str(clickedPoint.x) + ', y: ' + str(clickedPoint.y) + ' = ' + str(resized_image[clickedPoint.y][clickedPoint.x]))

if __name__ == "__main__":
    drawBoardForFirstTime()
    drawColorMarkings()
    clasifyTriangles()
    window.setMouseHandler(mouseCallback)
    window.mainloop()
