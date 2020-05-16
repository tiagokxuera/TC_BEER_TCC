####################################################################
####################################################################
####################################################################
####################################################################
#                                                                  #
#                             ABSTRACT                             #
#                       BEER FACTORY - TC BEER                     #
#                                                                  #
####################################################################
####################################################################
####################################################################
####################################################################





####################################################################
####################################################################
####################################################################
####################################################################
#                                                                  #
#                        Library configuration                     #
#                                                                  #
####################################################################
####################################################################
#First of all, let's configure thingspeak library:
import sys
sys.path.insert(1,'/home/pi/myPythonFiles/mymodules/thingspeak-1.0.0')
####################################################################
#Other libraries imports:
import time
import RPi.GPIO as GPIO
import Adafruit_DHT
import json
import thingspeak
####################################################################
####################################################################
####################################################################
####################################################################





####################################################################
####################################################################
####################################################################
####################################################################
#                                                                  #
#                         HW definition                            #
#                                                                  #
####################################################################
####################################################################

#temperature sensor on GPIO 25
temperatureSensor = 25
#type definition
sensor = Adafruit_DHT.DHT11

#System status LED
systemStatusLED = 13

#Start Stop Button
startStopButton = 21

#Cooler
cooler = 26
coolerRAM = 0

#Cooler Status LED
coolerStatusLED = 16
coolerLEDRAM = 0;

#Heather
heather = 20
heatherRAM = 0;

#Heather Status LED
heatherStatusLED = 19
heatherLEDRAM = 0;

####################################################################
####################################################################
####################################################################
####################################################################





####################################################################
####################################################################
####################################################################
####################################################################
#                                                                  #
#                           HW Initialization                      #
#                                                                  #
####################################################################
####################################################################

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

GPIO.setup(systemStatusLED,GPIO.OUT)  
GPIO.setup(startStopButton,GPIO.IN,pull_up_down=GPIO.PUD_UP)

GPIO.setup(cooler,GPIO.OUT)  
GPIO.setup(coolerStatusLED,GPIO.OUT)  

GPIO.setup(heather,GPIO.OUT)  
GPIO.setup(heatherStatusLED,GPIO.OUT)  

####################################################################
####################################################################
####################################################################
####################################################################





####################################################################
####################################################################
####################################################################
####################################################################
#                                                                  #
#                      Global variables inicialization             #
#                                                                  #
####################################################################
####################################################################

####################################################################
####################################################################
#the system status of aplication. 1 = ON; 0 = OFF
systemStatus = False;

####################################################################
####################################################################
#BUTTON READING VARIABLES STATE MACHINE
OFF_STATE_BUTTON = 10;
ON_STATE_BUTTON = 20;
LOCKED_STATE_BUTTON_ON = 30;
LOCKED_STATE_BUTTON_OFF = 40;
COUNTING_STATE_BUTTON = 50;
TIME_BUTTON_OFF = 500               #5S
LOCK_TIME = 300                     #3s
LOCK_RELEASE_TIME = 200
timerButton = 0;                    #buttonStartStop timer
stateButton = OFF_STATE_BUTTON;

####################################################################
####################################################################
#TEMPERATURE CONTROL
currentTemperature = 25.0;          #temperature at tis moment
timerTemperature = 0;               #used to count frequency
FREQUENCY_TEMPERATURE_READING = 500 #reading each 5s
maxTemperaturePercentage = 1.05     #5% over
minTemperaturePercentage = 0.95     #5% down
targetTemperature = 25.0            #target
timer1s = 0;                        #Generate timer1s

####################################################################
####################################################################
#THINGSPEAK CONTROL
timerThingSpeak = 0;                #used to count frequency
FREQUENCY_THINGSPEAK_READING = 1450 #15s

'''GPIO Channel:
Field1 = startStopButton
Field2 = systemStatusLED
Field3 = currentTemperature
Field4 = cooler
Field5 = coolerStatusLED
Field6 = heather
Field7 = heatherStatusLED
'''
GPIO_WRITE_KEY = "ZOXAWIT42OYRP8Z8";
GPIO_READ_KEY = "FS9XJWHHRD8GJZVV";
GPIO_ID = 998742;
startStopReceived = 0;
clearStartStopReceived = 0;

