from graphics import *
from pynput import keyboard
from enum import Enum
import math
import random

class ORIENTATION(Enum):
    LEFT = 1
    RIGHT = 2
    UNKNOWN = 3

class ACTION(Enum):
    COLOR = 1
    CLEAR = 2
    UNDRAW = 3
    PROCESS = 4

currentAction = ACTION.COLOR

# Board set-up parameters
TRIANGLE_SIZE = 70
COLOR_PALLETE_SIZE = 105
NR_TRIANGLES_HORIZONTAL = 10
NR_TRIANGLES_VERTICAL = 14

move_along_x = math.sqrt(3)/2.0 * TRIANGLE_SIZE
BOARD_SIZE_X = move_along_x * NR_TRIANGLES_HORIZONTAL + COLOR_PALLETE_SIZE * 2
BOARD_SIZE_Y = TRIANGLE_SIZE * NR_TRIANGLES_VERTICAL
FOLDING_COLOR = color_rgb(70, 70, 70)
OUTPUT_FILE = "C:\\Users\\atataru\\Desktop\\output.txt"

window = GraphWin("KAMI2", BOARD_SIZE_X, BOARD_SIZE_Y)

names = ['DarkRed',
         'Yallow',
         'Blue',
         'PaperGrey',
         'Orange',
         'DarkBlue',
         'Pink',
         'LightBlue',
         'DarkGrey',
         'Burgundy']

colors = [  color_rgb(192, 68, 56),
            color_rgb(196, 148, 66),
            color_rgb(51, 112, 113),
            color_rgb(212, 202, 175),
            color_rgb(210, 107, 63),
            color_rgb(36, 65, 70),
            color_rgb(157, 51, 73),
            color_rgb(157, 232, 195),
            color_rgb(102, 51, 0),
            color_rgb(101, 28, 48)
        ]

colorDictionary = {}
for idx in range(0, len(names)):
    colorDictionary[names[idx]] = colors[idx]

currentColor = colors[3]

triangles = []
uiButtons = []

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
    global currentColor
    return currentColor

class Kami2Button:
    def __init__(self, p, width, height, text, action):
        self.action = action
        self.p1 = p
        self.p2 = Point(p.x + width, p.y)
        self.p3 = Point(p.x + width, p.y + height)
        self.p4 = Point(p.x, p.y + height)
        vertices = [self.p1, self.p2, self.p3, self.p4]
        self.square = Polygon(vertices)
        self.square.setOutline(color_rgb(0, 0, 0));

        self.label = Text(Point(p.x + width/2, p.y + height / 2), text)
        self.label.setFace('courier')
        self.label.setSize(16)
        self.label.setWidth(width)

    def draw(self, window):
        self.square.draw(window)
        self.label.draw(window)

    def getAction(self):
        return self.action

    def isPointInside(self, pt):
        isHor = (pt.x >= self.p1.x and pt.x <= self.p2.x)
        isVer = (pt.y >= self.p2.y and  pt.y <= self.p3.y)
        return isHor and isVer;

class Kami2PalleteChooser:
    def __init__(self, p, size, color):
        self.p1 = p
        self.p2 = Point(p.x + size, p.y)
        self.p3 = Point(p.x + size, p.y + size)
        self.p4 = Point(p.x, p.y + size)
        vertices = [self.p1, self.p2, self.p3, self.p4]
        self.square = Polygon(vertices)
        self.color = color
        self.square.setFill(color)
        self.square.setOutline(color_rgb(0, 0, 0))
        self.square.setWidth(1)

    def draw(self, window):
        self.square.draw(window)

    def isPointInside(self, pt):
        isHor = (pt.x >= self.p1.x and pt.x <= self.p2.x)
        isVer = (pt.y >= self.p2.y and  pt.y <= self.p3.y)
        return isHor and isVer;

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

        self.triangle.setFill(color) # artistic color
        self.triangle.setOutline(FOLDING_COLOR)
        self.triangle.setWidth(1)

        self.label = Text(self.getCenterPoint(), '')
        self.label.setSize(5)

    def getColorGroup(self):
        for idx in range(0, len(colors)):
            if(colors[idx] == self.color):
                return names[idx]
        return None

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

    def setColor(self, color):
        self.color = color
        self.triangle.setFill(color)

    def getColor(self):
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
        self.label.setText(self.group[0] + self.group[len(self.group) - 1])

    def clearTriangle(self):
        self.color = getColor()
        self.triangle.setFill(self.color)
        self.label.setText('')
        self.hasBeenMarked = False

availableConnections = []

def makeConnection(group1, group2):
    connection = str(group1) + ' - ' + str(group2)
    if connection not in availableConnections:
        availableConnections.append(connection)

def writeDataToFile(data):
    file = open(OUTPUT_FILE, "w")
    file.write(data)
    file.close()

groupIdx = {}
for color in names:
    groupIdx[color] = 0

