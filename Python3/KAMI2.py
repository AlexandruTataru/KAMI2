from graphics import *
from pynput import keyboard
from enum import Enum
import math
import random

class ORIENTATION(Enum):
    LEFT = 1
    RIGHT = 2
    UNKNOWN = 3

# Board set-up parameters
TRIANGLE_SIZE = 60
NR_TRIANGLES_HORIZONTAL = 10
NR_TRIANGLES_VERTICAL = 14

TEXT_AREA_WIDTH = 200
CHAR_WIDTH = 5

move_along_x = math.sqrt(3)/2.0 * TRIANGLE_SIZE
BOARD_SIZE_X = move_along_x * NR_TRIANGLES_HORIZONTAL + TEXT_AREA_WIDTH + 1
BOARD_SIZE_Y = TRIANGLE_SIZE * NR_TRIANGLES_VERTICAL
FOLDING_COLOR = color_rgb(50, 50, 50)
OUTPUT_FILE = "C:\\Users\\alexandruflavian.ta\\Desktop\\output.txt"

window = GraphWin("KAMI2", BOARD_SIZE_X, BOARD_SIZE_Y)

def addLeftAllignedText(text, y):
    size = len(text)
    offset = TEXT_AREA_WIDTH/2 - size * CHAR_WIDTH
    instruction = Text(Point(TEXT_AREA_WIDTH/2 - offset + 5, y), text)
    instruction.setFace('courier')
    instruction.setWidth(TEXT_AREA_WIDTH)
    instruction.draw(window)

scanline = 20
addLeftAllignedText("Available colors:", scanline)
scanline += 20
addLeftAllignedText("0. Dark Red", scanline)
scanline += 20
addLeftAllignedText("1. Yellow", scanline)
scanline += 20
addLeftAllignedText("2. Blue", scanline)
scanline += 20
addLeftAllignedText("3. Paper Grey", scanline)
scanline += 20
addLeftAllignedText("4. Orange", scanline)
scanline += 20
addLeftAllignedText("5. Dark Blue", scanline)
scanline += 20
addLeftAllignedText("6. Pink", scanline)
scanline += 20
addLeftAllignedText("7. Light Blue", scanline)
scanline += 20
addLeftAllignedText("8. Dark Grey", scanline)
scanline += 20
addLeftAllignedText("9. Burgundy", scanline)
scanline += 20
addLeftAllignedText("", scanline)
scanline += 20
addLeftAllignedText("Available actions:", scanline)
scanline += 20
addLeftAllignedText("u. Undraw triangle", scanline)
scanline += 20
addLeftAllignedText("c. Clear drawing", scanline)
scanline += 20
addLeftAllignedText("s. Output graph", scanline)
scanline += 20

groupIdx = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

BOARD_STARTING_COLOR_SELECTION = '3'

currentAction = BOARD_STARTING_COLOR_SELECTION

def on_press(key):
    global currentAction
    currentAction = key.char

lis = keyboard.Listener(on_press=on_press)
lis.start()

triangles = []

def getNeighbors(triangle):
    centerPoint = triangle.getCenterPoint()
    n1 = centerPoint
    n2 = centerPoint
    n3 = centerPoint
    sign = 0;
    if triangle.getOrientation() == ORIENTATION.LEFT:
        sign = 1
    elif triangle.getOrientation() == ORIENTATION.RIGHT:
        sign = -1

    n1 = Point(centerPoint.x + 2 * (1.0/3.0 * move_along_x) * sign, centerPoint.y)
    n2 = Point(centerPoint.x - 1.0/3.0 * move_along_x * sign, centerPoint.y + TRIANGLE_SIZE/2 * sign)
    n3 = Point(centerPoint.x - 1.0/3.0 * move_along_x * sign, centerPoint.y - TRIANGLE_SIZE/2 * sign)

    neighbors = []
    for neighboardTriangle in triangles:
        if neighboardTriangle.isPointInside(n1) or neighboardTriangle.isPointInside(n2) or neighboardTriangle.isPointInside(n3):
                neighbors.append(neighboardTriangle)

    return neighbors

def getColor():
    colors = [  color_rgb(192, 68, 56),   # Dark Red
                color_rgb(196, 148, 66),  # Yellow
                color_rgb(51, 112, 113),  # Blue
                color_rgb(212, 202, 175), # Paper Grey
                color_rgb(210, 107, 63),  # Orange
                color_rgb(36, 65, 70),    # Dark Blue
                color_rgb(157, 51, 73),   # Pink
                color_rgb(157, 232, 195), # Light Blue
                color_rgb(102, 51, 0),    # Dark Grey
                color_rgb(101, 28, 48)    # Burgundy
            ]

    return colors[int(currentAction)]

