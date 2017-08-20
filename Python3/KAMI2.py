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

# Board set-up parameters
TRIANGLE_SIZE = 70
COLOR_PALLETE_SIZE = TRIANGLE_SIZE
NR_TRIANGLES_HORIZONTAL = 10
NR_TRIANGLES_VERTICAL = 14

move_along_x = math.sqrt(3)/2.0 * TRIANGLE_SIZE
BOARD_SIZE_X = move_along_x * NR_TRIANGLES_HORIZONTAL + COLOR_PALLETE_SIZE * 2
BOARD_SIZE_Y = TRIANGLE_SIZE * NR_TRIANGLES_VERTICAL
FOLDING_COLOR = color_rgb(70, 70, 70)
OUTPUT_FILE = "C:\\Users\\atataru\\Desktop\\output.txt"

window = GraphWin("KAMI 2 Puzzle Recreation Tool", BOARD_SIZE_X, BOARD_SIZE_Y)

names = ['a',
         'b',
         'c',
         'd',
         'e'
         ]

colors = [  color_rgb(192, 68, 56),
            color_rgb(196, 148, 66),
            color_rgb(51, 112, 113),
            color_rgb(212, 202, 175),
            color_rgb(210, 107, 63),
        ]

uiTriangles = []
uiErasedTriangles = []
uiButtons = []
uiPalettes = []
availableConnections = []

name2ColorDictionary = {}
color2IdDictionary = {}

currentColor = colors[3]
currentAction = ACTION.COLOR

for idx in range(0, len(names)):
    name2ColorDictionary[names[idx]] = colors[idx]

def getNeighbors(triangle):
    centerPoint = triangle.GetCenterPoint()
    n1 = centerPoint
    n2 = centerPoint
    n3 = centerPoint
    sign = 0;
    if triangle.GetOrientation() == ORIENTATION.LEFT:
        sign = 1
    elif triangle.GetOrientation() == ORIENTATION.RIGHT:
        sign = -1

    n1 = Point(centerPoint.x + 2 * (1.0/3.0 * move_along_x) * sign, centerPoint.y)
    n2 = Point(centerPoint.x - 1.0/3.0 * move_along_x * sign, centerPoint.y + TRIANGLE_SIZE/2 * sign)
    n3 = Point(centerPoint.x - 1.0/3.0 * move_along_x * sign, centerPoint.y - TRIANGLE_SIZE/2 * sign)

    neighbors = []
    for neighboardTriangle in uiTriangles:
        if neighboardTriangle.HasBeenTouched(n1) or neighboardTriangle.HasBeenTouched(n2) or neighboardTriangle.HasBeenTouched(n3):
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

    def Draw(self, window):
        self.square.draw(window)
        self.label.draw(window)

    def GetAction(self):
        return self.action

    def HasBeenTouched(self, pt):
        isHor = (pt.x >= self.p1.x and pt.x <= self.p2.x)
        isVer = (pt.y >= self.p2.y and  pt.y <= self.p3.y)
        return isHor and isVer;

class Kami2PalleteChooser:
    def __init__(self, p, size, color):
        self.p1 = p
        self.p2 = Point(p.x + size * 2, p.y)
        self.p3 = Point(p.x + size * 2, p.y + size * 1.5)
        self.p4 = Point(p.x, p.y + size * 1.5)
        vertices = [self.p1, self.p2, self.p3, self.p4]
        self.square = Polygon(vertices)
        self.color = color
        self.square.setFill(color)
        self.square.setOutline(color_rgb(0, 0, 0))
        self.square.setWidth(1)

    def Draw(self, window):
        self.square.draw(window)

    def HasBeenTouched(self, pt):
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

        self.label = Text(self.GetCenterPoint(), '')
        self.label.setSize(5)

    def getColorGroup(self):
        for idx in range(0, len(colors)):
            if(colors[idx] == self.color):
                return names[idx]
        return None

    def Draw(self, window):
        self.triangle.draw(window)
        self.label.draw(window)

    def Undraw(self):
        self.triangle.undraw()
        self.label.undraw()

    def HasBeenTouched(self, pt):
        b1 = sign(pt, self.p1, self.p2) < 0.0;
        b2 = sign(pt, self.p2, self.p3) < 0.0;
        b3 = sign(pt, self.p3, self.p1) < 0.0;

        return ((b1 == b2) and (b2 == b3));

    def SetColor(self, color):
        self.color = color
        self.triangle.setFill(color)

    def GetColor(self):
        return self.color

    def GetOrientation(self):
        if self.p2.x > self.p1.x:
            return ORIENTATION.RIGHT
        elif self.p2.x < self.p1.x:
            return ORIENTATION.LEFT
        return ORIENTATION.UNKNOWN

    def GetCenterPoint(self):
        x = 0
        y = self.p1.y + TRIANGLE_SIZE/2
        if self.GetOrientation() == ORIENTATION.LEFT:
            x = self.p1.x - 1.0/3.0 * move_along_x
        elif self.GetOrientation() == ORIENTATION.RIGHT:
            x = self.p1.x + 1.0/3.0 * move_along_x
        return Point(x, y)

    def ShowGroup(self):
        self.label.setText(self.group[0] + self.group[len(self.group) - 1])

    def Reset(self):
        self.color = getColor()
        self.triangle.setFill(self.color)
        
        self.label.setText('')
        self.hasBeenMarked = False

