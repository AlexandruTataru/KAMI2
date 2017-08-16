from graphics import *
from pynput import keyboard
from enum import Enum
import math
import random
from multiprocessing import Queue

class ORIENTATION(Enum):
    LEFT = 1
    RIGHT = 2
    UNKNOWN = 3

# Board set-up parameters
TRIANGLE_SIZE = 40
move_along_x = math.sqrt(3)/2.0 * TRIANGLE_SIZE
BOARD_SIZE_X = move_along_x * 10
BOARD_SIZE_Y = TRIANGLE_SIZE * 14
FOLDING_COLOR = color_rgb(50, 50, 50)

print('Available actions are:')
print('1. Color red\n2. Color green\n3. Color blue\n4. Color yellow\nu. Undraw\ns. Start processing')

BOARD_STARTING_COLOR_SELECTION = '3'

currentAction = BOARD_STARTING_COLOR_SELECTION

triangles = []

def getNeighbors(triangle):
    print('a1');
    print(triangle.getInternalColor())
    centerPoint = triangle.getCenterPoint()
    print('a2');
    n1 = centerPoint
    n2 = centerPoint
    n3 = centerPoint
    print('a3');
    if triangle.getOrientation() == ORIENTATION.LEFT:
        n1 = Point(centerPoint.x + 2 * (1.0/3.0 * move_along_x), centerPoint.y)
        n2 = Point(centerPoint.x - 1.0/3.0 * move_along_x, centerPoint.y + TRIANGLE_SIZE/2)
        n3 = Point(centerPoint.x - 1.0/3.0 * move_along_x, centerPoint.y - TRIANGLE_SIZE/2)
    elif triangle.getOrientation() == ORIENTATION.RIGHT:
        n1 = Point(centerPoint.x + 1.0/3.0 * move_along_x, centerPoint.y - TRIANGLE_SIZE/2)
        n2 = Point(centerPoint.x + 1.0/3.0 * move_along_x, centerPoint.y + TRIANGLE_SIZE/2)
        n3 = Point(centerPoint.x - 2 * (1.0/3.0 * move_along_x), centerPoint.y)

    neighbors = []
    for neighboardTriangle in triangles:
        if neighboardTriangle.isPointInside(n1) or neighboardTriangle.isPointInside(n2) or neighboardTriangle.isPointInside(n3):
                neighbors.append(neighboardTriangle)

    return neighbors

def getColor():
    rand_shade = random.randrange(30, 100, 20)
    color = color_rgb(0, 0, 0)
    if currentAction == '1':
        color = color_rgb(255, rand_shade, rand_shade)
    elif currentAction == '2':
        color = color_rgb(rand_shade, 255, rand_shade)
    elif currentAction == '3':
        color = color_rgb(rand_shade, rand_shade, 255)
    elif currentAction == '4':
        color = color_rgb(255, 255, rand_shade)

    return color

win = GraphWin("KAMI2", BOARD_SIZE_X, BOARD_SIZE_Y)

class Kami2Triangle:

    def __init__(self, p1, p2, p3, color):
        vertices = [p1, p2, p3]
        self.p1 = p1
        self.p2 = p2
        self.p3 = p3
        self.triangle = Polygon(vertices)
        self.hasBeenMarked = False
        self.color = color

        self.triangle.setFill(getColor()) # artistic color
        self.triangle.setOutline(FOLDING_COLOR)
        self.triangle.setWidth(1)

    def draw(self, window):
        self.triangle.draw(window)

    def undraw(self):
        self.triangle.undraw()

    def isPointInside(self, pt):
        b1 = sign(pt, self.p1, self.p2) < 0.0;
        b2 = sign(pt, self.p2, self.p3) < 0.0;
        b3 = sign(pt, self.p3, self.p1) < 0.0;

        return ((b1 == b2) and (b2 == b3));

    def setArtisticColor(self, color):
        self.triangle.setFill(color)

    def setInternalColor(self, color):
        self.color = color

    def getInternalColor(self):
        return self.color

    def getOrientation(self):
        print('o1')
        if self.p2.x > self.p1.x:
            print('o2')
            return ORIENTATION.RIGHT
        elif self.p2.x < self.p1.x:
            print('o3')
            return ORIENTATION.LEFT
        print('o4')
        return ORIENTATION.UNKNOWN

    def getCenterPoint(self):
        print('c1')
        x = 0
        y = self.p1.y + TRIANGLE_SIZE/2
        print('c2')
        if self.getOrientation() == ORIENTATION.LEFT:
            print('c3')
            x = self.p1.x - 1.0/3.0 * move_along_x
        elif self.getOrientation() == ORIENTATION.RIGHT:
            print('c4')
            x = self.p1.x + 1.0/3.0 * move_along_x
        print('c5')
        return Point(x, y)

def startToProcessTheBoard():
    print('Board has been processed')

    for triangle in triangles:
        if triangle.hasBeenMarked == False:
            internalColor = triangle.getInternalColor()
            q = [triangle]
            while len(q) > 0:
                currTriangle = q.pop()
                currTriangle.setArtisticColor(color_rgb(255, 255, 255))
                if currTriangle.hasBeenMarked == False:
                    neighbors = getNeighbors(currTriangle)
                    for neighbor in neighbors:
                        if internalColor == neighbor.getInternalColor():
                            q.append(neighbor)
                    currTriangle.hasBeenMarked = True

def on_press(key):
    global currentAction
    currentAction = key.char

lis = keyboard.Listener(on_press=on_press)
lis.start()

def sign(p1, p2, p3):
    return (p1.x - p3.x) * (p2.y - p3.y) - (p2.x - p3.x) * (p1.y - p3.y);

def drawRightTriangle(sp):
    p1 = sp
    p2 = Point(sp.x + move_along_x, sp.y + TRIANGLE_SIZE/2)
    p3 = Point(sp.x, sp.y + TRIANGLE_SIZE)

    triangle = Kami2Triangle(p1, p2, p3, currentAction)
    triangle.draw(win)
    
    return triangle

def drawLeftTriangle(sp):
    p1 = sp
    p2 = Point(sp.x - move_along_x, sp.y + TRIANGLE_SIZE/2)
    p3 = Point(sp.x, sp.y + TRIANGLE_SIZE)

    triangle = Kami2Triangle(p1, p2, p3, currentAction)
    triangle.draw(win)

    return triangle

startPosY = 0
while startPosY < BOARD_SIZE_Y - TRIANGLE_SIZE:
    startPosX = 0
    while startPosX + move_along_x <= BOARD_SIZE_X:
        triangles.append(drawRightTriangle(Point(startPosX, startPosY)))
        triangles.append(drawLeftTriangle(Point(startPosX + move_along_x*2, startPosY)))
        startPosX = startPosX + move_along_x*2
    startPosX = move_along_x
    startPosY = startPosY + TRIANGLE_SIZE/2
    while startPosX <= BOARD_SIZE_X:
        triangles.append(drawLeftTriangle(Point(startPosX, startPosY)))
        triangles.append(drawRightTriangle(Point(startPosX, startPosY)))
        startPosX = startPosX + move_along_x*2
    startPosY = startPosY + TRIANGLE_SIZE/2

while True:
    clickedPoint = win.getMouse()
    if currentAction == 's':
        startToProcessTheBoard()
    else:
        for triangle in triangles:
            if triangle.isPointInside(clickedPoint):
                if currentAction == 'u':
                    triangles.remove(triangle)
                    triangle.undraw()
                else:
                    triangle.setArtisticColor(getColor())
                    triangle.setInternalColor(currentAction)
