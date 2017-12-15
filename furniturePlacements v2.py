from parse import *
from shapely import *
from shapely.geometry import *
from shapely import affinity
import json

OFFSET = 0.15

js = open("result.json").read()
data = json.loads(js)

def parsePoints(input):
    #Output is a list of tuples
    output = []
    coord = ()
    for line in input.split("), "):
        x = float(line.split(",")[0].strip().strip('('))
        y = float(line.split(",")[1].strip().strip(')'))
        coord = (x,y)
        output.append(coord)
    return output;

def parseFurniture(input):
    input = input.strip().strip("(").strip(")")
    #Output is list of tuples
    output = [parsePoints(x.split(":")[1]) for x in input.split(";")]
    #To add weights
    #output = [[float(x.split(":")[0]),parsePoints(x.split(":")[1])] for x in input.split(";")]
    return output;

def shapeWeights(input):
    input = input.strip().strip("(").strip(")")
    #Output is list of tuples
    output = [parsePoints(x.split(":")[1]) for x in input.split(";")]
    #To add weights
    #output = [[float(x.split(":")[0]),parsePoints(x.split(":")[1]]) for x in input.split(";")]
    return output;

def mainParse():
    with open('problems.rfp') as lines:
        content = lines.readlines()
    content = [lines.strip() for lines in content]
    for line in content:
        problemNumber = (line.split("#")[0].split(":")[0])
        room = parsePoints((line.split("#")[0]).split(":")[1]) #Vertices of room as a list of tuples
        furniture = line.split("#")[1]
        furniture = parseFurniture(furniture) #List of list of vertices of shapes
        #CHANGE PROBLEM NUMBER HERE
        if int(problemNumber)==28:
            print(problemNumber,":")
            furnitureUsed, placement, furnitureNotUsed = placeFurniture(problemNumber, room, furniture)
            print(placement)

def placeFurniture(problemNumber, room, shapes):
    #initialise empty arrays
    shapeAreas = []
    shapeWeights = []
    usedShapes = []
    placement = []
    shapeIDs = []

    #find the areas of the pieces of furniture
    for i in range(0,len(shapes)):
        shape = Polygon(shapes[i])
        shapeAreas.append((i, shape.area))
        
    #find the costs of the pieces of furniture
    count = 0
    for item in data[str(problemNumber)]["furniture"]:
        shapeWeights.append((count, item["weight"]*shapeAreas[count][1]))
        count = count+1

    #sort the pieces of furniture by cost
    shapeWeights.sort()

    #sort the pieces of furniture by area
    shapeAreas.sort()
    
    #find the area and bounds of the room
    currentRoom = Polygon(room)
    originalRoomArea = currentRoom.area
    goal = 0.7*originalRoomArea
    roomBounds = currentRoom.bounds
    maxRoomHeight = roomBounds[3]-roomBounds[1]
    maxRoomWidth = roomBounds[2]-roomBounds[0]

    for j in range(0,len(shapeWeights)):
        #print("NEW SHAPE")
        try:
            currentShape = shapes[shapeWeights[j][0]]
            shapeID = shapeWeights[j][0]
        except:
            print("Not 30% of room")
            return usedShapes, placement, shapes
        currentPolygon = Polygon(currentShape)
        originalPolygon = currentPolygon
        
        #find max height and width of shape
        shapeBounds = currentPolygon.bounds
        maxShapeHeight = shapeBounds[3]-shapeBounds[1]
        maxShapeWidth = shapeBounds[2]-shapeBounds[0]
        
        if(currentRoom.area<goal):
            #when 30% of the room is filled return shapes and placements
            print("30% of room")
            return usedShapes, placement, shapes
        if((maxShapeHeight<maxRoomHeight and maxShapeHeight<maxRoomWidth) or (maxShapeWidth<maxRoomWidth and maxShapeHeight<maxRoomWidth)):
            #shape should fit
            if currentPolygon.within(currentRoom):
            #shape is in the room already
                usedShapes.append(currentShape)
                shapeIDs.append(shapeID)
                x,y = currentPolygon.exterior.coords.xy
                coords = list(zip(x,y))
                coords = coords[:-1]
                placement.append(coords)
                shapes.remove(currentShape)
                currentRoom = currentRoom.difference(currentPolygon)
            else:
                k = roomBounds[1]
                while k<maxRoomHeight:
                    l=0
                    while l < maxRoomWidth:
                        #currentPolygon = originalPolygon
                        currentPolygon = Polygon(affinity.translate(currentPolygon,l,0))
                        if currentPolygon.within(currentRoom):
                            if shapeID not in shapeIDs:
                                usedShapes.append(currentShape)
                                shapeIDs.append(shapeID)
                                x,y = currentPolygon.exterior.coords.xy
                                coords = list(zip(x,y))
                                coords = coords[:-1]
                                placement.append(coords)
                                shapes.remove(currentShape)
                                currentRoom = currentRoom.difference(currentPolygon)
                        l=l+OFFSET
                    currentPolygon = Polygon(affinity.translate(originalPolygon, roomBounds[0], k))
                    if currentPolygon.within(currentRoom):
                        if shapeID not in shapeIDs:
                            usedShapes.append(currentShape)
                            shapeIDs.append(shapeID)
                            x,y = currentPolygon.exterior.coords.xy
                            coords = list(zip(x,y))
                            coords = coords[:-1]
                            placement.append(coords)
                            shapes.remove(currentShape)
                            currentRoom = currentRoom.difference(currentPolygon)
                    k=k+OFFSET
                #if this while loop finishes then shape doesn't fit
                
        else:
            continue
    
mainParse()
