# Author: Liam Robinson
# Course: Spatial Algorithms
# Creation date: 07/05/2016
# Last update: 23/05/2017

# ----------------------------------------------------------------------------------------------------------------------
# Imports
import math
import decimal
import time
import sys
import igraph
import json

try:
    from Queue import *
    from Stack import *
except ImportError:
    print "Please add the Queue.py file and the Stack.py file to the same folder as the Assignment2.py folder."
    time.sleep(3)  # Give time to read the error message (if running on command line)
    sys.exit()

# ----------------------------------------------------------------------------------------------------------------------
# Global Variables


# ----------------------------------------------------------------------------------------------------------------------
# Function to let the user choose if they want to use a JSON file or a GTFS file.
# Inputs: None
# Outputs: File format
def fileFormatChoice():
    choice = str(raw_input("Please enter 'GTFS' if you want to use a GTFS file, or 'JSON' if you "
                           "want to use a geoJSON file: "))
    if choice.upper() == "GTFS":
        print "You have chosen to use a GTFS file."
        return "GTFS"
    elif choice.upper() == "JSON":
        print "You have chosen to use a geoJSON file."
        return "JSON"
    else:
        print "You didn't enter 'GTFS' or 'JSON' please try again."


# ----------------------------------------------------------------------------------------------------------------------
# Function to get the path to the GTFS file
# Inputs: None
# Outputs: File Path
def gtfsFilePath():
    file_path = raw_input("Please enter the path name for the GTFS file: ")
    return file_path
# ----------------------------------------------------------------------------------------------------------------------
# Function to check the user entered a valid path for the GTFS file
# Inputs: File Path
# Outputs: None

def checkFilePath(gtfs_file_name):
    try:
        int(gtfs_file_name)
        print "Please enter a valid path name."
        return ""  # Returns a blank file path, causes the error catch in the getJSONFromFile function to trigger.

    except ValueError:
        ''' Returns a blank file path if the user didn't enter any file.
        The code stills runs if the user doesn't enter a file without the following check.'''

        if gtfs_file_name == "":
            print "You didn't enter a path name. Please try again."
            return ""  # Will fall into the if statement in the getJSONFromFile function if the file path isn't valid.

        return gtfs_file_name


# ----------------------------------------------------------------------------------------------------------------------
# Function to get the JSON file path
# Inputs: None
# Outputs: File path
def jsonFilePath():
    json_file_path =  raw_input("Please enter the file path to the geoJSON file: ")
    return json_file_path


# ----------------------------------------------------------------------------------------------------------------------
# Function to check the user entered a valid path for the JSON file
# Inputs: File Path
# Outputs: None

def checkJsonPath(json_file_name):
    try:
        int(json_file_name)
        print "Please enter a valid path name."
        return ""  # Returns a blank file path, causes the error catch in the getJSONFromFile function to trigger.

    except ValueError:
        """ Returns a blank file path if the user didn't enter any file.
        The code stills runs if the user doesn't enter a file without the following check."""

        if json_file_name == "":
            print "You didn't enter a path name. Please try again."
            return ""  # Will fall into the if statement in the getJSONFromFile function if the file path isn't valid.

        return json_file_name


# ----------------------------------------------------------------------------------------------------------------------
# Function to open the JSON file of coordinates
# Inputs: File String
# Outputs: Json File Contents

def getJSONFromFile(path):
    if path == "":  # Checks if File is Valid
        return None
    try:
        fp=open(path)
        jsondict = json.load(fp)
        fp.close()
        return jsondict
    except IOError:
        print "Couldn't open file. Please check the path is correct and try again."
    except ValueError:
        print "The file you entered isn't a JSON file. Please attach a valid GeoJSON file and try again."
# End getJSONFromFile