def startToProcessTheBoard():
    for triangle in triangles:
        if triangle.hasBeenMarked == False:
            internalColor = triangle.getColor()
            groupIdx[triangle.getColorGroup()] += 1
            groupId = triangle.getColorGroup() + str(groupIdx[triangle.getColorGroup()])
            triangle.group = groupId
            q = [triangle]
            while len(q) > 0:
                currTriangle = q.pop()
                currTriangle.group = groupId
                currTriangle.displayBelongingGroup()

                if currTriangle.hasBeenMarked == False:
                    neighbors = getNeighbors(currTriangle)
                    for neighbor in neighbors:
                        if internalColor == neighbor.getColor():
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

    triangle = Kami2Triangle(p1, p2, p3, getColor())
    triangle.draw(window)
    
    return triangle

def drawBoardForFirstTime():
    startPosY = 0
    headerPosX = 0
    while headerPosX <= BOARD_SIZE_X - move_along_x * 2 - COLOR_PALLETE_SIZE * 2:
        triangles.append(drawTriangle(Point(headerPosX, startPosY - TRIANGLE_SIZE/2), ORIENTATION.RIGHT))
        triangles.append(drawTriangle(Point(headerPosX + move_along_x * 2, startPosY - TRIANGLE_SIZE/2), ORIENTATION.LEFT))
        headerPosX += move_along_x * 2

    while startPosY <= BOARD_SIZE_Y - TRIANGLE_SIZE:
        startPosX = move_along_x
        while startPosX <= BOARD_SIZE_X - move_along_x - COLOR_PALLETE_SIZE * 2:
            triangles.append(drawTriangle(Point(startPosX, startPosY), ORIENTATION.LEFT))
            triangles.append(drawTriangle(Point(startPosX, startPosY), ORIENTATION.RIGHT))
            startPosX += move_along_x * 2
        startPosX = 0
        while startPosX <= BOARD_SIZE_X - move_along_x * 2 - COLOR_PALLETE_SIZE * 2:
            triangles.append(drawTriangle(Point(startPosX, startPosY + TRIANGLE_SIZE/2), ORIENTATION.RIGHT))
            triangles.append(drawTriangle(Point(startPosX + move_along_x * 2, startPosY + TRIANGLE_SIZE/2), ORIENTATION.LEFT))
            startPosX += move_along_x * 2
        startPosY += TRIANGLE_SIZE

def clearBoard():
    global groupIdx
    for color in names:
        groupIdx[color] = 0

    global currentAction
    currentAction = ACTION.COLOR

    for triangle in triangles:
        triangle.clearTriangle()

palleteChooserZones = []

def setCurrentActionAsUndraw():
    global currentAction
    currentAction = ACTION.UNDRAW

def executionLoop():
    while True:
        clickedPoint = window.getMouse()
        for button in uiButtons:
            if button.isPointInside(clickedPoint):
                if button.getAction() == ACTION.CLEAR:
                    clearBoard()
                elif button.getAction() == ACTION.PROCESS:
                    startToProcessTheBoard()
                elif button.getAction() == ACTION.UNDRAW:
                    setCurrentActionAsUndraw()
        for pallete in palleteChooserZones:
            if pallete.isPointInside(clickedPoint):
                global currentColor
                currentColor = pallete.color
                global currentAction
                currentAction = ACTION.COLOR
        for triangle in triangles:
            if triangle.isPointInside(clickedPoint):
                if currentAction == ACTION.UNDRAW:
                    triangles.remove(triangle)
                    triangle.undraw()
                else:
                    triangle.setColor(getColor())

def drawColorPalleteUI():
    colorPalleteX = BOARD_SIZE_X - COLOR_PALLETE_SIZE * 2
    colorPalleteY = 0

    for colorIdx in range(0, len(colors)):
        zone = Kami2PalleteChooser(Point(colorPalleteX, colorPalleteY), COLOR_PALLETE_SIZE, colors[colorIdx])
        zone.draw(window)
        palleteChooserZones.append(zone)
        colorPalleteX += COLOR_PALLETE_SIZE
        if colorPalleteX == BOARD_SIZE_X:
            colorPalleteX -= COLOR_PALLETE_SIZE * 2
            colorPalleteY += COLOR_PALLETE_SIZE

def drawMenuButtonsUI():
    BUTTON_WIDTH = COLOR_PALLETE_SIZE * 2 - 10
    BUTTON_HEIGHT = 50
    button = Kami2Button(Point(BOARD_SIZE_X - COLOR_PALLETE_SIZE * 2 + 5, BOARD_SIZE_Y - 50), BUTTON_WIDTH, BUTTON_HEIGHT, 'Process', ACTION.PROCESS)
    uiButtons.append(button)
    button.draw(window)
    button = Kami2Button(Point(BOARD_SIZE_X - COLOR_PALLETE_SIZE * 2 + 5, BOARD_SIZE_Y - 55 - BUTTON_HEIGHT), BUTTON_WIDTH, BUTTON_HEIGHT, 'Clear', ACTION.CLEAR)
    uiButtons.append(button)
    button.draw(window)
    button = Kami2Button(Point(BOARD_SIZE_X - COLOR_PALLETE_SIZE * 2 + 5, BOARD_SIZE_Y - 60 - BUTTON_HEIGHT * 2), BUTTON_WIDTH, BUTTON_HEIGHT, 'Undraw', ACTION.UNDRAW)
    uiButtons.append(button)
    button.draw(window)

if __name__ == "__main__":
    drawColorPalleteUI()
    drawMenuButtonsUI()
    drawBoardForFirstTime()
    executionLoop()