def makeConnection(group1, group2):
    connection = str(group1) + ' - ' + str(group2)
    if connection not in availableConnections:
        availableConnections.append(connection)

def writeDataToFile(data):
    file = open(OUTPUT_FILE, "w")
    file.write(data)
    file.close()

def startToProcessTheBoard():
    for triangle in uiTriangles:
        if triangle.hasBeenMarked == False:
            internalColor = triangle.GetColor()
            color2IdDictionary[triangle.getColorGroup()] += 1
            groupId = triangle.getColorGroup() + str(color2IdDictionary[triangle.getColorGroup()])
            triangle.group = groupId
            q = [triangle]
            while len(q) > 0:
                currTriangle = q.pop()
                currTriangle.group = groupId
                currTriangle.ShowGroup()

                if currTriangle.hasBeenMarked == False:
                    neighbors = getNeighbors(currTriangle)
                    for neighbor in neighbors:
                        if internalColor == neighbor.GetColor():
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
    triangle.Draw(window)
    
    return triangle

def drawGuidelineTriangle(startingPoint, orientation):
    side = TRIANGLE_SIZE / 2
    m_a_x = move_along_x / 2
    p1 = startingPoint
    if orientation == ORIENTATION.RIGHT:
        p2 = Point(startingPoint.x + m_a_x, startingPoint.y + side/2)
    else:
        p2 = Point(startingPoint.x - m_a_x, startingPoint.y + side/2)
    p3 = Point(startingPoint.x, startingPoint.y + side)

    window.create_polygon([p1.x, p1.y, p2.x, p2.y, p3.x, p3.y], dash=(1,), outline='gray', fill='', width=1)

def drawPuzzleGuidelines():

    side = TRIANGLE_SIZE / 2
    m_a_x = move_along_x / 2

    startPosY = -side
    headerPosX = 0

    while startPosY <= BOARD_SIZE_Y - side:
        startPosX = m_a_x
        while startPosX <= BOARD_SIZE_X - m_a_x - COLOR_PALLETE_SIZE * 2 - side:
            drawGuidelineTriangle(Point(startPosX, startPosY + side/2), ORIENTATION.RIGHT)
            drawGuidelineTriangle(Point(startPosX + m_a_x * 2, startPosY + side/2), ORIENTATION.LEFT)
            startPosX += m_a_x * 2
        startPosX = 0
        while startPosX <= BOARD_SIZE_X - m_a_x * 2 - COLOR_PALLETE_SIZE * 2:
            drawGuidelineTriangle(Point(startPosX, startPosY), ORIENTATION.LEFT)
            drawGuidelineTriangle(Point(startPosX, startPosY), ORIENTATION.RIGHT)
            startPosX += m_a_x * 2
            if startPosX >= BOARD_SIZE_X - m_a_x * 2 - COLOR_PALLETE_SIZE * 2:
                drawGuidelineTriangle(Point(startPosX, startPosY), ORIENTATION.LEFT)
        startPosY += side

