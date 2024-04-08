import numpy as np
import serial
import time
import datetime
import csv
import sys



ROWS = 80  # Rows of the sensor
COLS = 28  # Columns of the sensor

debug = True


    

def activePointsRequestMap(ser):
    if debug:
        print("Requesting pressure map")
    data = "R"
    sentCount = ser.write(data.encode())
    # ser.flush()
    if debug:
        print(f"Sent R as {sentCount} bytes")


def activePointsReceiveMap(ser):
    if debug:
        print("Receiving map")
    matrix = np.zeros((ROWS, COLS), dtype=int)

    activePointCountHighByte = ser.read()
    activePointCountLowByte = ser.read()
    activePointCount = ((int.from_bytes(activePointCountHighByte, 'big') << 8) 
        | int.from_bytes(activePointCountLowByte, 'big'))

    if debug:
        print(f"activePointCount={activePointCount}")

    xbyte = ser.read().decode('utf-8')
    xbyte = ser.read().decode('utf-8')
    x = 0
    y = 0
    n = 0
    while(n < activePointCount):
        x = ser.read()
        y = ser.read()
        x = int.from_bytes(x, 'big')
        y = int.from_bytes(y, 'big')
        valueHighByte = ser.read()
        valueLowByte = ser.read()
        value = ((int.from_bytes(valueHighByte, 'big') << 8) | int.from_bytes(valueLowByte, 'big'))
        if debug:
            print(f"x={x}, y={y}, value={value}")
        matrix[x][y] = value
        n += 1
    return matrix
 
def activePointsRetrieveMap(ser):
    xbyte = ''
    print(f"Bytes waiting to be read: {ser.in_waiting}")
    if ser.in_waiting > 0:
        try:
            xbyte = ser.read()
            if debug:
                print(f"Byte read: {xbyte.hex()}")
            if(xbyte.decode('utf-8') == 'N'):
                xbyte = ser.read()
                if debug:
                    print(f"Byte read: {xbyte.hex()}")
                if(xbyte.decode('utf-8') == '\n'):
                    map = activePointsReceiveMap(ser)
                    return map
                else:
                    raise Exception(f"ActivePoints protocol error: expected '0a' but received {xbyte.hex()}")                    
            else:
                raise Exception(f"ActivePoints protocol error: expected '4e' but received {xbyte.hex()}")
                
        except Exception as ex:
            print(ex)
            return None
    else:
        ser.flush()
        return None


def getMap(ser):
    activePointsRequestMap(ser)
    map = None
    while map is None: 
        map = activePointsRetrieveMap(ser)
        if map is None:
            if debug:
                print("Map not available, waiting 0.1s")
            time.sleep(0.1)
    if debug:
        print(f"Map retrieved")
    return map

def printMap(map):
    for i in range(ROWS):
        tmp = ""
        for j in range(COLS):
            tmp = tmp + str(map[i][j]) + " ,"
        print(tmp)
    print("\n")

def fitness_mat_data_collector(pathname, port):
    # Connects to serial port
    # '/dev/ttyUSB0'
    ser = serial.Serial(
        port,
        baudrate=115200,
        timeout=0.1
    )

    # Open file
    with open(pathname, 'w') as f:
    
        writer = csv.writer(f)
    
        # Write CSV header
        csvHeader = ['Timestamp']
        for row in range(ROWS):
            for column in range(COLS):
                csvHeader.append("({row}-{column})".format(row=row, column=column))
        writer.writerow(csvHeader)
    
        # Run until interrupted
        while True:
        
            # Get map
            map = getMap(ser)
                 
            # Get current timestamp
            currentTimestamp = time.time()
            if debug:
                print(f"Got map at {currentTimestamp}")
            # if debug:
            #     printMap(map)

            # Prepare new CSV line
            csvLine = []
            csvLine.append(currentTimestamp)
            for row in range(ROWS):
                csvLine.extend(map[row,:])
            # if debug:
            #     print(csvLine)

            # Write CSV line to file            
            writer.writerow(csvLine)
            


def main():

    # Check syntax
    arg_count = len(sys.argv)
    if arg_count != 3:
        print(f"Syntax: python3 {sys.argv[0]} <port> <filename>")
        sys.exit(-1)
    
    # Get port
    port = sys.argv[1]
    if debug:
        print(f"Port {port}")
        
    # get pathname
    pathname = sys.argv[2]
    if debug:
        print(f"Pathname {pathname}")
    
    # Connects to serial port
    # '/dev/ttyUSB0'
    ser = serial.Serial(
        port,
        baudrate=115200,
        timeout=0.1
    )

    # Open file
    with open(pathname, 'w') as f:
    
        writer = csv.writer(f)
    
        # Write CSV header
        csvHeader = ['Timestamp']
        for row in range(ROWS):
            for column in range(COLS):
                csvHeader.append("({row}-{column})".format(row=row, column=column))
        writer.writerow(csvHeader)
    
        # Run until interrupted
        while True:
        
            # Get map
            map = getMap(ser)
                 
            # Get current timestamp
            currentTimestamp = time.time()
            if debug:
                print(f"Got map at {currentTimestamp}")
            # if debug:
            #     printMap(map)

            # Prepare new CSV line
            csvLine = []
            csvLine.append(currentTimestamp)
            for row in range(ROWS):
                csvLine.extend(map[row,:])
            # if debug:
            #     print(csvLine)

            # Write CSV line to file            
            writer.writerow(csvLine)
            
            
            

main()