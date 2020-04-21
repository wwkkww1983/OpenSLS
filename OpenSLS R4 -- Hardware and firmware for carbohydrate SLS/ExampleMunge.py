###Munge File for #MillerLab OpenSLS
#
# Authors: Ian Kinstlinger & David Yalacki
# Revised 12/24/16 
#
#

import math
import re
import time

from Tkinter import Tk
from tkFileDialog import askopenfilename
from tkFileDialog import asksaveasfilename
from tkFileDialog import asksaveasfile


################################
################################
#DEFINITIONS
#

TRAVEL_SPEED = 8000 #mm/min
LAYER_HEIGHT_SLIC3R = 0.05 #mm 
FEED_MULTIPLIER = 0 #Change from 0 to use feed piston
SHAKE_SPEED = 18000 #mm/min
PLOW_SPEED = 1800 #mm/min
# SINTER_SPEED = 500 #mm/min
# POWER_1 = 20 #PWM % 0-100
# POWER_2 = 19 #PWM % 0-100
# POWER_3 = 20 #PWM % 0-100
# POWER_4 = 20.0
POWER = [30, 19, 19, 19, 19, 20, 19.5, 20, 20, 20, 20, 20, 20, 20, 20]
SPEED = [3500, 1500, 2400, 2100, 2100, 3600, 1700, 2000, 2250, 2500, 2750, 2750, 2500, 2800, 3100]
EXTRUDE_MIN = [0.0002, 0.00005, 0.00005, 0.00005, 0.00005, 0.00005, 0.0000, 0, 0, 0, 0] #How large must the extrude value be to be valid?
numModels = 2


############################################################################
        ##Beginning of print commands
BeginningCode = '''
;GCODE generated by Slic3r
;Munged for OpenSLS on ''' + time.strftime("%x") + ' at ' + time.strftime("%H:%M:%S") +'''\n

G21
M107
G90
M83


G21 ; set units to millimeters
G90 ; use absolute coordinates
M83 ; use relative distances for extrusion
G4 S1
M166 S200
G4 S1
M649 S28


M649 S''' + str(POWER[0]) + '\n\n' ##Note this assumes the first geometry to be printed uses POWER_1 (AKA EXT0)




############################################################################
            ##DISTRIBUTION CODE##
                #Comments within GCODE are denoted by semicolon
            
DistributionCode = '''
;Begin distributing
G90
G0 X0 Y0 F3000
T0 ;Build platform active
G0 E-1.15 F200
G0 E1.0 F200
T1 ;Feed piston active
G0 X0 Y0 F2000
G0 E0 F200
G4 S0.5
M166 S200 ;servos down

G91 ;Go to relative coords for shaking
G0 X-115 Y30 F7000

;G0 X-10 Y-5 F8000
;G0 X-10 Y5
;G0 X-10 Y-5
;G0 X-10 Y5
;G0 X-10 Y-5
;G0 X-10 Y5

;G0 X0 Y25 F9000

;G0 X10 Y-5 F8000
;G0 X10 Y5
;G0 X10 Y-5
;G0 X10 Y5
;G0 X10 Y-5
;G0 X10 Y5

G0 X0 Y50 F9000


G0 X-70 Y25 F9000
G0 X5 Y5
G0 X5 Y5
G0 X5 Y-5
G0 X0 Y5
G0 X0 Y-5

G0 X10 Y-5 F9000
G0 X10 Y0
G0 X10 Y-5
G0 X10 Y5
G0 X10 Y-5
G0 X5 Y5
G0 X0 Y0
G0 X5 Y-5
G0 X0 Y5
G0 X0 Y-5

G0 X0 Y20 F10000
G0 X-5 Y-5
G0 X-5 Y-5
G0 X-5 Y5
G0 X0 Y-5
G0 X0 Y5
G0 X0 Y-20 F9000

;G0 X-10 Y5
;G0 X-10 Y-5
;G0 X-10 Y5
;G0 X-10 Y-5
;G0 X-10 Y5
;G0 X-10 Y-5
;G0 X-10 Y5
G0 X-10 Y5


G0 X0 Y20 F10000
G0 X-5 Y-5
G0 X-5 Y-5
G0 X-5 Y5
G0 X0 Y-5
G0 X0 Y5

G0 X-10 Y-60 F7000



G90 ;Back to absolute positioning
G4 S0.5

;%Clean laser nosepiece
G0 X0 Y-150 F7000
M166 S300
G4 S1
G0 Z70 F10000
M166 S200
G4 S1

G0 Z850 F10000 ;travel 2
G4 S1
;Clean spatula
G4 S0.5
;M166 S100 ;way up, hit brush
;G4 S0.5
M166 S300 ; back to normal
G4 S0.5
;M106 S150 ;rod spin
G4 S1
G0 Z0 F10000
G0 X0 Y0 F5000


;G0 X0 Y0 Z0 F10000
M166 S300
M107
G4 S0.5
M166 S200
G4 S2
;End distribution
'''

