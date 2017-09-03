from graphics import *
from pynput import keyboard
from threading import Thread
from enum import Enum
import math
import random
import time
import json
from pprint import pprint

class ORIENTATION(Enum):
    LEFT = 1
    RIGHT = 2
    UNKNOWN = 3

class ACTION(Enum):
    COLOR = 1
    CLEAR = 2
    UNDRAW = 3
    PROCESS = 4
    SAVE = 5
    LOAD = 6
    SWITCH_MODE= 7

class PALLETE_COLOR(Enum):
    COLOR1 = 0
    COLOR2 = 1
    COLOR3 = 2
    COLOR4 = 3
    COLOR5 = 4

class STATE(Enum):
    COLOR = 0
    NORMAL = 1

class MODE(Enum):
    PLAY = 0
    DEV = 1

currentState = STATE.NORMAL
currentMode = MODE.DEV

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
SERIALIZED_OUTPUT_FILE = "C:\\Users\\atataru\\Desktop\\saved_level.txt"

window = GraphWin("KAMI 2 Puzzle Recreation Tool", BOARD_SIZE_X, BOARD_SIZE_Y)

def motion(event):
    if currentState == STATE.COLOR:
        clickedPoint = Point(event.x, event.y)
        
        for triangle in uiTriangles:
            if triangle.HasBeenTouched(clickedPoint):
                if currentAction == ACTION.UNDRAW:
                    triangle.Undraw()
                else:
                    if not triangle.IsVisible():
                        triangle.Draw(window)
                    triangle.SetColor(currentColor)

window.bind('<Motion>', motion)

colorPalletes = [ ['#dcd1bf','#74b9c1','#43717c','#8f2b40','#bc993e'],
                  ['#2f302c','#e3d0af','#418e76','#a43535','#7b7b78'],
                  ['#c2763a','#d2ae3a','#7d9637','#324826','#8bb1b3'],
                  ['#d4d2c5','#223d61','#cda947','#59152c','#487076'],
                  ['#42382f','#aa4c31','#83b4b0','#ac7f3f','#b4a696'],
                  ['#1b3238','#647e46','#bfad78','#4a807c','#5d3f29'],
                  ['#2f302c','#bc517a','#5aacb7','#c6b257','#c8c9c5'],
                  ['#e3c8bd','#de9b4e','#c9536f','#832544','#311c49']]

names = ['A','B','C','D','E']

colors = colorPalletes[0]

uiTriangles = []
uiButtons = []
uiPalettes = []
transparencyPallete = []
availableConnections = []

name2ColorDictionary = {}
color2IdDictionary = {}

neighbordsMap = {}

currentColor = 0
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

def getColorWithIndex(idx):
    return colors[int(idx)]

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

    def SetText(self, text):
        self.label.setText(text)

class Kami2PalleteChooser:
    def __init__(self, p, size, palleteColorIndex):
        self.p1 = p
        self.p2 = Point(p.x + size * 2, p.y)
        self.p3 = Point(p.x + size * 2, p.y + size * 1.5)
        self.p4 = Point(p.x, p.y + size * 1.5)
        vertices = [self.p1, self.p2, self.p3, self.p4]
        self.square = Polygon(vertices)
        self.colorIndex = palleteColorIndex
        self.square.setFill(getColorWithIndex(self.colorIndex))
        self.square.setOutline(color_rgb(0, 0, 0))
        self.square.setWidth(1)

        self.bookmark1 = Polygon([p, Point(p.x + size/3, p.y), Point(p.x, p.y + size/3)])
        self.bookmark1.setOutline(color_rgb(0, 0, 0));
        self.bookmark1.setFill('white')
        self.bookmark1.setWidth(1)

        self.bookmark2 = Polygon([Point(p.x + size/3, p.y), Point(p.x + size/3, p.y + size/3), Point(p.x, p.y + size/3)])
        self.bookmark2.setOutline(color_rgb(0, 0, 0));
        self.bookmark2.setFill('lightgrey')
        self.bookmark2.setWidth(1)

    def Draw(self, window):
        self.square.draw(window)

    def RefreshColor(self):
        self.square.setFill(getColorWithIndex(self.colorIndex))

    def HasBeenTouched(self, pt):
        isHor = (pt.x >= self.p1.x and pt.x <= self.p2.x)
        isVer = (pt.y >= self.p2.y and  pt.y <= self.p3.y)
        return isHor and isVer;

    def SetSelected(self, selected, window):
        if selected == True:
            self.bookmark1.draw(window)
            self.bookmark2.draw(window)
        elif selected == False:
            self.bookmark1.undraw()
            self.bookmark2.undraw()

    def SetFill(self, fill):
        self.square.setFill(fill)