'''FermentationTime Channel:
Field1 = temperature1
Field2 = time1
Field3 = temperature2
Field4 = time2
Field5 = temperature3
Field6 = time3
Field7 = temperature4
Field8 = time4
'''
FERMENTATION_TIME_WRITE_KEY = "MJLW7MUQEFDVJJYD";
FERMENTATION_TIME_READ_KEY = "85EUJOGNPD9S0WGL";
FERMENTATION_TIME_ID = 998747;

fermentationTemperature1 = 0;
fermentationTemperature2 = 0;
fermentationTemperature3 = 0;
fermentationTemperature4 = 0;
fermentationTime1 = 0;
fermentationTime2 = 0;
fermentationTime3 = 0;
fermentationTime4 = 0;

'''MaturationTime Channel:
Field1 = temperature1
Field2 = time1
Field3 = temperature2
Field4 = time2
Field5 = temperature3
Field6 = time3
Field7 = temperature4
Field8 = time4
'''
MATURATION_TIME_WRITE_KEY = "KUEG7YVXEDWMAF9N";
MATURATION_TIME_READ_KEY = "CMRBBZA87WA315AA";
MATURATION_TIME_ID = 998751;
maturationTemperature1 = 0;
maturationTemperature2 = 0;
maturationTemperature3 = 0;
maturationTemperature4 = 0;
maturationTime1 = 0;
maturationTime2 = 0;
maturationTime3 = 0;
maturationTime4 = 0;

'''stage Channel:
Field1 = timeLasts
Field2 = stage
Field3 = process
'''
STAGE_WRITE_KEY = "RVV2VFH2Q8MF3W9X";
STAGE_READ_KEY = "E0Q0FPKEI9YED8VH";
STAGE_ID = 998756;

#time to finish current stage of process
timeLasts = 0;

#stage: 1, 2, 3 or 4 (0 means nio one)
stage = 0;

#process == 1 means fermentation
#process == 2 means maturation
#process == 0 means no one
process = 2;

OFF_STAGE = 10;
FERMENTATION_1_STAGE = 20;
FERMENTATION_2_STAGE = 30;
FERMENTATION_3_STAGE = 40;
FERMENTATION_4_STAGE = 50;
MATURATION_1_STAGE = 60;
MATURATION_2_STAGE = 70;
MATURATION_3_STAGE = 80;
MATURATION_4_STAGE = 90;

stateStage = OFF_STAGE;

####################################################################
####################################################################
####################################################################
####################################################################





