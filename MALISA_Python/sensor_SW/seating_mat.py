import numpy as np
import serial
import time
import csv
import sys


ROWS = 20  # Rows of the sensor
COLS = 20  # Columns of the sensor

debug = False


def fullMatrixStartSequence(ser):
    # This function sends a start sequence command to the device connected to the serial port (ser). It sends the character 'S' to initiate the pressure map sequence.
    if debug:
        print("Starting pressure map sequence")
    data = "S"
    sentCount = ser.write(data.encode())
    # ser.flush()
    if debug:
        print(f"Sent S as {sentCount} bytes")

    
def fullMatrixStopSequence(ser):
    # This function sends a start sequence command to the device connected to the serial port (ser). It sends the character 'S' to initiate the pressure map sequence.
    if debug:
        print("Stopping pressure map sequence")
    data = "X"
    sentCount = ser.write(data.encode())
    # ser.flush()
    if debug:
        print(f"Sent X as {sentCount} bytes")


def fullMatrixReceiveMap(ser):
    # This function receives a pressure map from the device connected to the serial port (ser). It reads data packets containing pressure values and constructs a matrix representing the pressure map. 
    # It returns the constructed matrix.
    if debug:
        print("Receiving map")
    
    matrix = np.zeros((ROWS, COLS), dtype=int)
    
    for row in range (0, ROWS):
        
        xbyte = ser.read()
        if debug:
            print(f"Byte read: {xbyte.hex()}")
        if(xbyte.decode('utf-8') != 'M'):
            raise Exception(f"FullMatrix protocol error: expected '4d' but received {xbyte.hex()} - {xbyte.decode('utf-8')}")
    
        xbyte = ser.read()
        if debug:
            print(f"Byte read: {xbyte.hex()}")
        if(int.from_bytes(xbyte, 'big') != COLS):
            raise Exception(f"FullMatrix protocol error: expected {COLS} columns but received {xbyte.hex()} - {int.from_bytes(xbyte, 'big')}")

        xbyte = ser.read()
        if debug:
            print(f"Row index: {xbyte.hex()}")
        rowIndex = int.from_bytes(xbyte, 'big')
        
        for columnIndex in range(0, COLS):
            
            valueLowByte  = ser.read()
            valueHighByte = ser.read()
            high = int.from_bytes(valueHighByte, 'big')
            if debug:
                print(f"Value high byte {high}")
            low = int.from_bytes(valueLowByte, 'big')
            if debug:
                print(f"Value low byte {low}")

            receivedValue = ((high << 8) + low)
            value = 4095 - receivedValue 
            if debug:
                print(f"Received: {receivedValue}, value: {value}")
            
            matrix[rowIndex][columnIndex] = value
        
        xbyte = ser.read()
        if debug:
            print(f"Row end: {xbyte.hex()}")  

    return matrix


 
def fullMatrixRetrieveMap(ser):
    # This function retrieves a pressure map from the device connected to the serial port (ser). It checks for the availability of data and then calls fullMatrixReceiveMap(ser) to receive the pressure map data.
    # It returns the received pressure map matrix or None if no data is available.
    xbyte = ''
    print(f"Bytes waiting to be read: {ser.in_waiting}")
    if ser.in_waiting > 0:
        try:
            xbyte = ser.read()
            if debug:
                print(f"Byte read: {xbyte.hex()}")
            if(xbyte.decode('utf-8') != 'H'):
                raise Exception(f"FullMatrix protocol error: expected '48' but received {xbyte.hex()} - {xbyte.decode('utf-8')}")

            xbyte = ser.read()
            if debug:
                print(f"Byte read: {xbyte.hex()}")
            if(xbyte.hex() != '00'):
                raise Exception(f"FullMatrix protocol error: expected '00' but received {xbyte.hex()} - {xbyte.decode('utf-8')}")
                
            xbyte = ser.read()
            if debug:
                print(f"Byte read: {xbyte.hex()}")
            if(xbyte.decode('utf-8') != '\n'):
                raise Exception(f"FullMatrix protocol error: expected '0a' but received {xbyte.hex()}")                

            map = fullMatrixReceiveMap(ser)
            return map
                
        except Exception as ex:
            print(ex)
            return None
    else:
        # ser.flush()
        return None


def getMap(ser):
    # This function retrieves a pressure map from the device connected to the serial port (ser). It repeatedly calls fullMatrixRetrieveMap(ser) until it successfully retrieves a pressure map. 
    # It returns the received pressure map matrix.
    map = None
    while map is None: 
        map = fullMatrixRetrieveMap(ser)
        if map is None:
            if debug:
                print("Map not available, waiting 0.1s")
            time.sleep(0.1)
    if debug:
        print(f"Map retrieved")
    return map


def printMap(map):
    # This function prints a pressure map matrix to the console. It prints each element of the matrix row by row.
    for i in range(ROWS):
        tmp = ""
        for j in range(COLS):
            tmp = tmp + str(map[i][j]) + " ,"
        print(tmp)
    print("\n")
   

def skipAdv(ser):
    # This function skips any additional data available in the serial buffer. It reads and discards any data present in the serial buffer until it becomes empty.
    while ser.in_waiting > 0:
        xbyte = ser.read()
        if debug:
            print(f"Read byte {xbyte.hex()} - {xbyte.decode('utf-8')}")


# def main():

#     # Check syntax
#     arg_count = len(sys.argv)
#     if arg_count != 3:
#         print(f"Syntax: python3 {sys.argv[0]} <port> <filename>")
#         sys.exit(-1)
    
#     # Get port
#     port = sys.argv[1]
#     if debug:
#         print(f"Port {port}")
        
#     # get pathname
#     pathname = sys.argv[2]
#     if debug:
#         print(f"Pathname {pathname}")
    
#     # Connects to serial port
#     # '/dev/ttyUSB0'
#     ser = serial.Serial(
#         port,  
#         baudrate=115200,
#         timeout=0.1
#     )

#     # Skip BLE advertising string
#     time.sleep(5)
#     skipAdv(ser)

#     # Open file
#     with open(pathname, 'w') as f:
    
#         writer = csv.writer(f)
    
#         # Write CSV header
#         csvHeader = ['Timestamp']
#         for row in range(ROWS):
#             for column in range(COLS):
#                 csvHeader.append("({row}-{column})".format(row=row, column=column))
#         writer.writerow(csvHeader)
        
#         # Run until interrupted
#         while True:
        
#             # Send start sequence to retrieve full matrix
#             fullMatrixStartSequence(ser)

#             # Get matrix
#             map = getMap(ser)
            
#             # Get current timestamp
#             currentTimestamp = time.time()
#             if debug:
#                 print(f"Got map at {currentTimestamp}")
#             # if debug:
#             #     printMap(map)

       
#             # Prepare new CSV line
#             csvLine = []
#             csvLine.append(currentTimestamp)
#             for row in range(ROWS):
#                 csvLine.extend(map[row,:])
#             # if debug:
#             #     print(csvLine)

#             # Write CSV line to file            
#             writer.writerow(csvLine)
            


# main()