#Note the negative Z move in the above script
#Max distance hopper can move is +80 from origin, better off at +70



####################################################################
####################################################################



print("\n\nChoose the original G-code file")


Tk().withdraw() # we don't want a full GUI, so keep the root window from appearing
orig_gcode = askopenfilename() # show an "Open" dialog box and return the path to the selected file

print(orig_gcode)


print("\n\nName the output munged G-code")
Munged = asksaveasfile(mode='w', defaultextension=".gcode")

#outname = raw_input("Name for the output file: ")

#Munged = open(outname + ".gcode", 'a')

prevline = ''

AfterLayer1 = False
currentExtruder = 0
currentZ = '0.100'

Munged.write(BeginningCode)
#Munged.write(BeginningCode)




with open(orig_gcode, 'r') as original_gcode:
    for line in original_gcode:

        #Remove the carriage return that ends each line (for editing ease)
        line = line.replace('\n', '')

        #Start munging line-by-line
        if re.search('Layer ' + str(numModels), line):
            AfterLayer1 = True

        if AfterLayer1 == False:
           line = '' 

        elif AfterLayer1: 

            #Get rid of anything involving temperature control
            if re.search('M104', line) or re.search('M106', line) or re.search('M109', line) \
               or re.search('M190', line) or re.search('M140', line):

                line = ''

            #Set power based on extruder
            # if re.search('T0', line):
                # line = 'M649 S' + str(POWER_1)

            # if re.search('T1', line):
                # line = "M649 S" + str(POWER_2)

            # if re.search('T2', line):
                # line = "M649 S" + str(POWER_3)
                            
            # if re.search('T3', line):
                # line = "M649 S" + str(POWER_4)
                
        if re.search('T[0-9]', line):
            extruder = re.search('T[0-9]', line).group()
            currentExtruder = int(re.search('[0-9]', extruder).group())
            line = "M649 S" + str(POWER[currentExtruder])


            #Fix XY motion commands

            if re.search('G1', line) and not(re.search('X', line) or re.search('Y', line) or re.search('Z', line)):
                #Only an extrude - no motion
                line = ''



             
        if re.search('G1', line): #this line involves XY motion

            if re.search('E[0-9.]+', line): #Extrude move

                               
                e_value = re.search('E[0-9.]+', line)
                e_capture = e_value.group(0) #Isolates the "E#.######"
                value_only = float(e_capture[1:]) #Remove the E and convert string to floating pt number

                ##if value_only < EXTRUDE_MIN or re.search('Layer', prevline): #This should actually be a G0 move
                if re.search('Layer', prevline): #This should actually be a G0 move #switched IK 1/11/18
                    line = re.sub('E[0-9.]+', '', line) #Get rid of the extrude
                    line = re.sub('G1', 'G0', line)

                    if re.search('F[0-9.]+', line): #Speed specified
                        line = re.sub('F[0-9.]+','', line) 
                        line = line + "F" + str(TRAVEL_SPEED)

                    else: 
                        line = line + "F" + str(TRAVEL_SPEED)

                elif value_only < EXTRUDE_MIN[currentExtruder]:
                    line = '; - REMOVED - ' + line


                else: #This is a valid extrude move
                    if re.search('F[0-9.]+', line): #Speed specified
                        line = re.sub('F[0-9.]+','', line)
                    
                    line = re.sub('E[0-9.]+', '', line) #Get rid of the extrude
                    line = line + "F" + str(SPEED[currentExtruder])

                
            else: #No extrude; G0 (travel move)
                line = re.sub('G1', 'G0', line)
                
                if re.search('Layer', prevline): #this is the first travel of the layer
                        line = re.sub('F[0-9.]+', 'F4000', line) #Set speed of travel returning to build platform for new layer


 

        #Implement powder handling code
        if re.search('Z', line): #This line has a Z move
            newZ = re.search('(?<=Z)[0-9.]+', line) #captures the Z coordinate of the move
            print 'Current Z:' + str(currentZ)
            print 'New Z:' + str(newZ.group(0))
            #if currentZ == newZ.group(0):
                #print 'match'
            #else:
                #print 'diff'

            if newZ.group(0) == currentZ:
                line = ';Excessive z move removed\n'
                
            else: 
                    
                line = ''
                #NewLayer()
                line = DistributionCode
                currentZ = newZ.group(0)
            #line = ''
        prevline = line


        
        #Add back the carriage return
        line += '\n'
        if line != '\n':
            Munged.write(line)




                

                