####################################################################
####################################################################
####################################################################
####################################################################
#                                                                  #
#                         STAGE MACHINE                            #
#                                                                  #
####################################################################
####################################################################
def stageMachine():
   global stateStage,OFF_STAGE,FERMENTATION_1_STAGE,systemStatus,timeLasts;
   global FERMENTATION_2_STAGE,FERMENTATION_3_STAGE,FERMENTATION_4_STAGE;
   global targetTemperature, process, stage; 

   #OFF STAGE
   if(stateStage == OFF_STAGE):
      process = 0;
      stage = 0;
      if(systemStatus==True):
         stateStage = FERMENTATION_1_STAGE;
         timeLasts = fermentationTime1;
         targetTemperature = fermentationTemperature1;
         print("Starting Fermentation 1 process...");

   #Fermentation 1 Stage
   if(stateStage == FERMENTATION_1_STAGE):
      process = 1;
      stage = 1;
      if(systemStatus==False):
         stateStage = OFF_STAGE;
      else:
         if(timeLasts <= 0):
            stateStage = FERMENTATION_2_STAGE;
            timeLasts = fermentationTime2;
            targetTemperature = fermentationTemperature2;
            print("Starting Fermentation 2 process..."); 
      
   #Fermentation 2 Stage
   if(stateStage == FERMENTATION_2_STAGE):
      process = 1;
      stage = 2;
      if(systemStatus==False):
         stateStage = OFF_STAGE;
      else:
         if(timeLasts <= 0):
            stateStage = FERMENTATION_3_STAGE;
            timeLasts = fermentationTime3;
            targetTemperature = fermentationTemperature3;
            print("Starting Fermentation 3 process...");

   #Fermentation 3 Stage
   if(stateStage == FERMENTATION_3_STAGE):
      process = 1;
      stage = 3;
      if(systemStatus==False):
         stateStage = OFF_STAGE;
      else:
         if(timeLasts <= 0):
            stateStage = FERMENTATION_4_STAGE;
            timeLasts = fermentationTime4;
            targetTemperature = fermentationTemperature4;
            print("Starting Fermentation 4 process...");             
            
   #Fermentation 4 Stage
   if(stateStage == FERMENTATION_4_STAGE):
      process = 1;
      stage = 4;
      if(systemStatus==False):
         stateStage = OFF_STAGE;
      else:
         if(timeLasts <= 0):
            stateStage = MATURATION_1_STAGE;
            timeLasts = maturationTime1;
            targetTemperature = maturationTemperature1;
            print("Starting Maturation 1 process...");

   #Maturation 1 Stage
   if(stateStage == MATURATION_1_STAGE):
      process = 2;
      stage = 1;
      if(systemStatus==False):
         stateStage = OFF_STAGE;
      else:
         if(timeLasts <= 0):
            stateStage = MATURATION_2_STAGE;
            timeLasts = maturationTime2;
            targetTemperature = maturationTemperature2;
            print("Starting Maturation 2 process...");

   #Maturation 2 Stage
   if(stateStage == MATURATION_2_STAGE):
      process = 2;
      stage = 2;      
      if(systemStatus==False):
         stateStage = OFF_STAGE;
      else:
         if(timeLasts <= 0):
            stateStage = MATURATION_3_STAGE;
            timeLasts = maturationTime3;
            targetTemperature = maturationTemperature3;
            print("Starting Maturation 3 process...");

   #Maturation 3 Stage
   if(stateStage == MATURATION_3_STAGE):
      process = 2;
      stage = 3; 
      if(systemStatus==False):
         stateStage = OFF_STAGE;
      else:
         if(timeLasts <= 0):
            stateStage = MATURATION_4_STAGE;
            timeLasts = maturationTime4;
            targetTemperature = maturationTemperature4;
            print("Starting Maturation 4 process...");

   #Maturation 4 Stage
   if(stateStage == MATURATION_4_STAGE):
      process = 2;
      stage = 4; 
      if(systemStatus==False):
         stateStage = OFF_STAGE;
      else:
         if(timeLasts <= 0):
            stateStage = OFF_STAGE;
            timeLasts = 0;
            targetTemperature = 0;
            systemStatus=False;
            print("PROCESS COMPLETE SUCCESSFULL!");
   
####################################################################
####################################################################
####################################################################
####################################################################