# ----------------------------------------------------------------------------------------------------------------------
# Function to get the point coordinates from the dictionary (JSON)
# Inputs: JSON File Dictionary
# Outputs: Coordinates
def getPointCoordsFromJSON(jsondict):
    # Set an initial list for the coordinates
    coords = []

    # Loop through the dictionary and append the coordinates into the list
    try:
        for feature in jsondict['features']:
            geom = feature['geometry']
            if geom['type'] == "Point":
                coords.append(geom['coordinates'])
        return coords

    except KeyError:  # Code will error if the above keys aren't in the JSON file.
        print "Please check the JSON file entered has 'features', 'geometry' and 'coordinates' keys and try again."
        return ""


# ----------------------------------------------------------------------------------------------------------------------
# Function to get the point coordinates from the JSON file as a tuple
# Inputs: JSON File Dictionary
# Outputs: Tuple of point coordinates
def getPointsFromJSON(jsondict):
    if jsondict is None:
        return []  # Return an empty list if there is no data

    # Get list of point string coords
    lsCoords = getPointCoordsFromJSON(jsondict)
    # Split into x,y tuples for each segment
    points = []
    if lsCoords is None:  # Checks that the for loop won't error - can't loop through a list with no records.
        print "The code didn't return any valid points, please check the geometry type is 'Point' and try again."
        return None
    elif lsCoords == "":  # Occurs if the keys are wrong, the error message has already displayed so it returns None
        return None
    else:
        for point in lsCoords:
            pointCoords = (point[0], point[1])  # Appends the points to the list as a tuple.
            points.append(pointCoords)
        return points

# ----------------------------------------------------------------------------------------------------------------------
# Function to get the indexes for the required information from a text file. Assumes that the "stop_name", "stop_lon"
# and "stop_lat" column headings, all have a space in between the first quotation mark and the variable name, like the
# stops.txt file used for this assignment. (GTFS)
# Inputs: Heading Row
# Outputs: Indexes for the required columns
def getDataIndexes(row):
    i = 0
    ''' The following code loops through the first row (the headers) of the file. And if the header matches the required
    information then the index is recorded.'''
    while i < len(row):
        # print row[i]  #DEBUG
        if str(row[i]) == " stop_name":
            stop_name_index = i
            # print i  #DEBUG
        elif str(row[i]) == " stop_lon":
            longitude_index = i
            # print i  #DEBUG
        elif str(row[i]) == " stop_lat":
            latitude_index = i
            # print i  #DEBUG
        elif str(row[i]) == "location_type":
            location_type_index = i
            # print i  #DEBUG
        else:
            pass
        i +=1
    try:
        return (stop_name_index, longitude_index, latitude_index, location_type_index)
    except UnboundLocalError:  # Error received if one of the indexes has not been found.
        pass  # The error message displays in the getGTFSPointData function.
        return None


# ----------------------------------------------------------------------------------------------------------------------
# Function to get the point data from a comma separated text file. (GTFS)
# Inputs: File Path
# Outputs: Point Data
def getGTFSPointData(gtfs_file_name):
    pointData = []
    i = 0
    if gtfs_file_name != "":
       try:
            file = open(gtfs_file_name, 'r')
            for row in file:
                row = row.split(',')  # Splits the data on the comma, each row can then be indexed.
                if pointData == []:  # i.e. the first iteration
                    indexes = getDataIndexes(row)
                if indexes != None:  # Indexes will be none if the UnboundLocalError occurs in getDataIndexes()
                    stop_name = row[indexes[0]]  # getDataIndexes returns stop_name, long, lat and then location_type

                    longitude = row[indexes[1]].replace("'", "")  # Need to remove the quotes to convert to a decimal
                    if longitude != " stop_lon":  # Cannot convert the header row into a decimal
                        try:
                            longitude = decimal.Decimal(longitude)  # Uses the decimal module because float errors
                        except decimal.InvalidOperation:  # Error occurs if the latitude can't be converted to a decimal
                            # print "Error Code: 1"  #DEBUG
                            print "Error on latitude: " + str(latitude) + "and longitude: " + \
                                  str(longitude) + "please check the data and try again."

                    latitude = row[indexes[2]].replace("'","")  # Need to remove the quotes to convert to a decimal
                    if latitude != " stop_lat":  # Cannot convert the header row into a decimal
                        try:
                            latitude = decimal.Decimal(latitude)  # Uses the decimal module because float errors
                        except decimal.InvalidOperation:  # Error occurs if the latitude can't be converted to a decimal
                            # print "Error Code: 2"  #DEBUG
                            print "Error on latitude: " + str(latitude) + "and longitude: " + \
                                  str(longitude) + "please check the data and try again."

                    location_type = row[indexes[3]]
                    pointData.append((latitude, longitude, stop_name, location_type))
                else:  # Indexes is none - The code could not retrieve the headers.
                    print "At least one of the headings in the file was different than expected. Please check " \
                          "the file has the headings: ' stop_name', ' stop_lon', 'stop_lat', and 'location_type'."
                    return None

            if pointData == []:
                print "The program hasn't returned any data. Please check your file has data and try again."
                return None
            else:
                file.close()  # Close the file now the data read has been completed
                return pointData[1:]  # Returns the rows, except for the header row.

       except IOError:  # Error obtained if the file doesn't exist or can't be opened.
           print "The file name is invalid, please check the correct path has been entered."
    else:
        pass  # The error message for a blank file input has already been displayed

# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------
# Find the maximum Y value from the list of points
# Inputs: Point Tuples
# Outputs: Max Y Coordinate
def findPivot(points):
    maxY= 0
    maxX= 0
    try:
        for point in points:
            if point[0] > maxY:  # Pivot is the maximum y point
                maxY = point[0]  # Point coords stored as latitude, longitude (so Y is [0])
                maxX = point[1]

            elif point[0] == maxY:  # If max Y's are equal have to use max X and max Y
                if point[1] > maxX:
                    maxX = point[1]
                else:
                    pass
            else:
                pass
    except TypeError:  # Occurs if points is empty - for some reason "if points is not None" didn't appear to work.
        print "Cannot find the pivot, there is no point data. Please check the data and try again."
        sys.exit()  # Code exits because the rest of the code requires both point data and a pivot.

    return (maxY,maxX)



# ----------------------------------------------------------------------------------------------
# Calculate the polar angles of the points
# Inputs: Point Tuples, the Pivot Point
# Outputs: Polar Angles
def calcPolars(points, pivot):
    # Create list to append points and polar coordinates
    pointPolars = []
    if points is not None:
        # Calculates required variables and uses atan2 to account for functions
        for point in points:
            dy = pivot[1] - point[1] # Point[1] points to the longitude column
            dx = pivot[0] - point[0] # Point[0] points to the latitude column

            # Need to check if we're going to divide by 0
            if dx == 0:
                if dy == 0:
                    pass  # Means its the same point as the pivot
                else:
                    if dy < 0:  # if dy is negative
                            theta = 90
                            pointPolars.append(((point),theta))
                    else:  # dy is positive
                        theta = 270
                        pointPolars.append(((point),theta))
            else:
                if dy == 0:  # Same horizontal line
                    theta = 180
                    pointPolars.append(((point),theta))
                else:
                    theta = math.degrees(math.atan2(dy, dx))

                    # Need to check if angle greater than 360 degrees
                    if int(theta) > 360:
                        theta -= 360
                    pointPolars.append(((point),theta))

        return pointPolars
    else:
        pass  # The error message that says the points were empty has already displayed.

# ----------------------------------------------------------------------------------------------
# Sort the list of points and polar coordinates by polar coordinates
# Inputs: pointPolars (list of points and polar coordinates)
# Outputs: Re-ordeded pointPolars list
def sortPolars(pointPolars):
    # Sort the points by their polar coordinates
    try:
        pointPolars.sort(key=lambda point:point[1])
        return pointPolars
    except AttributeError:  # Occurs if it tries to sort an empty list
        pass  # The error for the empty point data has already displayed