class Kami2Triangle:

    def __init__(self, p1, p2, p3, palleteColorIndex):
        self.group = None
        self.isVisible = True
        vertices = [p1, p2, p3]
        self.p1 = p1
        self.p2 = p2
        self.p3 = p3
        self.triangle = Polygon(vertices)
        self.hasBeenMarked = False
        self.colorIndex = palleteColorIndex

        self.triangle.setFill(getColorWithIndex(self.colorIndex)) # artistic color
        self.triangle.setOutline(FOLDING_COLOR)
        self.triangle.setWidth(1)

        self.label = Text(self.GetCenterPoint(), '')
        self.label.setSize(14)
        self.label.setWidth(300)
        self.label.setFace('courier')

    def SetColor(self, colorPalleteIndex):
        self.colorIndex = colorPalleteIndex
        self.triangle.setFill(getColorWithIndex(self.colorIndex))

    def RefreshColor(self):
        self.triangle.setFill(getColorWithIndex(self.colorIndex))

    def getColorGroup(self):
        return names[self.colorIndex]

    def Draw(self, window):
        self.triangle.draw(window)
        self.label.draw(window)
        self.isVisible = True

    def Undraw(self):
        self.triangle.undraw()
        self.label.undraw()
        self.isVisible = False

    def IsVisible(self):
        return self.isVisible

    def HasBeenTouched(self, pt):
        b1 = sign(pt, self.p1, self.p2) < 0.0;
        b2 = sign(pt, self.p2, self.p3) < 0.0;
        b3 = sign(pt, self.p3, self.p1) < 0.0;

        return ((b1 == b2) and (b2 == b3));

    def GetColor(self):
        return getColorWithIndex(self.colorIndex)

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
        self.label.setText(self.group)

    def Reset(self):
        self.colorIndex = currentColor
        self.triangle.setFill(getColorWithIndex(currentColor))
        
        if not self.isVisible:
            self.isVisible = True
            self.Draw(window)

        self.label.setText('')
        self.hasBeenMarked = False

    def getUniqueID(self):
        return str(self.p1.x) + str(self.p1.y) + str(self.p2.x) + str(self.p2.y) + str(self.p3.x) + str(self.p3.y)

    def serialize(self):
        data = {}
        data['isVisible'] = self.isVisible
        data['colorIndex'] = self.colorIndex
        return json.dumps(data)

    def unserialize(self, jsonContent):
        data = json.loads(jsonContent)
        visible = bool(data['isVisible'])
        self.colorIndex = int(data['colorIndex'])
        self.RefreshColor()
        if self.isVisible:
            if not visible:
                self.isVisible = False
                self.Undraw()

def makeConnection(group1, group2):
    connection = str(group1) + ' - ' + str(group2)
    if connection not in availableConnections:
        availableConnections.append(connection)

def writeDataToFile(locationOnDisk, data):
    file = open(locationOnDisk, "w")
    file.write(data)
    file.close()