####################################################################
####################################################################
####################################################################
####################################################################
#                                                                  #
#                         UPDATE THINGSPEAK                        #
#                                                                  #
####################################################################
####################################################################
#UPDATE THINGSPEAK CHANNELS
def thingSpeakUpdate():
   global systemStatus,timerThingSpeak,FREQUENCY_THINGSPEAK_READING;
   global currentTemperature,timerThingSpeak,cooler,coolerRAM,coolerLEDRAM;
   global heatherRAM, heatherLEDRAM, startStopReceived, clearStartStopReceived;
   global fermentationTemperature1, fermentationTemperature2, fermentationTemperature3
   global fermentationTemperature4, fermentationTime1, fermentationTime2
   global fermentationTime3, fermentationTime4
   global maturationTemperature1, maturationTemperature2, maturationTemperature3
   global maturationTemperature4, maturationTime1, maturationTime2
   global maturationTime3, maturationTime4, timeLasts, process, stage;

   #Lets prepare data to write
   if(systemStatus==True):
      systemStatusThingSpeak = 1;
   else:
      systemStatusThingSpeak = 0;      
   
   if(timerThingSpeak > FREQUENCY_THINGSPEAK_READING):
      print("--------------------");
      print("Updating ThingSpeak data channels:");
      timerThingSpeak = 0;

      ##################################
      #First Channel: GPIO
      print("GPIO...");
      channel = thingspeak.Channel(id=GPIO_ID,api_key=GPIO_WRITE_KEY);                          
      try:
         if(systemStatus==True):
            if (clearStartStopReceived == 0):
               #if we don't need to clear startStopCommand
               responseWrite = channel.update({'field2':systemStatusThingSpeak, 'field3':currentTemperature, 'field4':coolerRAM, 'field5':coolerLEDRAM, 'field6':heatherRAM, 'field7':heatherLEDRAM})
            else:
               #if we need to clear startStopCommand
               clearStartStopReceived = 0;
               responseWrite = channel.update({'field1':0, 'field2':systemStatusThingSpeak, 'field3':currentTemperature, 'field4':coolerRAM, 'field5':coolerLEDRAM, 'field6':heatherRAM, 'field7':heatherLEDRAM})
            #print('GPIO UPDATED sucessfull!!!');
            #print('JSON response of print:')
            #print(responseWrite)
         else:
            responseWrite = channel.update({'field2':systemStatusThingSpeak,'field3':-999})
            #print('JSON response of print:')
            #print(responseWrite)
      except:
         print('Connection with ThingSpeak Failed in GPIO Channel!!!');

      #now, let's read the startStopButton from thingspeak (field1):
      channelRead = thingspeak.Channel(id=GPIO_ID,api_key=GPIO_READ_KEY);         
      read = channelRead.get_field_last(1);
      #print('JSON received from thingspeak:');
      #print(read);     
      #read is a json. Let's parse it:
      JSONConverted = json.loads(read)
      #print('JSON converted:')                
      #print (JSONConverted)
      startStopButonReceived = JSONConverted["field1"]
      #print('field1 data:')                
      #print (startStopButonReceived)

      if(startStopButonReceived == "1"):
         print('Start/Stop received!');
         startStopReceived = 1;
      #else:
         #print('Start/Stop not received')
      ##################################

      ##################################
      #Secound Channel: FermentationTime
      print("Fermentation Time...");
      channelFermentationRead = thingspeak.Channel(id=FERMENTATION_TIME_ID,api_key=FERMENTATION_TIME_READ_KEY);

      #Fermentation temperature 1
      readFermentation = channelFermentationRead.get_field_last(field="field1"); 
      #readFermentation is a json. Let's parse it:
      JSONFermentationConverted = json.loads(readFermentation)
      fermentationTemperature1 = int(JSONFermentationConverted["field1"]);
      #print("Fermentation Temperature 1 : " + str(fermentationTemperature1));

      #Fermentation time 1
      readFermentation = channelFermentationRead.get_field_last(field="field2"); 
      #readFermentation is a json. Let's parse it:
      JSONFermentationConverted = json.loads(readFermentation)
      fermentationTime1 = int(JSONFermentationConverted["field2"]);
      #print("Fermentation Time 1: " + str(fermentationTime1));

      #Fermentation temperature 2
      readFermentation = channelFermentationRead.get_field_last(field="field3"); 
      #readFermentation is a json. Let's parse it:
      JSONFermentationConverted = json.loads(readFermentation)
      fermentationTemperature2 = int(JSONFermentationConverted["field3"]);
      #print("Fermentation Temperature 2: " + str(fermentationTemperature2));

      #Fermentation time 2
      readFermentation = channelFermentationRead.get_field_last(field="field4"); 
      #readFermentation is a json. Let's parse it:
      JSONFermentationConverted = json.loads(readFermentation)
      fermentationTime2 = int(JSONFermentationConverted["field4"]);
      #print("Fermentation Time 2: " + str(fermentationTime2));
     
      #Fermentation temperature 3
      readFermentation = channelFermentationRead.get_field_last(field="field5"); 
      #readFermentation is a json. Let's parse it:
      JSONFermentationConverted = json.loads(readFermentation)
      fermentationTemperature3 = int(JSONFermentationConverted["field5"]);
      #print("Fermentation Temperature 3: " + str(fermentationTemperature3));

      #Fermentation time 3
      readFermentation = channelFermentationRead.get_field_last(field="field6"); 
      #readFermentation is a json. Let's parse it:
      JSONFermentationConverted = json.loads(readFermentation)
      fermentationTime3 = int(JSONFermentationConverted["field6"]);
      #print("Fermentation Time 3: " + str(fermentationTime3));

      #Fermentation temperature 4
      readFermentation = channelFermentationRead.get_field_last(field="field7"); 
      #readFermentation is a json. Let's parse it:
      JSONFermentationConverted = json.loads(readFermentation)
      fermentationTemperature4 = int(JSONFermentationConverted["field7"]);
      #print("Fermentation Temperature 4: " + str(fermentationTemperature4));

      #Fermentation time 4
      readFermentation = channelFermentationRead.get_field_last(field="field8"); 
      #readFermentation is a json. Let's parse it:
      JSONFermentationConverted = json.loads(readFermentation)
      fermentationTime4 = int(JSONFermentationConverted["field8"]);
      #print("Fermentation Time 4: " + str(fermentationTime4));

      #print('Fermentation UPDATED sucessfull!!!');
      ##################################
     
      ##################################
      #Third Channel: MaturationTime
      print("Maturation Time...");
      channelMaturationRead = thingspeak.Channel(id=MATURATION_TIME_ID,api_key=MATURATION_TIME_READ_KEY);

      #Maturation temperature 1
      readMaturation = channelMaturationRead.get_field_last(field="field1"); 
      #readMaturation is a json. Let's parse it:
      JSONMaturationConverted = json.loads(readMaturation)
      maturationTemperature1 = int(JSONMaturationConverted["field1"]);
      #print("Maturation Temperature 1: " + str(maturationTemperature1));

      #Maturation time 1
      readMaturation = channelMaturationRead.get_field_last(field="field2"); 
      #readMaturation is a json. Let's parse it:
      JSONMaturationConverted = json.loads(readMaturation)
      maturationTime1 = int(JSONMaturationConverted["field2"]);
      #print("Maturation Time 1: " + str(maturationTime1));

      #Maturation temperature 2
      readMaturation = channelMaturationRead.get_field_last(field="field3"); 
      #readMaturation is a json. Let's parse it:
      JSONMaturationConverted = json.loads(readMaturation)
      maturationTemperature2 = int(JSONMaturationConverted["field3"]);
      #print("Maturation Temperature 2: " + str(maturationTemperature2));

      #Maturation time 2
      readMaturation = channelMaturationRead.get_field_last(field="field4"); 
      #readMaturation is a json. Let's parse it:
      JSONMaturationConverted = json.loads(readMaturation)
      maturationTime2 = int(JSONMaturationConverted["field4"]);
      #print("Maturation Time 2: " + str(maturationTime2));

      #Maturation temperature 3
      readMaturation = channelMaturationRead.get_field_last(field="field5"); 
      #readMaturation is a json. Let's parse it:
      JSONMaturationConverted = json.loads(readMaturation)
      maturationTemperature3 = int(JSONMaturationConverted["field5"]);
      #print("Maturation Temperature 3: " + str(maturationTemperature3));

      #Maturation time 3
      readMaturation = channelMaturationRead.get_field_last(field="field6"); 
      #readMaturation is a json. Let's parse it:
      JSONMaturationConverted = json.loads(readMaturation)
      maturationTime3 = int(JSONMaturationConverted["field6"]);
      #print("Maturation Time 3: " + str(maturationTime3));
    
      #Maturation temperature 4
      readMaturation = channelMaturationRead.get_field_last(field="field7"); 
      #readMaturation is a json. Let's parse it:
      JSONMaturationConverted = json.loads(readMaturation)
      maturationTemperature4 = int(JSONMaturationConverted["field7"]);
      #print("Maturation Temperature 4: " + str(maturationTemperature4));

      #Maturation time 4
      readMaturation = channelMaturationRead.get_field_last(field="field8"); 
      #readMaturation is a json. Let's parse it:
      JSONMaturationConverted = json.loads(readMaturation)
      maturationTime4 = int(JSONMaturationConverted["field8"]);
      #print("Maturation Time 4: " + str(maturationTime4));
      #print('Maturation UPDATED sucessfull!!!');
      
      ##################################
      #Fourth Channel: Stage
      print("Stage...");
      if(process==0)or(stage==0):
         timeLasts = 0;
      channelStage = thingspeak.Channel(id=STAGE_ID,api_key=STAGE_WRITE_KEY);                          
      try:
         responseWriteStage = channelStage.update({'field1':timeLasts, 'field2':stage, 'field3':process})
         #print('STAGE UPDATED sucessfull!!!');
      except:
         print('Connection with ThingSpeak Failed in Stage Channel!!!');

      