class Kami2Triangle:

    def __init__(self, p1, p2, p3, color):
        self.group = None
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

        self.label = Text(self.getCenterPoint(), '')
        self.label.setSize(5)

    def getColorGroup(self):
        colorGroups = ['DarkRed', 'Yellow', 'Blue', 'PaperGrey', 'Orange', 'DarkBlue', 'Pink', 'LightBlue', 'DarkGrey', 'Burgundy']
        return colorGroups[int(self.color)]

    def draw(self, window):
        self.triangle.draw(window)
        self.label.draw(window)

    def undraw(self):
        self.triangle.undraw()
        self.label.undraw()

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
        if self.p2.x > self.p1.x:
            return ORIENTATION.RIGHT
        elif self.p2.x < self.p1.x:
            return ORIENTATION.LEFT
        return ORIENTATION.UNKNOWN

    def getCenterPoint(self):
        x = 0
        y = self.p1.y + TRIANGLE_SIZE/2
        if self.getOrientation() == ORIENTATION.LEFT:
            x = self.p1.x - 1.0/3.0 * move_along_x
        elif self.getOrientation() == ORIENTATION.RIGHT:
            x = self.p1.x + 1.0/3.0 * move_along_x
        return Point(x, y)

    def displayBelongingGroup(self):
        self.label.setText( self.group[0] + self.group[len(self.group) - 1])

availableConnections = []

def makeConnection(group1, group2):
    connection = str(group1) + ' - ' + str(group2)
    if connection not in availableConnections:
        availableConnections.append(connection)

def writeDataToFile(data):
    file = open(OUTPUT_FILE, "w")
    file.write(data)
    file.close()

def startToProcessTheBoard():
    for triangle in triangles:
        if triangle.hasBeenMarked == False:
            internalColor = triangle.getInternalColor()
            groupIdx[int(internalColor)] = groupIdx[int(internalColor)] + 1
            groupId = triangle.getColorGroup() + str(groupIdx[int(internalColor)])
            triangle.group = groupId
            q = [triangle]
            while len(q) > 0:
                currTriangle = q.pop()
                currTriangle.group = groupId
                currTriangle.displayBelongingGroup()

                if currTriangle.hasBeenMarked == False:
                    neighbors = getNeighbors(currTriangle)
                    for neighbor in neighbors:
                        if internalColor == neighbor.getInternalColor():
                            q.append(neighbor)
                        elif neighbor.hasBeenMarked == True and neighbor.group != None:
                            makeConnection(currTriangle.group, neighbor.group)
                    currTriangle.hasBeenMarked = True

    data = ''
    for conn in availableConnections:
        data = data + conn + '\n'
    writeDataToFile(data)

def sign(p1, p2, p3):
    return (p1.x - p3.x) * (p2.y - p3.y) - (p2.x - p3.x) * (p1.y - p3.y);

def drawTriangle(startingPoint, orientation):
    p1 = startingPoint
    if orientation == ORIENTATION.RIGHT:
        p2 = Point(startingPoint.x + move_along_x, startingPoint.y + TRIANGLE_SIZE/2)
    else:
        p2 = Point(startingPoint.x - move_along_x, startingPoint.y + TRIANGLE_SIZE/2)
    p3 = Point(startingPoint.x, startingPoint.y + TRIANGLE_SIZE)

    triangle = Kami2Triangle(p1, p2, p3, currentAction)
    triangle.draw(window)
    
    return triangle

def clearBoardAndRedrawEverything():
    global groupIdx
    for i in range(0, len(groupIdx)):
        groupIdx[i] = 0

    global currentAction
    currentAction = BOARD_STARTING_COLOR_SELECTION

    for triangle in triangles:
        triangle.undraw()

    startPosY = 0
    headerPosX = TEXT_AREA_WIDTH
    while headerPosX <= BOARD_SIZE_X - move_along_x * 2:
        triangles.append(drawTriangle(Point(headerPosX, startPosY - TRIANGLE_SIZE/2), ORIENTATION.RIGHT))
        triangles.append(drawTriangle(Point(headerPosX + move_along_x * 2, startPosY - TRIANGLE_SIZE/2), ORIENTATION.LEFT))
        headerPosX += move_along_x * 2

    while startPosY <= BOARD_SIZE_Y - TRIANGLE_SIZE:
        startPosX = move_along_x + TEXT_AREA_WIDTH
        while startPosX <= BOARD_SIZE_X - move_along_x:
            triangles.append(drawTriangle(Point(startPosX, startPosY), ORIENTATION.LEFT))
            triangles.append(drawTriangle(Point(startPosX, startPosY), ORIENTATION.RIGHT))
            startPosX += move_along_x * 2
        startPosX = TEXT_AREA_WIDTH
        while startPosX <= BOARD_SIZE_X - move_along_x * 2:
            triangles.append(drawTriangle(Point(startPosX, startPosY + TRIANGLE_SIZE/2), ORIENTATION.RIGHT))
            triangles.append(drawTriangle(Point(startPosX + move_along_x * 2, startPosY + TRIANGLE_SIZE/2), ORIENTATION.LEFT))
            startPosX += move_along_x * 2
        startPosY += TRIANGLE_SIZE

def executionLoop():
    while True:
        clickedPoint = window.getMouse()
        if currentAction == 's':
            startToProcessTheBoard()
        if currentAction == 'c':
            clearBoardAndRedrawEverything()
        else:
            for triangle in triangles:
                if triangle.isPointInside(clickedPoint):
                    if currentAction == 'u':
                        triangles.remove(triangle)
                        triangle.undraw()
                    else:
                        triangle.setArtisticColor(getColor())
                        triangle.setInternalColor(currentAction)

if __name__ == "__main__":
    clearBoardAndRedrawEverything()
    executionLoop()