def drawBoardForFirstTime():
    for color in names:
        color2IdDictionary[color] = 0

    startPosY = 0
    headerPosX = 0
    while headerPosX <= BOARD_SIZE_X - move_along_x * 2 - COLOR_PALLETE_SIZE * 2:
        uiTriangles.append(drawTriangle(Point(headerPosX, startPosY - TRIANGLE_SIZE/2), ORIENTATION.RIGHT))
        uiTriangles.append(drawTriangle(Point(headerPosX + move_along_x * 2, startPosY - TRIANGLE_SIZE/2), ORIENTATION.LEFT))
        headerPosX += move_along_x * 2

    while startPosY <= BOARD_SIZE_Y - TRIANGLE_SIZE:
        startPosX = move_along_x
        while startPosX <= BOARD_SIZE_X - move_along_x - COLOR_PALLETE_SIZE * 2:
            uiTriangles.append(drawTriangle(Point(startPosX, startPosY), ORIENTATION.LEFT))
            uiTriangles.append(drawTriangle(Point(startPosX, startPosY), ORIENTATION.RIGHT))
            startPosX += move_along_x * 2
        startPosX = 0
        while startPosX <= BOARD_SIZE_X - move_along_x * 2 - COLOR_PALLETE_SIZE * 2:
            uiTriangles.append(drawTriangle(Point(startPosX, startPosY + TRIANGLE_SIZE/2), ORIENTATION.RIGHT))
            uiTriangles.append(drawTriangle(Point(startPosX + move_along_x * 2, startPosY + TRIANGLE_SIZE/2), ORIENTATION.LEFT))
            startPosX += move_along_x * 2
        startPosY += TRIANGLE_SIZE

def clearBoard():
    global color2IdDictionary
    for color in names:
        color2IdDictionary[color] = 0

    global currentAction
    currentAction = ACTION.COLOR

    for triangle in uiErasedTriangles:
        uiTriangles.append(triangle)

    for triangle in uiTriangles:
        triangle.Reset()

    for triangle in uiErasedTriangles:
        triangle.Draw(window)
    uiErasedTriangles.clear()

def setCurrentActionAsUndraw():
    global currentAction
    currentAction = ACTION.UNDRAW

def executionLoop():
    while True:
        clickedPoint = window.getMouse()
        for button in uiButtons:
            if button.HasBeenTouched(clickedPoint):
                if button.GetAction() == ACTION.CLEAR:
                    clearBoard()
                elif button.GetAction() == ACTION.PROCESS:
                    startToProcessTheBoard()
                elif button.GetAction() == ACTION.UNDRAW:
                    setCurrentActionAsUndraw()
        for pallete in uiPalettes:
            if pallete.HasBeenTouched(clickedPoint):
                global currentColor
                currentColor = pallete.color
                global currentAction
                currentAction = ACTION.COLOR
        for triangle in uiTriangles:
            if triangle.HasBeenTouched(clickedPoint):
                if currentAction == ACTION.UNDRAW:
                    uiTriangles.remove(triangle)
                    uiErasedTriangles.append(triangle)
                    triangle.Undraw()
                else:
                    triangle.SetColor(getColor())

def drawColorPalleteUI():
    colorPalleteX = BOARD_SIZE_X - COLOR_PALLETE_SIZE * 2
    colorPalleteY = 0

    for colorIdx in range(0, len(colors)):
        zone = Kami2PalleteChooser(Point(colorPalleteX, colorPalleteY), COLOR_PALLETE_SIZE, colors[colorIdx])
        zone.Draw(window)
        uiPalettes.append(zone)
        colorPalleteY += COLOR_PALLETE_SIZE * 1.5

def drawMenuButtonsUI():
    BUTTON_WIDTH = COLOR_PALLETE_SIZE * 2 - 10
    BUTTON_HEIGHT = 50
    button = Kami2Button(Point(BOARD_SIZE_X - COLOR_PALLETE_SIZE * 2 + 5, BOARD_SIZE_Y - 50), BUTTON_WIDTH, BUTTON_HEIGHT, 'Process', ACTION.PROCESS)
    uiButtons.append(button)
    button.Draw(window)
    button = Kami2Button(Point(BOARD_SIZE_X - COLOR_PALLETE_SIZE * 2 + 5, BOARD_SIZE_Y - 55 - BUTTON_HEIGHT), BUTTON_WIDTH, BUTTON_HEIGHT, 'Clear', ACTION.CLEAR)
    uiButtons.append(button)
    button.Draw(window)
    button = Kami2Button(Point(BOARD_SIZE_X - COLOR_PALLETE_SIZE * 2 + 5, BOARD_SIZE_Y - 60 - BUTTON_HEIGHT * 2), BUTTON_WIDTH, BUTTON_HEIGHT, 'Undraw', ACTION.UNDRAW)
    uiButtons.append(button)
    button.Draw(window)

if __name__ == "__main__":
    drawPuzzleGuidelines()
    drawColorPalleteUI()
    drawMenuButtonsUI()
    drawBoardForFirstTime()
    executionLoop()