# ----------------------------------------------------------------------------------------------
# Code to calculate the convex hull of a set of points using the Graham Scan Algorithm
# Logic was largely obtained from https://lms.curtin.edu.au/bbcswebdav/pid-4014769-dt-content
# -rid-22747674_1/courses/314394-FacSciEng-1824991473/ConvexHull_v2%284%29.swf
# Inputs: sortedPointPolars, pivot
# Outputs: Stack with the points on the convex hull
def grahamScan(sortedPointPolars, pivot):

    # Create the stack and the queue for the points to be added to
    Q = Deque()
    S = Stack()

    '''In the for loop, the coordinates are converted into floats. Previously this errored in the getPointData()
     function. However, after testing it doesn't appear to error when the numbers are converted to floats here'''
    if sortedPointPolars is not None:
        for point in sortedPointPolars:
            longitude = point[0][1]
            latitude = point[0][0]
            Q.addBack((float(latitude), float(longitude)))  # Add all the points into the queue
        longitude = float(pivot[1])
        latitude = float(pivot[0])
        S.push((latitude,longitude))  # Add the pivot point to the stack
        if Q.isEmpty() != True:  # Code can not run if the queue is empty
            value = Q.peek()  # Read the first value from the queue
            Q.removeFront()
            S.push(value)  # Add the value onto the stack

        else:
            print "There are no values in the queue. Please check the data and try again."
            sys.exit()  # If there are no point the Convex Hull cannot be plotted.

        while Q.isEmpty() != True:  # Loop through the queue until it is empty
            value = Q.peek()
            Q.removeFront()
            S.push(value)  # Add the next value from the queue onto the stack
            turn = 1  # Set the turn to initially get into the while loop
            while turn == 1:  # Allows for the backtrack
                ValueA = S.peek()
                S.pop()
                ValueB = S.peek()
                S.pop()
                ValueC = S.peek()
                S.pop()  # Get the three points from the stack and pop them
                S.push(ValueC)  # Add pointC back onto the stack

                turn = calculateTurn(ValueA, ValueB, ValueC)  # Returns a 1 if there is a LHT or a 0 if it is a RHT
                if turn == 1:
                    S.push(ValueA)

                else:
                    S.push(ValueB)
                    S.push(ValueA)
        # S.size()  #DEBUG- Used to see if the convex hull contains a smaller number of points than the original data
        return S
    else:
        pass  # Error message has already been displayed

# ----------------------------------------------------------------------------------------------
# Converts 3 points into 2 lines and calculates the cross product between them
# http://stackoverflow.com/questions/27635188/algorithm-to-detect-left-or-right-turn-from-x-y-co-ordinates
# Inputs: ValueA, ValueB, ValueC
# Outputs: Value based on direction of turn
def calculateTurn(ValueA, ValueB, ValueC):
    # == Line 1
    x1 = ValueB[0] - ValueA[0]
    y1 = ValueB[1] - ValueA[1]

    # == Line 2
    x2 = ValueC[0] - ValueB[0]
    y2 = ValueC[1] - ValueB[1]

    # Cross Product
    cp = (x1 * y2) - (y1 * x2)
    if cp > 0:
        return 1
    else:
        return 0


# ----------------------------------------------------------------------------------------------
# Removes the pivot point from the point data
# Inputs: pointCoords, pivot
# Outputs: pointCoords without the pivot
def removePivotFromData(pointCoords,pivot):
    numIterations = 0  # Sets an initial counter for the number of iterations
    for point in pointCoords:  # Loops through all of the points
        numIterations +=1  # Increments the count by one
        if str(point) == str(pivot):  # If the point is the pivot point
            pointCoords.pop(numIterations-1)  # Pop that point from the list
    return pointCoords