def startToProcessTheBoard():
    for triangle in uiTriangles:
        if triangle.hasBeenMarked == False and triangle.IsVisible():
            internalColor = triangle.GetColor()
            color2IdDictionary[triangle.getColorGroup()] += 1
            groupId = triangle.getColorGroup() + str(color2IdDictionary[triangle.getColorGroup()])
            triangle.group = groupId
            q = [triangle]
            qSecond = []
            while len(q) > 0:
                currTriangle = q.pop()
                currTriangle.group = groupId
                currTriangle.ShowGroup()

                if currTriangle.hasBeenMarked == False:
                    #neighbors = getNeighbors(currTriangle)
                    neighbors = neighbordsMap[currTriangle.getUniqueID()]
                    for neighbor in neighbors:
                        if not neighbor.IsVisible():
                            continue
                        if internalColor == neighbor.GetColor():
                            qSecond.append(neighbor)
                        elif neighbor.hasBeenMarked == True and neighbor.group != None:
                            makeConnection(currTriangle.group, neighbor.group)
                    currTriangle.hasBeenMarked = True

                if len(q) == 0:
                    for g in qSecond:
                        q.append(g)
                    qSecond.clear()

    data = ''
    for conn in availableConnections:
        data = data + conn + '\n'
    writeDataToFile(OUTPUT_FILE, data)

def sign(p1, p2, p3):
    return (p1.x - p3.x) * (p2.y - p3.y) - (p2.x - p3.x) * (p1.y - p3.y);

def drawTriangle(startingPoint, orientation):
    p1 = startingPoint
    if orientation == ORIENTATION.RIGHT:
        p2 = Point(startingPoint.x + move_along_x, startingPoint.y + TRIANGLE_SIZE/2)
    else:
        p2 = Point(startingPoint.x - move_along_x, startingPoint.y + TRIANGLE_SIZE/2)
    p3 = Point(startingPoint.x, startingPoint.y + TRIANGLE_SIZE)

    triangle = Kami2Triangle(p1, p2, p3, currentColor)
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

    for triangle in uiTriangles:
        triangle.Reset()

def setCurrentActionAsUndraw():
    global currentAction
    currentAction = ACTION.UNDRAW

def drawColorPalleteUI():
    colorPalleteX = BOARD_SIZE_X - COLOR_PALLETE_SIZE * 2
    colorPalleteY = 0

    for colorIdx in range(0, len(colors)):
        zone = Kami2PalleteChooser(Point(colorPalleteX, colorPalleteY), COLOR_PALLETE_SIZE, colorIdx)
        zone.Draw(window)
        uiPalettes.append(zone)
        colorPalleteY += COLOR_PALLETE_SIZE * 1.5
    zone = Kami2PalleteChooser(Point(colorPalleteX, colorPalleteY), COLOR_PALLETE_SIZE, colorIdx)
    zone.SetFill('')
    zone.Draw(window)
    transparencyPallete.append(zone)
    uiPalettes[0].SetSelected(True, window)

    side = TRIANGLE_SIZE / 2
    m_a_x = move_along_x / 2

    startPosX = colorPalleteX
    startPosY = colorPalleteY

    while startPosX < BOARD_SIZE_X - m_a_x - side:
        drawGuidelineTriangle(Point(startPosX, startPosY), ORIENTATION.RIGHT)
        drawGuidelineTriangle(Point(startPosX + m_a_x * 2, startPosY), ORIENTATION.LEFT)
        startPosX += m_a_x * 2
    drawGuidelineTriangle(Point(startPosX, startPosY), ORIENTATION.RIGHT)

    startPosX = colorPalleteX
    startPosY += side
    while startPosX < BOARD_SIZE_X - m_a_x - side:
        drawGuidelineTriangle(Point(startPosX, startPosY), ORIENTATION.RIGHT)
        drawGuidelineTriangle(Point(startPosX + m_a_x * 2, startPosY), ORIENTATION.LEFT)
        startPosX += m_a_x * 2
    drawGuidelineTriangle(Point(startPosX, startPosY), ORIENTATION.RIGHT)

    startPosX = colorPalleteX
    startPosY += side
    while startPosX < BOARD_SIZE_X - m_a_x - side:
        drawGuidelineTriangle(Point(startPosX, startPosY), ORIENTATION.RIGHT)
        drawGuidelineTriangle(Point(startPosX + m_a_x * 2, startPosY), ORIENTATION.LEFT)
        startPosX += m_a_x * 2
    drawGuidelineTriangle(Point(startPosX, startPosY), ORIENTATION.RIGHT)

    startPosX = colorPalleteX + m_a_x
    startPosY = colorPalleteY + side/2
    while startPosX <= BOARD_SIZE_X - m_a_x - side:
        drawGuidelineTriangle(Point(startPosX, startPosY), ORIENTATION.LEFT)
        drawGuidelineTriangle(Point(startPosX + m_a_x * 2, startPosY), ORIENTATION.RIGHT)
        startPosX += m_a_x * 2

    startPosX = colorPalleteX + m_a_x
    startPosY += side
    while startPosX <= BOARD_SIZE_X - m_a_x - side:
        drawGuidelineTriangle(Point(startPosX, startPosY), ORIENTATION.LEFT)
        drawGuidelineTriangle(Point(startPosX + m_a_x * 2, startPosY), ORIENTATION.RIGHT)
        startPosX += m_a_x * 2

    