####################################################################
####################################################################
####################################################################
####################################################################




           
####################################################################
####################################################################
####################################################################
####################################################################
#                                                                  #
#                    READING TEMPERATURE SENSOR                    #
#                                                                  #
####################################################################
####################################################################
#Does the temperature measuring
#Output: currentTemperature
def readTemperature():
   global systemStatus,currentTemperature,timerTemperature
   global targetTemperature,stage,process,timeLasts, coolerRAM,heatherRAM;

   if(timerTemperature > FREQUENCY_TEMPERATURE_READING):
      timerTemperature = 0;
      print("--------------------");
      if(systemStatus==True):
         umid, temp = Adafruit_DHT.read_retry(sensor, temperatureSensor);
         currentTemperature = temp;
         if temp is None:
           print("Temperature sensor measuring error...")
         #else:
         #  print ('Temperatura = {0:0.1f} Graus Celsius'.format(temp));

      #Lets update the system Status:
      if(systemStatus==True):
         print ('System is ON');
         if(process==1):
            print ("Process is Fermentation");
         else:
            print ("Process is Maturation");
         print("Stage: " + str(stage));
         print("Time lasting: " + str(timeLasts) + "s");
         print ('Curret temperature is = {0:0.1f} Degrees'.format(currentTemperature));
         print ('Target temperature is = {0:0.1f} Degrees'.format(targetTemperature));
         if(coolerRAM==1):
            print ("Cooler is ON");
         else:
            print ("Cooler is OFF");
         if(heatherRAM==1):
            print ("Heather is ON");
         else:
            print ("Heather is OFF");
      else:
         print ('System is OFF');
         
     