# ----------------------------------------------------------------------------------------------
# Displays the graph of the convexHull
# Inputs: Convex Hull, pointData
# Outputs: None
def createGraph(convexHull, pointData):
    g = igraph.Graph()
    coords = []  # Creates an initial list for the coordinates to be appended into
    edgeList =[]  # Creates an initial list for the vertex indexes to be appended into so the vertices join up
    i=1  # Create an initial index
    while convexHull.isEmpty() is not True:  # Code keeps looping until the convex hull has no more points to plot
        g.add_vertex(str(i))  # Vertex index is just the i counter -> Can't be a stop name because JSON doesn't have
                              # this information
        coords.append(convexHull.peek())  # Add the coordinates to the coordinates list
        convexHull.pop()
        if str(i) != "1":  # At i=1 there is not two edges to append to the edge list
            if int(convexHull.size()) != 0:  # The last point needs to append itself and the previous point as well
                                             # as the initial point
                edgeList.append((str(i), str(i-1)))
            else:  # Last Point
                edgeList.append((str(i), str(i-1)))
                edgeList.append((str(i), "1"))
        else:
            pass
        i += 1

    points = Stack()  # Create a stack for the point data to be added into
    for point in pointData:
        points.push(point)
    while points.isEmpty() is not True:
        g.add_vertex(str(i))  # Adds all the points (The ones in the convex hull are added again, but this does not
                              # affect the graph produced)
        latitude = points.peek()[0]  # Create lat and long variables in order to append them to the coordinate list
        longitude = points.peek()[1]
        coords.append((float(latitude), float(longitude))) # Float errors if they aren't converted to variables first
        points.pop()  # Remove the point

    g.add_edges(edgeList)  # Uses the edge list to create the edges

    visual_style = {}
    visual_style["layout"] = coords  # layout takes a 2d matrix of coordinates and uses them
                                     # to position the vertexes. bbox of 2000,2000 appears to be a
                                     # suitable size
    visual_style['bbox'] = (2000,2000)
    igraph.plot(g, **visual_style)
    # print igraph.GraphSummary(g)  #DEBUG



#  Main Script
def main():

    choice = fileFormatChoice()

    if choice == "GTFS":
        # == Get File Path ==
        gtfs_file_name = gtfsFilePath()

        # == Check inputs ==
        checkFilePath(gtfs_file_name)

        # == Get point data ==
        pointData = getGTFSPointData(gtfs_file_name)
        # pointData = [(0,0),(0,1),(1,0),(1,1), (1,2),(2,1),(3,1), (2,2),(2,0),(3,0),(4,0)]  #DEBUG

        # == Find Pivot ==
        pivot = findPivot(pointData)
        pointData = removePivotFromData(pointData,pivot)

        # == Calculate Polar Angles ==
        pointPolars = calcPolars(pointData, pivot)

        # == Sort by Polar Angles ==
        sortedPointPolars = sortPolars(pointPolars)

        # == Get the Convex Hull ==
        convexHull = grahamScan(sortedPointPolars,pivot)

        # == Graph the Convex Hull ==
        createGraph(convexHull, pointData)

    elif choice == "JSON":  # Choice has to be JSON
        # == Get File Path ==
        json_file_name = jsonFilePath()

        # == Check inputs ==
        json_file_name = (json_file_name)

        # == Get point data ==
        jsondict = getJSONFromFile(json_file_name)
        points = getPointsFromJSON(jsondict)

        # == Find Pivot ==
        pivot = findPivot(points)
        points = removePivotFromData(points,pivot)

        # == Calculate Polar Angles ==
        pointPolars = calcPolars(points, pivot)

        # == Sort by Polar Angles ==
        sortedPointPolars = sortPolars(pointPolars)

        # == Get the Convex Hull ==
        convexHull = grahamScan(sortedPointPolars,pivot)

        # == Graph the Convex Hull ==
        createGraph(convexHull, points)

    else:
        sys.exit()  # Code keeps running if invalid choice was entered - need to exit the program

    # == Debug ==
    '''if pointData is not None:
        for i in range(0, 10, 5):
            print pointData[i]'''

    '''for data in sortedPointPolars:
        print data'''

    '''x = Deque()
    y = Stack()'''
main()