def drawMenuButtonsUI():
    BUTTON_WIDTH = COLOR_PALLETE_SIZE * 2 - 10
    BUTTON_HEIGHT = 50
    button = Kami2Button(Point(BOARD_SIZE_X - COLOR_PALLETE_SIZE * 2 + 5, BOARD_SIZE_Y - 50), BUTTON_WIDTH, BUTTON_HEIGHT, 'Dev Mode', ACTION.SWITCH_MODE)
    uiButtons.append(button)
    button.Draw(window)
    button = Kami2Button(Point(BOARD_SIZE_X - COLOR_PALLETE_SIZE * 2 + 5, BOARD_SIZE_Y - 55 - BUTTON_HEIGHT), BUTTON_WIDTH, BUTTON_HEIGHT, 'Load', ACTION.LOAD)
    uiButtons.append(button)
    button.Draw(window)
    button = Kami2Button(Point(BOARD_SIZE_X - COLOR_PALLETE_SIZE * 2 + 5, BOARD_SIZE_Y - 60 - BUTTON_HEIGHT * 2), BUTTON_WIDTH, BUTTON_HEIGHT, 'Save', ACTION.SAVE)
    uiButtons.append(button)
    button.Draw(window)
    button = Kami2Button(Point(BOARD_SIZE_X - COLOR_PALLETE_SIZE * 2 + 5, BOARD_SIZE_Y - 65 - BUTTON_HEIGHT * 3), BUTTON_WIDTH, BUTTON_HEIGHT, 'Clear', ACTION.CLEAR)
    uiButtons.append(button)
    button.Draw(window)
    button = Kami2Button(Point(BOARD_SIZE_X - COLOR_PALLETE_SIZE * 2 + 5, BOARD_SIZE_Y - 70 - BUTTON_HEIGHT * 4), BUTTON_WIDTH, BUTTON_HEIGHT, 'Process', ACTION.PROCESS)
    uiButtons.append(button)
    button.Draw(window)

def saveTheBoard():
    data = {}
    cells = []
    for cell in uiTriangles:
        cells.append(cell.serialize())
    data['cells'] = cells

    writeDataToFile(SERIALIZED_OUTPUT_FILE, json.dumps(data))

def loadTheBoard():
    data = {}

    with open(SERIALIZED_OUTPUT_FILE) as data_file:    
        data = json.load(data_file)

    for i in range(0, len(uiTriangles)):
        uiTriangles[i].unserialize(data['cells'][i])