####################################################################
####################################################################
####################################################################
####################################################################





####################################################################
####################################################################
####################################################################
####################################################################
#                                                                  #
#                    READING BUTTON FUNCTION                       #
#                                                                  #
####################################################################
####################################################################
#Read button function and write systemStaus flag
#one touch -> on
#pressand release -> off
#output: systemStatus
def readStartStopButton():
   global stateButton,OFF_STATE_BUTTON,ON_STATE_BUTTON,LOCKED_STATE_BUTTON_ON
   global timerButton, LOCKED_STATE_BUTTON_OFF, COUNTING_STATE_BUTTON, systemStatus
   global startStopReceived, clearStartStopReceived;

   if((startStopReceived==1)and(stateButton == OFF_STATE_BUTTON)):
      print("turning on after startStopReceived");
      systemStatus = True;
      startStopReceived = 0;
      clearStartStopReceived = 1;
      stateButton = ON_STATE_BUTTON;

   if((startStopReceived==1)and(stateButton == ON_STATE_BUTTON)):
      print("turning off after startStopReceived");
      systemStatus = False;
      startStopReceived = 0;
      clearStartStopReceived = 1;
      stateButton = OFF_STATE_BUTTON;      

   #off
   if(stateButton == OFF_STATE_BUTTON):
      if(GPIO.input(startStopButton)==False):
         systemStatus = True;
         stateButton = LOCKED_STATE_BUTTON_ON;
         timerButton = 0;
         print("Start Button pressed. Starting the process...")

   #waiting release buton
   if(stateButton == LOCKED_STATE_BUTTON_ON):
      if(GPIO.input(startStopButton)==True):         
         stateButton = ON_STATE_BUTTON;

   #on
   if(stateButton == ON_STATE_BUTTON):
      if(GPIO.input(startStopButton)==False):       
         stateButton = COUNTING_STATE_BUTTON;
         timerButton = 0;

   #countig to turn off
   if(stateButton == COUNTING_STATE_BUTTON):
      if(GPIO.input(startStopButton)==True):       
         stateButton = ON_STATE_BUTTON;
      else:
         if(timerButton > TIME_BUTTON_OFF):
            systemStatus = False;
            stateButton = LOCKED_STATE_BUTTON_OFF;
            timerButton = 0;
            print("Stop Button pressed. Droping the process...")

   #waiting release after off
   if(stateButton == LOCKED_STATE_BUTTON_OFF):
      if(GPIO.input(startStopButton)==False):
         timerButton = 0;
      if(timerButton>LOCK_RELEASE_TIME):       
         stateButton = OFF_STATE_BUTTON;       
   
