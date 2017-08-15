from graphics import *
import random
import math
from pynput import keyboard

TRIANGLE_SIZE = 80
move_along_x = math.sqrt(3)/2.0 * TRIANGLE_SIZE

BOARD_SIZE_X = move_along_x * 10
BOARD_SIZE_Y = TRIANGLE_SIZE * 14

print('Available colors are:')
print('1. Red\n2. Green\n3. Blue\n4. Yellow\nu. Undraw')

currentColor = '2'

FOLDING_COLOR = color_rgb(50, 50, 50)

def getColor():
    rand_shade = random.randrange(30, 100, 20)
    color = color_rgb(0, 0, 0)
    if currentColor == '1':
        color = color_rgb(255, rand_shade, rand_shade)
    elif currentColor == '2':
        color = color_rgb(rand_shade, 255, rand_shade)
    elif currentColor == '3':
        color = color_rgb(rand_shade, rand_shade, 255)
    elif currentColor == '4':
        color = color_rgb(255, 255, rand_shade)

    return color

win = GraphWin("KAMI2", BOARD_SIZE_X, BOARD_SIZE_Y)

def on_press(key):
    try: k = key.char # single-char keys
    except: k = key.name # other keys
    global currentColor
    currentColor = k

lis = keyboard.Listener(on_press=on_press)
lis.start() # start to listen on a separate thread
#lis.join() # no this if main thread is polling self.keys

def sign(p1, p2, p3):
    return (p1.x - p3.x) * (p2.y - p3.y) - (p2.x - p3.x) * (p1.y - p3.y);

def PointInTriangle(pt, v1, v2, v3):
    b1 = sign(pt, v1, v2) < 0.0;
    b2 = sign(pt, v2, v3) < 0.0;
    b3 = sign(pt, v3, v1) < 0.0;

    return ((b1 == b2) and (b2 == b3));

def drawRightTriangle(sp):
    p1 = sp
    p2 = Point(sp.x + move_along_x, sp.y + TRIANGLE_SIZE/2)
    p3 = Point(sp.x, sp.y + TRIANGLE_SIZE)

    vertices = [p1, p2, p3]

    triangle = Polygon(vertices)

    triangle.setFill(getColor())
    triangle.setOutline(FOLDING_COLOR)
    triangle.setWidth(1)
    triangle.draw(win)
    
    return triangle

def drawLeftTriangle(sp):
    p1 = sp
    p2 = Point(sp.x - move_along_x, sp.y + TRIANGLE_SIZE/2)
    p3 = Point(sp.x, sp.y + TRIANGLE_SIZE)

    vertices = [p1, p2, p3]

    triangle = Polygon(vertices)
    
    triangle.setFill(getColor())
    triangle.setOutline(FOLDING_COLOR)
    triangle.setWidth(1)
    triangle.draw(win)

    return triangle

triangles = []

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
    for triangle in triangles:
        vertices = triangle.getPoints()
        if PointInTriangle(clickedPoint, vertices[0], vertices[1], vertices[2]):
            if currentColor == 'u':
                triangle.undraw()
            else:
                triangle.setFill(getColor())