def colorArea(startingTriangle, timestampColor):
    internalColor = startingTriangle.GetColor()
    q = [startingTriangle]
    qSecond = []
    while len(q) > 0:
        time.sleep(0.01)
        currTriangle = q.pop()
        #neighbors = getNeighbors(currTriangle)
        neighbors = neighbordsMap[currTriangle.getUniqueID()]
        for neighbor in neighbors:
            if not neighbor.IsVisible():
                continue
            if internalColor == neighbor.GetColor():
                qSecond.append(neighbor)
                neighbor.SetColor(timestampColor)
        if len(q) == 0:
            for g in qSecond:
                q.append(g)
            qSecond.clear()

def mouseCallback(clickedPoint):
    global currentAction
    global currentMode
    global currentColor
    if currentMode == MODE.PLAY:
        for button in uiButtons:
            if button.HasBeenTouched(clickedPoint):
                if button.GetAction() == ACTION.SWITCH_MODE:
                    button.SetText('Dev Mode')
                    currentMode = MODE.DEV
                    return
        for triangle in uiTriangles:
            if triangle.HasBeenTouched(clickedPoint):
                if currentAction == ACTION.UNDRAW:
                    return
                else:
                    if not triangle.IsVisible():
                        return
                    thread = Thread(target = colorArea, args = (triangle, currentColor))
                    thread.start()


    for button in uiButtons:
        if button.HasBeenTouched(clickedPoint):
            if button.GetAction() == ACTION.CLEAR:
                clearBoard()
            elif button.GetAction() == ACTION.PROCESS:
                startToProcessTheBoard()
            elif button.GetAction() == ACTION.SAVE:
                saveTheBoard()
            elif button.GetAction() == ACTION.LOAD:
                loadTheBoard()
            elif button.GetAction() == ACTION.SWITCH_MODE:
                button.SetText('Play Mode')
                currentMode = MODE.PLAY

    for pallete in uiPalettes:
        if pallete.HasBeenTouched(clickedPoint):
            currentColor = pallete.colorIndex
            currentAction = ACTION.COLOR

            for p in uiPalettes:
                p.SetSelected(False, window)
            for p in transparencyPallete:
                p.SetSelected(False, window)
            pallete.SetSelected(True, window)

    for pallete in transparencyPallete:
        if pallete.HasBeenTouched(clickedPoint):
            for p in uiPalettes:
                p.SetSelected(False, window)
            pallete.SetSelected(True, window)
            setCurrentActionAsUndraw()
            return

    for triangle in uiTriangles:
        if triangle.HasBeenTouched(clickedPoint):
            if currentAction == ACTION.UNDRAW:
                triangle.Undraw()
            else:
                if not triangle.IsVisible():
                    triangle.Draw(window)
                triangle.SetColor(currentColor)
            return

def changeColorPallete(index):
    global colors
    colors = colorPalletes[index - 1]
    for uiPalleteChooser in uiPalettes:
        uiPalleteChooser.RefreshColor()
    for uiTriangle in uiTriangles:
        uiTriangle.RefreshColor()

def on_press(key):
    global currentState
    try: k = key.char
    except: k = key.name
    if k in ['1', '2', '3', '4', '5', '6', '7', '8']:
        changeColorPallete(int(k))
    if k == 'c':
        if currentState == STATE.COLOR:
            currentState = STATE.NORMAL
        elif currentState == STATE.NORMAL:
            currentState = STATE.COLOR

lis = keyboard.Listener(on_press=on_press)
lis.start()

def cacheNeighbors():
    for triangle in uiTriangles:
        neighbordsMap[triangle.getUniqueID()] = getNeighbors(triangle)

if __name__ == "__main__":
    drawPuzzleGuidelines()
    drawColorPalleteUI()
    drawMenuButtonsUI()
    drawBoardForFirstTime()
    cacheNeighbors()
    window.setMouseHandler(mouseCallback)
    window.mainloop()