####################################################################
####################################################################   
####################################################################
####################################################################





####################################################################
####################################################################
####################################################################
####################################################################
#                                                                  #
#                 tick system function - 10ms                      #
#                                                                  #
####################################################################
####################################################################
#Pass here each 10ms
def tick():
   global timerButton, timerTemperature,timerThingSpeak,timer1s,timeLasts;   
   timerButton = timerButton + 1;
   timerTemperature = timerTemperature + 1;
   timerThingSpeak = timerThingSpeak + 1;
   timer1s = timer1s +1;
   if(timer1s>100):
      timer1s = 0;
      timeLasts=timeLasts-1;   
   time.sleep(0.010);

####################################################################
####################################################################
####################################################################
####################################################################





####################################################################
####################################################################
####################################################################
####################################################################
#                                                                  #
#                       Main aplication                            #
#                                                                  #
####################################################################
####################################################################

print("Welcome to TC BEER, the beer factory!")
while(1):
   tick();                       #system tick
   readStartStopButton();        #charged of startStopButton
   readTemperature();            #read the temperature sensor
   thingSpeakUpdate();           #Update Thingspeak
   stageMachine();               #controll the stage process
   
####################################################################
####################################################################  
#systemStatusLED: 
   if(systemStatus==True):
      GPIO.output(systemStatusLED, GPIO.HIGH);
   else:
      GPIO.output(systemStatusLED, GPIO.LOW);
####################################################################
####################################################################

####################################################################
####################################################################  
#temperatureControl: 
   if(systemStatus==True):
      if(currentTemperature>(targetTemperature*maxTemperaturePercentage)):
         #if temperature is high:
         GPIO.output(cooler,GPIO.HIGH);
         coolerRAM = 1;
         GPIO.output(coolerStatusLED,GPIO.HIGH);
         coolerLEDRAM = 1;
         GPIO.output(heather,GPIO.LOW);
         heatherRAM = 0;
         GPIO.output(heatherStatusLED,GPIO.LOW);
         heatherLEDRAM = 0;
      else:
         if(currentTemperature<(targetTemperature*minTemperaturePercentage)):
            #if temperature is down:
            GPIO.output(heather,GPIO.HIGH);
            heatherRAM = 1;
            GPIO.output(heatherStatusLED,GPIO.HIGH);
            heatherLEDRAM = 1;
            GPIO.output(cooler,GPIO.LOW);
            coolerRAM = 0;
            GPIO.output(coolerStatusLED,GPIO.LOW);            
            coolerLEDRAM = 0;            
         else:
            #if temperature is ok:
            GPIO.output(heather,GPIO.LOW);
            heatherRAM = 0;            
            GPIO.output(heatherStatusLED,GPIO.LOW);
            heatherLEDRAM = 0;            
            GPIO.output(cooler,GPIO.LOW);
            coolerRAM = 0;
            GPIO.output(coolerStatusLED,GPIO.LOW);
            coolerLEDRAM = 0;                                            
   else:
       GPIO.output(heather,GPIO.LOW);
       heatherRAM = 0;                                            
       GPIO.output(heatherStatusLED,GPIO.LOW);
       heatherLEDRAM = 0;                                                   
       GPIO.output(cooler,GPIO.LOW);
       coolerRAM = 0;
       GPIO.output(coolerStatusLED,GPIO.LOW);
       coolerLEDRAM = 0;                                            
####################################################################
####################################################################      

####################################################################
####################################################################
####################################################################
####################################################################
   
  
