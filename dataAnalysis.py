# DataParser.py
#
# By Matthieu Couturier, April 2008 at McGill University
# Purpose: Do basic data analysis for Eyetracking experiments
# Note: Need to collect data at a sampling rate of 1000

# Modified by Mohsen Akbari, November 27 2009
# Last Modified: 15 Februray 2010

# Variable declaration
import re
import os
import operator
import glob
import time
import shutil


def delete_file_ignore_error(file_name):
    try:
        os.remove(file_name)
    except:
        pass

def manage_expectations(file_produced_by_this_step):
    pass
    # expected = file_produced_by_this_step + '.expected'
    # actual = file_produced_by_this_step
    # 
    # # create temp file without the background column
    # with open(file_produced_by_this_step, 'r') as f:
    #     lines = f.readlines()
    # 
    # headers = lines[0].strip().split('\t')
    # if 'BACKGROUND' in headers:
    #     print "Have to remove the background column"
    #     background_index = 999999
    #     for i, h in enumerate(headers):
    #         if h == 'BACKGROUND':
    #             print "The background is at index ", i
    #             background_index = i
    #             del headers[background_index]
    #             break
    #     actual += '.without_background'
    #     with open(actual, 'w') as out:
    #         out.write('\t'.join(headers) + '\n')
    #         for line in lines[1:]:
    #             line_items = line.strip().split('\t')
    #             del line_items[background_index]
    #             out.write('\t'.join(line_items) + '\n')
    # 
    # print "diff %s %s" % (expected, actual)
    # result = os.system("diff -w --suppress-common-lines %s %s > diff.txt" % (expected, actual))
    # if result == 0:
    #     print "OK"
    # else:
    #     print "NO"
    #     os.system('mate diff.txt')
    #     exit(1)


def remove_bakground_column(inputfilename, outputfilename):
    # create temp file without the background column
    with open(inputfilename, 'r') as f:
        lines = f.readlines()
    
    headers = lines[0].strip().split('\t')
    if 'BACKGROUND' in headers:
        background_index = 999999
        for i, h in enumerate(headers):
            if h == 'BACKGROUND':
                print "The background is at index ", i
                background_index = i
                del headers[background_index]
                break

        with open(outputfilename, 'w') as out:
            out.write('\t'.join(headers) + '\n')
            for line in lines[1:]:
                line_items = line.strip().split('\t')
                del line_items[background_index]
                out.write('\t'.join(line_items) + '\n')

# ---------------- discard Function -------------------------------
def discardPractice(fullFilename,outFilename, pColumn):

    # Open the unedited file
    fResults = open(fullFilename, 'r')
    data = fResults.readlines()
    fResults.close()

    # Remove lines
    data2 = []
    for line in data:
        if (line.split("\t")[pColumn]!="P"):
            data2 += [line]

    # Output the corrected data
    out = open(outFilename, "w")
    for line in data2:
        out.write(line)
    out.close()
    print "Discarded all practice lines: "+fullFilename + " --> " + outFilename
    manage_expectations(outFilename)

# ---------------- sort Function -------------------------------
def sortExcel(inFilename, outFilename):

    SAMPLE_INDEX = 3
    SET = 16
    CONDITION = 17
    NAMEDPICTURE_WORD = 24

    # Open the unsorted file
    fResults = open(inFilename+".xls", 'r')
    data = fResults.readlines()
    fResults.close()

    # Open the output file
    out = open(outFilename+".xls","w")
    
    # Print the header
    out.write(data[0])
    
    # Split the data
    data2 = []
    for i in range(1,len(data)):
        data2 += [data[i].replace("\n","").split("\t")]

    # Convert some of the fields to int for sorting
    for line in data2:
        line[SAMPLE_INDEX] = int(line[SAMPLE_INDEX])
        line[SET] = int(line[SET])

    # Sort the data according to set (15), condition (16),
    # Target/Control(23) and sample_id (3)
    data2 = sorted(data2, key=operator.itemgetter(SET,CONDITION,NAMEDPICTURE_WORD,SAMPLE_INDEX))

    # Convert back to text
    for line in data2:
        line[SAMPLE_INDEX] = "%d"%line[SAMPLE_INDEX]
        line[SET] = "%d"%line[SET]

    # Write the sorted data to file
    for line in data2:
        for word in line:
            out.write(word+"\t")
        out.write("\n")

    # Close the sorted file
    out.close()
    print "Created the sorted file: "  +outFilename+".xls"
    manage_expectations(outFilename+".xls")

# ---------------- Convert function -------------------------------
def convert(edfFilename):
    # run the converter
    os.system("./edf2asc "+edfFilename)
    filename = edfFilename.split(".")[0] 
    print("Created asc file: "+filename+".edf --> "+filename+".asc")

# ---------------- Create the message files 
def createMessageFiles(ascFilename):    
    # Open the text file
    fResults = open(ascFilename, 'r')
    data = fResults.readlines()    
    fResults.close()
    
    filename = ascFilename.split(".")[0] 
    out = open(filename+"_audio.msg","w")
    out2 = open(filename+"_answers.msg","w")

    # File headers:
    out.write("Trial\tAudio_start_time\n")
    out2.write("Trial\tAns_start_time\tAns_latency\tAns\n")

    for line in range(0, len(data)):
        if re.search("APLAYSTART", data[line]):
            splitResults = data[line].strip().replace("\t", " ").split(" ")
            time = (int(splitResults[1])-int(splitResults[2]))
            trial = splitResults[6]
            out.write(trial+"\t%d\n"%time)
        if re.search("IMAGE_CLICK", data[line]):
            splitResults = data[line].strip().replace("\t", " ").split(" ")
            out2.write(trial+"\t"+splitResults[1]+"\t%d\t"%(int(splitResults[1])-time)+splitResults[3][12]+"\n")    
                  
    out.close()
    out2.close()    
    print("Created the audio file: "+filename+"_audio.msg")
    print("Created the answer file: "+filename+"_answers.msg")

    
# ---------------- Analyse function -------------------------------
def analyse(dataFilename, audioFilename, ansFilename, discardWrong, reactionTimeAnalysis, downSampling, timeBins, alignedFlag):    
    # Open the text file
    fResults = open(dataFilename, 'r')
    data = fResults.readlines()    
    fResults.close()
    fResults = open(audioFilename, 'r')
    audioData = fResults.readlines()    
    fResults.close()
    fResults = open(ansFilename, 'r')
    ansData = fResults.readlines()    
    fResults.close()

    # Split the filename
    filename = dataFilename.split(".")[0]
    out = open(filename+"_output.xls","w")

    # Append to right wrong report
    out2 = open ("RW_report.xls","a")
    
    if (reactionTimeAnalysis == 1):
        outReaction = open(filename+"_reaction.xls","w")

    # Variables for the program
    DOWNSAMPLING_RATE = downSampling   # Keep only 1 in every n lines
    SUM_OVER = timeBins                # Sum n lines of data
    HEADER_SIZE = 1                    # Number of lines to discard in the text
    CONDITIONS = ["ED","ND","EFD","FD","P"]    
    MAX_TRIAL_TIME = 3000 # 3 seconds
    WORD_ONSET = 1293

    #--------Modified by Mohsen
    #--------------------------------------

    # Divergence points(ms) for different Sets
    Div_Times = [215, 277, 207, 254, 172, 272, 285, 182, 218, 200, 335, 469, 365, 370, 333, 300, 343, 338, 378, 383]
    
    # Column IDs to use
    Set_ID = 6
    
    #--------------------------------------
       



    
    # Column IDs to use: (Starting at 0)
    TRIAL_ID = 1
    TIMING = 2
    SAMPLE_INDEX = 3
    IA_COLUMN = 4
    RIGHT_IN_SACCADE = 5
    CONDITION = 7
    IMAGE_A = 8
    IMAGE_B = 9
    IMAGE_C = 10
    IMAGE_D = 11
    TRIAL_TARGET = 16   # Named picture, used for R/W
    TARGET = 17         # Same target accross sets
    FR_DIS = 18
    ENG_DIS = 19
    TAR_CTRL = 20
    FR_CTRL = 21
    ENG_CTRL = 22

    itemsPerCondition = [0 for col in range(len(CONDITIONS))]

    # Print the headers for the reaction time file
    if (reactionTimeAnalysis==1):
        outReaction.write("RECORDING_SESSION_LABEL\tTRIAL_LABEL\tR/W\tAns_latency\t")

    # Print the extra headers in the output file
    for line in range(HEADER_SIZE):
        splitResults = data[line].strip().split("\t")
        for i in range(len(splitResults)):
            if (i==RIGHT_IN_SACCADE):
                out.write("In_Saccade\t")                
            elif (i==IA_COLUMN):
                if (SUM_OVER == 1):
                    out.write("IA\tTarget\tFR_DIS\tENG_DIS\tTAR_CTRL\tFR_CTRL\tENG_CTRL\tBACKGROUND\tR/W\tAns\tAns_latency\t")
                else:
                    out.write("SUMMED_OVER\tTarget\tFR_DIS\tENG_DIS\tTAR_CTRL\tFR_CTRL\tENG_CTRL\tBACKGROUND\tR/W\tAns\tAns_latency\t")
            else:
                out.write(splitResults[i]+"\t")
                if (i>=CONDITION-1): # -1 to include the set column
                    outReaction.write(splitResults[i]+"\t")
    out.write("\n")
    outReaction.write("\n")

    # Variables
    startTime = 0   # Start time of the current trial
    trial_id = ""   # Name of the current trial
    correct = ""
    ansLatency = -1
    givenAns = ""
    nWrong = 0
    nRight = 0
    lastLine = ""
    lastLine2 = ""
    tData = [0,0,0,0,0,0,0]
    summed = 0 # Number of lines summed in this bin

    # ------------------ For each line ---------------------------
    for line in range(HEADER_SIZE, len(data)):
        splitResults = data[line].split("\t")
        
        # Remove trailing characters on the lines
        for i in range(len(splitResults)):
            splitResults[i] = splitResults[i].strip()

        # ------------------- Trial level analysis ------------------------------ #
        # Reset the time for each new trial
        if (trial_id != splitResults[TRIAL_ID].split(" ")[1].strip()):
            trial_id = splitResults[TRIAL_ID].split(" ")[1].strip()

            #--------Modified by Mohsen
            #--------------------------------------

            if (alignedFlag == 1):
                # Modify ONSET value based on SET number
                Current_SET_Number = int(splitResults[Set_ID].strip())
                WORD_ONSET_NEW = 1293 + Div_Times[Current_SET_Number - 1]
            else:
                WORD_ONSET_NEW = 1293                

            

            # Print the data left over in the buffer
            if (trial_id != "1" and summed !=0):
                # Fill out the last "normal" line
                out.write(lastLine2)
            
            # Padding the last lines using the last good line line
            lastLine = lastLine+lastLine2
            if (trial_id!="1" and len(lastLine)!=0):
                addedTime = float(lastLine.split("\t")[TIMING])
                while( addedTime<MAX_TRIAL_TIME-WORD_ONSET):
                    # Update the time to be printed in the line
                    addedTime += DOWNSAMPLING_RATE*SUM_OVER
                    lastLine = lastLine.replace("%f"%(addedTime-(DOWNSAMPLING_RATE*SUM_OVER)),"%f"%addedTime)
                    out.write(lastLine)
                    
            # Reset the values used for summing            
            tData = [0,0,0,0,0,0,0]
            summed = 0 # Number of lines summed in this bin
            
            
            # Answer messages
            # Get the answer from the data and from the messages
            for i in range(len(ansData)):
                expectedAns = splitResults[TRIAL_TARGET]
                if (ansData[i].split("\t")[0].strip() == trial_id):
                    ansLatency = ansData[i].split("\t")[2]
                    givenAns = ansData[i].split("\t")[3].strip()
                    if (givenAns.lower() == expectedAns.lower()):
                        correct = "R" # true
                        nRight = nRight+1
                    else:
                        correct = "W" # false
                        nWrong = nWrong+1
            # Audio messages            
            # Get the start time from the audio/message file
            for i in range(len(audioData)):                    
                if (audioData[i].split("\t")[0].strip() == trial_id):
                    startTime =  int(audioData[i].split("\t")[1].strip())
                    for i in range(len(CONDITIONS)):
                        if (CONDITIONS[i]==splitResults[CONDITION]):
                            if (discardWrong == 0 or (discardWrong == 1 and correct == "R")):
                                itemsPerCondition[i] = itemsPerCondition[i]+1

            # Generate the data for the reaction time file
            if (reactionTimeAnalysis==1):
                outReaction.write(splitResults[0]+"\t"+splitResults[TRIAL_ID]+"\t"+correct+"\t"+ansLatency+"\t")
                for i in range(CONDITION-1,len(splitResults)):
                    outReaction.write(splitResults[i]+"\t")
                outReaction.write("\n")
                                  
                                
        # ------------------- Line level analysis ------------------------------ #

        # Compute the start time
        time = float(splitResults[TIMING]) - startTime - WORD_ONSET_NEW

        # Downsample the data
        if (time%DOWNSAMPLING_RATE==0):                        
            # Update the Saccade information
            if (splitResults[RIGHT_IN_SACCADE] == "0"):
                splitResults[RIGHT_IN_SACCADE] = "No"
            else:
                splitResults[RIGHT_IN_SACCADE] = "Yes"

            # Update the IA column
            splitResults[IA_COLUMN] = splitResults[IA_COLUMN].replace("INTERESTAREA_A", "A")
            splitResults[IA_COLUMN] = splitResults[IA_COLUMN].replace("INTERESTAREA_B", "B")
            splitResults[IA_COLUMN] = splitResults[IA_COLUMN].replace("INTERESTAREA_C", "C")
            splitResults[IA_COLUMN] = splitResults[IA_COLUMN].replace("INTERESTAREA_D", "D")

            # Run the data analysis for the Interest areas
            if (time<MAX_TRIAL_TIME-WORD_ONSET and time>-WORD_ONSET):
                k = int((time+WORD_ONSET)/DOWNSAMPLING_RATE)        
                if(splitResults[IA_COLUMN]=="A"):
                    if (splitResults[RIGHT_IN_SACCADE]=="No" and (discardWrong==0 or (discardWrong==1 and correct=="R"))):
                        for j in range(0,len(CONDITIONS)):
                            if (CONDITIONS[j] == splitResults[CONDITION]):                                
                                if (splitResults[TARGET].split(".")[0]==splitResults[IMAGE_A].split(".")[0]):                        
                                    tData[0] += 1
                                if (splitResults[FR_DIS].split(".")[0]==splitResults[IMAGE_A].split(".")[0]):                        
                                    tData[1] += 1
                                if (splitResults[ENG_DIS].split(".")[0]==splitResults[IMAGE_A].split(".")[0]):                        
                                    tData[2] += 1
                                if (splitResults[TAR_CTRL].split(".")[0]==splitResults[IMAGE_A].split(".")[0]):                        
                                    tData[3] += 1
                                if (splitResults[FR_CTRL].split(".")[0]==splitResults[IMAGE_A].split(".")[0]):                        
                                    tData[4] += 1
                                if (splitResults[ENG_CTRL].split(".")[0]==splitResults[IMAGE_A].split(".")[0]):                        
                                    tData[5] += 1          
                elif(splitResults[IA_COLUMN]=="B"):            
                    if (splitResults[RIGHT_IN_SACCADE]=="No" and (discardWrong==0 or (discardWrong==1 and correct=="R"))):
                        for j in range(0,len(CONDITIONS)):
                            if (CONDITIONS[j] == splitResults[CONDITION]):                                
                                if (splitResults[TARGET].split(".")[0]==splitResults[IMAGE_B].split(".")[0]):                        
                                    tData[0] += 1
                                if (splitResults[FR_DIS].split(".")[0]==splitResults[IMAGE_B].split(".")[0]):                        
                                    tData[1] += 1
                                if (splitResults[ENG_DIS].split(".")[0]==splitResults[IMAGE_B].split(".")[0]):                        
                                    tData[2] += 1
                                if (splitResults[TAR_CTRL].split(".")[0]==splitResults[IMAGE_B].split(".")[0]):                        
                                    tData[3] += 1
                                if (splitResults[FR_CTRL].split(".")[0]==splitResults[IMAGE_B].split(".")[0]):                        
                                    tData[4] += 1
                                if (splitResults[ENG_CTRL].split(".")[0]==splitResults[IMAGE_B].split(".")[0]):                        
                                    tData[5] += 1         
                elif(splitResults[IA_COLUMN]=="C"):
                    if (splitResults[RIGHT_IN_SACCADE]=="No" and (discardWrong==0 or (discardWrong==1 and correct=="R"))):
                        for j in range(0,len(CONDITIONS)):
                            if (CONDITIONS[j] == splitResults[CONDITION]):      
                                if (splitResults[TARGET].split(".")[0]==splitResults[IMAGE_C].split(".")[0]):                                            
                                    tData[0] += 1
                                if (splitResults[FR_DIS].split(".")[0]==splitResults[IMAGE_C].split(".")[0]):                        
                                    tData[1] += 1
                                if (splitResults[ENG_DIS].split(".")[0]==splitResults[IMAGE_C].split(".")[0]):                        
                                    tData[2] += 1
                                if (splitResults[TAR_CTRL].split(".")[0]==splitResults[IMAGE_C].split(".")[0]):                        
                                    tData[3] += 1
                                if (splitResults[FR_CTRL].split(".")[0]==splitResults[IMAGE_C].split(".")[0]):                        
                                    tData[4] += 1
                                if (splitResults[ENG_CTRL].split(".")[0]==splitResults[IMAGE_C].split(".")[0]):                        
                                    tData[5] += 1
                elif(splitResults[IA_COLUMN]=="D"):
                    if (splitResults[RIGHT_IN_SACCADE]=="No" and (discardWrong==0 or (discardWrong==1 and correct=="R"))):
                        for j in range(0,len(CONDITIONS)):
                            if (CONDITIONS[j] == splitResults[CONDITION]):                                                           
                                if (splitResults[TARGET].split(".")[0]==splitResults[IMAGE_D].split(".")[0]):                        
                                    tData[0] += 1
                                if (splitResults[FR_DIS].split(".")[0]==splitResults[IMAGE_D].split(".")[0]):                        
                                    tData[1] += 1
                                if (splitResults[ENG_DIS].split(".")[0]==splitResults[IMAGE_D].split(".")[0]):                        
                                    tData[2] += 1
                                if (splitResults[TAR_CTRL].split(".")[0]==splitResults[IMAGE_D].split(".")[0]):                        
                                    tData[3] += 1
                                if (splitResults[FR_CTRL].split(".")[0]==splitResults[IMAGE_D].split(".")[0]):                        
                                    tData[4] += 1
                                if (splitResults[ENG_CTRL].split(".")[0]==splitResults[IMAGE_D].split(".")[0]):                        
                                    tData[5] += 1
                                
                else:
                    if (splitResults[RIGHT_IN_SACCADE]=="No" and (discardWrong==0 or (discardWrong==1 and correct=="R"))):
                        tData[6] += 1
                        
            # Go through one item at a time
            for i in range(len(splitResults)):                                
                # Don't do anything if out of the time range we are interested in
                if (time<MAX_TRIAL_TIME-WORD_ONSET and time>-WORD_ONSET):                    
                    if (i==0):
                        summed += 1 # Reached a new line
                        if (summed == 1):
                            lastLine = ""
                    # Reached the last item of the block
                    if (i == len(splitResults)-1 and SUM_OVER+1 == summed):
                        out.write(splitResults[i]+"\n")
                        lastLine2 += splitResults[i]+"\n"
                        summed = 0
                        # Target FR_DIS ENG_DIS TAR_CTRL FR_CTRL ENG_CTRL
                        tData = [0,0,0,0,0,0,0]                        
                    if (i==TIMING):
                        if (summed == 1):
                            out.write("%f\t"%(time))
                            lastLine += "%f\t"%(time)
                    elif  (i<4):
                        if (summed == 1):
                            out.write(splitResults[i]+"\t")
                            lastLine += splitResults[i]+"\t"
                    elif (i==IA_COLUMN):                                                
                        if (summed == 1 and SUM_OVER == 1): # Only print IA if not summing lines
                            out.write(splitResults[IA_COLUMN]+"\t")
                            lastLine += splitResults[IA_COLUMN]+"\t"                                                                                                
                    else:
                        if (summed == SUM_OVER):
                            lastLine2 = ""
                            if (SUM_OVER == 1):
                                out.write("%d\t%d\t%d\t%d\t%d\t%d\t%d\t"%(tData[0],tData[1],tData[2],tData[3],tData[4],tData[5],tData[6]))
                                lastLine2 += "%d\t%d\t%d\t%d\t%d\t%d\t%d\t"%(tData[0],tData[1],tData[2],tData[3],tData[4],tData[5],tData[6])
                            else:
                                out.write("%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t"%(summed, tData[0],tData[1],tData[2],tData[3],tData[4],tData[5],tData[6]))
                                lastLine2 += "%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t"%(summed,tData[0],tData[1],tData[2],tData[3],tData[4],tData[5],tData[6])
                            out.write(correct+"\t"+givenAns+"\t"+ansLatency+"\t")
                            lastLine2 += correct+"\t"+givenAns+"\t"+ansLatency+"\t"
                            summed = SUM_OVER+1 
                        if (summed == SUM_OVER+1):
                            out.write(splitResults[i]+"\t")
                            lastLine2 += splitResults[i]+"\t"

    
    # Pad the last trial in the file
    # Print the data left over in the buffer
    if (trial_id != "1" and summed !=0):
        # Fill out the last "normal" line
        out.write(lastLine2)
    
    # Padding the last lines using the last good line line
    lastLine = lastLine+lastLine2
    if (trial_id!="1" and len(lastLine)!=0):
        addedTime = float(lastLine.split("\t")[TIMING])
        while( addedTime<MAX_TRIAL_TIME-WORD_ONSET):
            # Update the time to be printed in the line
            addedTime += DOWNSAMPLING_RATE*SUM_OVER
            lastLine = lastLine.replace("%f"%(addedTime-(DOWNSAMPLING_RATE*SUM_OVER)),"%f"%addedTime)
            out.write(lastLine)

    out.close()
    print("Created the output file: "+filename+"_output.xls")
    manage_expectations(filename+"_output.xls")
    
    if (reactionTimeAnalysis==1):
        outReaction.close()
        print("Created the reaction time file: "+filename+"_reaction.xls")
        manage_expectations(filename+"_reaction.xls")

    # Print the right wrong report
    out2.write(splitResults[0]+"\t%d\t%d\t%d\n"%(nRight,nWrong,(nRight+nWrong)))
    out2.close()
    print("Appended to the RW report: RW_report.xls")


# ---------------- substract Function -------------------------------
def substract(inFilename, outFilename):
    
    # Open the unsubstracted file
    fResults = open(inFilename, 'r')
    data = fResults.readlines()
    fResults.close()

    # Open the output file
    out =open(outFilename, "w")

    # Print the header
    headers = [0,1,2,4,5,6,7,8,9,10,11,15,16,17,18,19,20,22,23,24,32,33,34,35,36,37,38,39,41]
    headerLine = data[0].replace("\n","").split("\t")    
    for h in headers:
        out.write(headerLine[h]+"\t")
    out.write("\n")
    merge = [1,11,23,24]   
    # Variables
    TARGET = 23

    # Run over each set
    target = []
    control = []
    substracted = []
    state  = 0 # 0 target is empty
               # 1 target is starting to fill up
               
    for i in range(1, len(data)):
        splitResults = data[i].replace("\n","").split("\t")
        
        # Read the control into a temp list
        if (splitResults[TARGET]=="control"):                                    
            if (state == 1): # Looped back around to a new trial
                # Substract the lines
                substracted = []
                for j in range(len(target)):
                    # Columns 5,6,7,8,9,10
                    sub = [0,0,0,0,0,0]
                    sub[0] = int(target[j][5])-int(control[j][5])
                    sub[1] = int(target[j][6])-int(control[j][6])
                    sub[2] = int(target[j][7])-int(control[j][7])
                    sub[3] = int(target[j][8])-int(control[j][8])
                    sub[4] = int(target[j][9])-int(control[j][9])
                    sub[5] = int(target[j][10])-int(control[j][10])
                    # Merged data
                    merged = ["","","",""]
                    merged[0] = target[j][1]+"/"+control[j][1].split(" ")[1]
                    merged[1] = target[j][11]+"/"+control[j][11]
                    merged[2] = target[j][23]+"/"+control[j][23]
                    merged[3] = target[j][24]+"/"+control[j][24]
                    substracted += [[target[j][0],merged[0],target[j][2],target[j][4],
                                     "%d"%sub[0],"%d"%sub[1],"%d"%sub[2],"%d"%sub[3],"%d"%sub[4],"%d"%sub[5],                        
                                     merged[1],target[j][15],target[j][16],target[j][17],target[j][18],
                                     target[j][19],target[j][20],target[j][22]
                                     ,merged[2],merged[3],
                                     target[j][32],target[j][33],target[j][34],target[j][35],target[j][36],
                                     target[j][37],target[j][38],target[j][39], target[j][42]]]                                                
                # Print the data
                for line in substracted:
                    for word in line:
                        out.write(word+"\t")
                    out.write("\n")
                # Empty the temp buffers
                state = 0 # reset to 0                
                control = []
                target = []
            # Add to control
            control += [splitResults]
        # Read the target into a temp list
        else:
            state = 1
            # Add to target
            target += [splitResults]

    # Close the output file
    out.close()
    print "Substracted the data: " +inFilename+ " --> " + outFilename
    
# ---------------- noSubstract Function -------------------------------
def noSubstract(inFilename, outFilename, split):
    
    # Open the unsubstracted file
    fResults = open(inFilename, 'r')
    data = fResults.readlines()
    fResults.close()

    # Open the output file
    out =open(outFilename, "w")

    # Print the header
    # headers = [0,1,2,4,5,6,7,8,9,10,11,15,16,17,18,19,20,22,23,24,32,33,34,35,36,37,38,39,41]
    headers = [0,1,2,4,5,6,7,8,9,10,11,12,16,17,18,19,20,21,23,24,25,33,34,35,36,37,38,39,40,42]
    headerLine = data[0].replace("\n","").split("\t")
    for h in headers:
        out.write(headerLine[h]+"\t")
    out.write("\n")

    CONDITION = 17
    NAMEDPICTURE_NATURE = 24

    for i in range(1, len(data)):
        splitResults = data[i].replace("\n","").split("\t")
        if (split==1):
            if (splitResults[NAMEDPICTURE_NATURE]=="control"):
                splitResults[CONDITION] +="-C"
            else:
                splitResults[CONDITION] +="-T"
        for j in headers:
            out.write(splitResults[j]+"\t")
        out.write("\n");        

    # Close the output file
    out.close()
    print "Did not substract the data but reordered the columns: " +inFilename+ " --> " + outFilename
    manage_expectations(outFilename)
    
# ---------------- Prepare for Averaging Function -------------------------------
def prepareForAveraging(inFilename, outFilename):
    # Open the first file
    fResults = open(inFilename, 'r')
    data = fResults.readlines()
    fResults.close()
    
    # Open the output file
    out = open(outFilename, "w")

    # Print the header
    headers = [1,2,3,4,5,6,7,8,9,10,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29]
    headerLine = data[0].split("\t")
    out.write("AVERAGED_OVER\t")
    for h in headers:
        out.write(headerLine[h]+"\t")
    out.write("\n")

    # Print the data
    for i in range(1,len(data)):
        splitResults = data[i].replace("\n","").split("\t")
        out.write(splitResults[0])
        for j in headers:
            out.write("\t" + splitResults[j])
        out.write("\n")
    out.close()
    print "Ready for merge: " + inFilename + " --> " + outFilename
    manage_expectations(outFilename)

# ---------------- Discard Trials with Wrong Answers Function ------------------------------
def removeWrongAnswers(inFilename, reactionFile, outFilename):

    TRIAL_LABEL_COL = 1
    RIGHT_OR_WRONG_COL = 2
    CONDITION_COL = 11
    discardList = []
    
    # Open the input file
    fResults = open(inFilename, 'r')
    headerline = fResults.readline()
    data = fResults.readlines()
    fResults.close()

    fResults = open(reactionFile, 'r')
    dataReaction = fResults.readlines()
    fResults.close()


    # Remove trials with wrong answers
    data2 = [headerline]
    for line in data:
        trial_id = line.split("\t")[TRIAL_LABEL_COL]
        condition = line.split("\t")[CONDITION_COL]
        trialNumber = trial_id.split(":")[1].strip()
        for i in range(len(dataReaction)):
            if (dataReaction[i].split("\t")[TRIAL_LABEL_COL].strip() == trial_id):
                RightOrWrong = dataReaction[i].split("\t")[RIGHT_OR_WRONG_COL].strip()
           
        if (RightOrWrong == "R"):
            data2 += [line]
        else:
            if [trialNumber, condition] not in discardList:
                discardList.append([trialNumber, condition])

    # Output the corrected data
    out = open(outFilename, "w")
    for line in data2:
        out.write(line)
    out.close()
    print "Discarded all Trials with Incorrect Answers: "+inFilename + " --> " + outFilename
    manage_expectations(outFilename)
    return discardList




# ---------------- Discard Trials with no Fixation Function ------------------------------
def discardNoFixation(inFilename, outFilename):

    TRIAL_ID = 1
    TARGET_COL = 4
    TAR_CTRL_COL = 7
    CONDITION_COL = 12
    NAMEPICTURE_NATURE_COL = 18
    discardThisTrial = False
    discardList = []


    
    #Open the input file
    fResults = open(inFilename, 'r')
    headerline = fResults.readline()
    data = fResults.readlines()
    fResults.close()

    # Specify the trials with no fixations
    trial_id = ""
    for line in data:
        if (trial_id != line.split("\t")[TRIAL_ID].strip()):
            if (discardThisTrial == True):
                discardList.append([trialNumber, condition])
            trial_id = line.split("\t")[TRIAL_ID].strip()
            trialNumber = trial_id.split(":")[1].strip()
            condition = line.split("\t")[CONDITION_COL]
            targetOrcontrol = line.split("\t")[NAMEPICTURE_NATURE_COL].strip()
            discardThisTrial = True

        if (targetOrcontrol == 'control' and discardThisTrial == True):
            if (line.split("\t")[TAR_CTRL_COL].strip() != '0'):
                discardThisTrial = False
        elif (targetOrcontrol == 'target' and discardThisTrial == True):
            if (line.split("\t")[TARGET_COL].strip() != '0'):
                discardThisTrial = False

    # Check the last trial in the file
    if (discardThisTrial == True):
        discardList.append([trialNumber, condition])
    


    # Remove Trials with no fixations
    data2 = [headerline]
    for line in data:
        trial_id = line.split("\t")[TRIAL_ID].strip()
        trialNumber = trial_id.split(":")[1].strip()
        condition = line.split("\t")[CONDITION_COL]
        if ([trialNumber, condition] not in discardList):
            data2 += [line]    
    
    # Output the corrected data
    out = open(outFilename, "w")
    for line in data2:
        out.write(line)
    out.close()
    print "Discarded all Trials with No Fixations: "+inFilename + " --> " + outFilename
    manage_expectations(outFilename)
    return discardList

# ---------------- Discard Trials  with Low Answer Latency Function ------------------------------
def discardLowLatencyAnswer(inFilename, reactionFile, outFilename, latencyTh):
    TRIAL_LABEL_COL = 1
    ANS_LATENCY_COL = 3
    CONDITION_COL = 12
    discardList = []



    # Open the input file
    fResults = open(inFilename, 'r')
    headerline = fResults.readline()
    data = fResults.readlines()
    fResults.close()

    fResults = open(reactionFile, 'r')
    dataReaction = fResults.readlines()
    fResults.close()

    
    # Remove trials with wrong answers
    data2 = [headerline]
    for line in data:
        trial_id = line.split("\t")[TRIAL_LABEL_COL]
        trialNumber = trial_id.split(":")[1].strip()
        condition = line.split("\t")[CONDITION_COL]
        for i in range(len(dataReaction)):
            if (dataReaction[i].split("\t")[TRIAL_LABEL_COL].strip() == trial_id):
                currentLatency = int(dataReaction[i].split("\t")[ANS_LATENCY_COL].strip())
           
        if (currentLatency > int(latencyTh)):
            data2 += [line]
        else:
            if [trialNumber, condition] not in discardList:
                discardList.append([trialNumber, condition])
            
        
    # Output the corrected data
    out = open(outFilename, "w")
    for line in data2:
        out.write(line)
    out.close()
    print "Discarded all Trials with Low Latency Answers: "+inFilename + " --> " + outFilename
    manage_expectations(outFilename)
    return discardList

# ---------------- Discard Trials with Prefixaiton Function ------------------------------
def discardPreFixtion(inFilename, outFilename, timeRange, rangeSize, colSel, alignedFlag):

    TRIAL_ID = 1
    TIMESTAMP = 2
    TARGET_COL = 4
    FRDis_COL = 5
    ENGDis_COL = 6
    TAR_CTRL_COL = 7
    CONDITION_COL = 12
    NAMEPICTURE_NATURE_COL = 18
    
    discardThisTrial = False
    controlFlag = False
    discardList = []

    Selected_Columns = []
    Column_Counter = []
    if (int(colSel[0]) == 1):
        Selected_Columns = Selected_Columns + [TARGET_COL]
        Column_Counter = Column_Counter + [0]
    if (int(colSel[1]) == 1):
        Selected_Columns = Selected_Columns + [FRDis_COL]
        Column_Counter = Column_Counter + [0]
    if (int(colSel[2]) == 1):
        Selected_Columns = Selected_Columns + [ENGDis_COL]
        Column_Counter = Column_Counter + [0]

    if (int(colSel[3]) == 1):
        controlFlag = True

    controlCounter = 0
    
    if (Selected_Columns == [] and controlFlag == False):
        return discardList

    InitialLowBound = timeRange[0]
    InitialUpBound = timeRange[1]
    lowBound = InitialLowBound
    upBound = InitialUpBound
    

    #Open the input file
    fResults = open(inFilename, 'r')
    headerline = fResults.readline()
    data = fResults.readlines()
    fResults.close()

    # Divergence points(ms) for different Sets
    Div_Times = [199, 293, 200, 255, 172, 272, 285, 182, 250, 200, 330, 518, 379, 370, 335, 310, 306, 376, 367, 378]

    # Column IDs to use
    Set_ID = 10


    # Specify the trials with pre fixations
    trial_id = ""
    for line in data:
        if (trial_id != line.split("\t")[TRIAL_ID].strip()):
            ## if data has been aligned based on the divergence points
            if (alignedFlag == 1):
            # Modify lowBound and upBound value based on SET number
                Current_SET_Number = int(line.split("\t")[Set_ID].strip())
                lowBound = int(InitialLowBound) - int(Div_Times[Current_SET_Number - 1])
                upBound = int(InitialUpBound) - int(Div_Times[Current_SET_Number - 1])

            for i in range(len(Column_Counter)):
                if (int(Column_Counter[i]) >= int(rangeSize)):
                    print [trial_id, Column_Counter[i]]
                    discardThisTrial = True
                Column_Counter[i] = 0
                
            if (int(controlCounter) >= int(rangeSize)):
                discardThisTrial = True
            controlCounter = 0
            
            if (discardThisTrial == True):
                discardList.append([trialNumber, condition])

            ## updating the trial ID
            trial_id = line.split("\t")[TRIAL_ID].strip()
            trialNumber = trial_id.split(":")[1].strip()
            condition = line.split("\t")[CONDITION_COL]
            targetOrcontrol = line.split("\t")[NAMEPICTURE_NATURE_COL].strip()
            discardThisTrial = False



        currentTime = line.split("\t")[TIMESTAMP]
        if  (int(float(currentTime)) >= int(lowBound) and (int(float(currentTime)) <= int(upBound))):
            if (targetOrcontrol == 'target'):
                for index, column in enumerate(Selected_Columns):
                    if (int(Column_Counter[index]) < int(rangeSize)):
                        if (line.split("\t")[column].strip() == '1'):
                            Column_Counter[index] += 1
                        elif (line.split("\t")[column].strip() == '0'):
                            Column_Counter[index] = 0
                        else:
                            print "Error in discardPreFixtion function (target)."
                            print "The value of the input file can be either '0' or '1'."
                    
                    
            elif (targetOrcontrol == 'control' and controlFlag == True):
                if (int(controlCounter) < int(rangeSize)):
                    if (line.split("\t")[TAR_CTRL_COL].strip() == '1'):
                        controlCounter +=1
                    elif (line.split("\t")[TAR_CTRL_COL].strip() == '0'):
                        controlCounter = 0
                    else:
                        print "Error in discardPreFixtion function (control)."
                        print "The value of the input file can be either '0' or '1'."



    # Check the last trial in the file
    for i in range(len(Column_Counter)):
        if (int(Column_Counter[i]) >= int(rangeSize)):
            discardThisTrial = True
 
    if (int(controlCounter) >= int(rangeSize)):
        discardThisTrial = True
    
    if (discardThisTrial == True):
        discardList.append([trialNumber, condition])

    # Remove Trials with no fixations
    data2 = [headerline]
    for line in data:
        trial_id = line.split("\t")[TRIAL_ID].strip()
        trialNumber = trial_id.split(":")[1].strip()
        condition = line.split("\t")[CONDITION_COL]
        if ([trialNumber, condition] not in discardList):
            data2 += [line]    
    
    # Output the corrected data
    out = open(outFilename, "w")
    for line in data2:
        out.write(line)
    out.close()
    print "Discarded all Trials with Prefixations: "+inFilename + " --> " + outFilename
    manage_expectations(outFilename)
    return discardList

# ---------------- Compute the total number of trials in the input file ------------------------------
def computeTotaltrials(inFilename):
    TRIAL_ID = 1
    
    fResults = open(inFilename, 'r')
    headerline = fResults.readline()

    trialCounter = 0    
    trial_id = ""
    for line in fResults:
        if (trial_id != line.split("\t")[TRIAL_ID].strip()):
            trial_id = line.split("\t")[TRIAL_ID].strip()
            trialCounter +=1

    fResults.close()
    return trialCounter


    
# ---------------- Generate log file of discarded trials ------------------------------
def discardedLogGenerator(name, outFilename, wrongList, nofixList, lowList, prefixList, latencyTh, trialNum, opList):

    TRIAL_ID = 1
    RIGHT_OR_WRONG_COL = 2

    RW_OPTION_INDEX = 2
    NOFIX_OPTION_INDEX = 3
    LAT_OPTION_INDEX = 4
    PREFIXATION_OPTION_INDEX = 5

    RWstatus = 'No'
    NoFix = 'No'
    LATstatus = 'No'
    PreFixationStatus = 'No'
    
    if opList[RW_OPTION_INDEX] == 1:
        RWstatus = 'Yes'
    if opList[NOFIX_OPTION_INDEX] == 1:
        NoFix = 'Yes'
    if opList[LAT_OPTION_INDEX] == 1:
        LATstatus = 'Yes'
    if opList[PREFIXATION_OPTION_INDEX ] == 1:
        PreFixationStatus = 'Yes'

    Condition_List = ['ED-T','ED-C', 'ND-T', 'ND-C', 'FD-T','FD-C', 'EFD-T', 'EFD-C']
    RWconditionNumber = [0, 0, 0, 0, 0, 0, 0, 0]
    NOFIXconditionNumber = [0, 0, 0, 0, 0, 0, 0, 0]
    LATconditionNumber = [0, 0, 0, 0, 0, 0, 0, 0]
    PreFixationNumber = [0, 0, 0, 0, 0, 0, 0, 0]

    totalRemoved = len(wrongList) + len(nofixList) + len(lowList) + len(prefixList)

    for condition in Condition_List:
        for item in wrongList:
            if item[1] == condition:
                RWconditionNumber[Condition_List.index(condition)] +=1


    for condition in Condition_List:
        for item in nofixList:
            if item[1] == condition:
                NOFIXconditionNumber[Condition_List.index(condition)] +=1
    
   
    for condition in Condition_List:
        for item in lowList:
            if item[1] == condition:
                LATconditionNumber[Condition_List.index(condition)] +=1

    for condition in Condition_List:
        for item in prefixList:
            if item[1] == condition:
                PreFixationNumber[Condition_List.index(condition)] +=1

        
    if LATstatus == 'No':
        header = "Participant\t" + "Total Number of Trials\t" + "RW Discarded Trials (" + str(RWstatus) + ")\t"
        for condition in Condition_List:
            header = header + "RW Discarded-" + str(condition) + "\t"

        header = header + "NoFix Discarded Trials ("  + str(NoFix) +")\t"
        for condition in Condition_List:
            header = header + "NoFix Discarded-" + str(condition) + "\t"

        header = header + "LAT Discarded Trials (" + str(LATstatus) +  ")\t"
        for condition in Condition_List:
            header = header + "LAT Discarded-" + str(condition) + "\t"

        header = header + "PreFixation Discarded Trials (" + str(PreFixationStatus) +  ")\t"
        for condition in Condition_List:
            header = header + "PreFixation Discarded-" + str(condition) + "\t"


        header = header + "Total Number of Discarded Trials\n"

    else:
        header = "Participant\t" + "Total Number of Trials\t" + "RW Discarded Trials (" + str(RWstatus) + ")\t"
        for condition in Condition_List:
            header = header + "RW Discarded-" + str(condition) + "\t"

        header = header + "NoFix Discarded Trials ("  + str(NoFix) +")\t"
        for condition in Condition_List:
            header = header + "NoFix Discarded-" + str(condition) + "\t"

        header = header + "LAT Discarded Trials (" + str(latencyTh) +  ")\t"
        for condition in Condition_List:
            header = header + "LAT Discarded-" + str(condition) + "\t"


        header = header + "PreFixation Discarded Trials (" + str(PreFixationStatus) +  ")\t"
        for condition in Condition_List:
            header = header + "PreFixation Discarded-" + str(condition) + "\t"


        header = header + "Total Number of Discarded Trials\n"

    
   
    # Check if the output log file is empty or not    
    try:
        out = open(outFilename, 'r')
    # If it is, write the header into it
    except IOError:
        out = open(outFilename, 'w')
        out.write(header)

    out.close()

    out = open(outFilename, 'a')
    out.write(str(name) + "\t")

    out.write(str(trialNum) + "\t")

    out.write(str(len(wrongList)) + "\t")
    for condition in Condition_List:
        out.write(str(RWconditionNumber[Condition_List.index(condition)]) + "\t")
          
    out.write(str(len(nofixList)) + "\t")
    for condition in Condition_List:
         out.write(str(NOFIXconditionNumber[Condition_List.index(condition)]) + "\t")
            
   
    out.write(str(len(lowList)) + "\t")
    for condition in Condition_List:
        out.write(str(LATconditionNumber[Condition_List.index(condition)]) + "\t")


    out.write(str(len(prefixList)) + "\t")
    for condition in Condition_List:
        out.write(str(PreFixationNumber[Condition_List.index(condition)]) + "\t")

    out.write(str(totalRemoved) + "\n")
    out.close()
    print "Log file of discarded trials was generated:" + " --> " + outFilename

def getCurrentFixation(line_elements):
    current_fix = 0
    for fix_index in [4,5,6,7,8,9,10]:
        if line_elements[fix_index] == '1':
            return fix_index
    return 0
            

def expandFixations(inputFile, outputFile):
    with open(inputFile, 'r') as inFile:
        lines = []
        for line in inFile.readlines():
            lines.append(line.strip().split('\t'))
    
    i = len(lines) - 1
    last_fix = 0
    while i > 0:
        line = lines[i]
        current_fix = getCurrentFixation(line)
        if current_fix == 0:
            if last_fix != 0:
                line[last_fix] = '1'
        else:
            last_fix = current_fix
        i -= 1
    
    with open(outputFile, 'w') as outFile:
        for elements in lines:
            outFile.write('\t'.join(elements) + '\n')
            
    manage_expectations(inputFile)

# ---------------- Cleanup Function -------------------------------
def cleanup(filename):
    delete_file_ignore_error(filename+"_audio.msg")
    delete_file_ignore_error(filename+"_answers.msg")
    # delete_file_ignore_error(filename+".asc")
    delete_file_ignore_error(filename+"_removedP.xls")
    delete_file_ignore_error(filename+"_removedP_output.xls")
    delete_file_ignore_error(filename+"_removedP_output_sorted.xls")
    delete_file_ignore_error(filename+"_substractedData.xls")
    delete_file_ignore_error(filename+"_notSubstractedData.xls")

#------------------- Start sequence ----------------------------#

# Program options

discardWrong = 1 # 1 = true, 0 = false

## Note(Mohsen): Although it seems there is discardWrong parameter for discarding the trials with
## wrong answers, it does not do so. As a result a new parameter and a function are difined
## for performing this task.

iswrongRemoved = 1 # 1 = true: the wrong answers will be removed, 0 = false: the wrong answers will be kept
noFixationRemoval = 1 #1 = true: the trials where there is no fixation will be discarded. 0 = false
lowAnswerLatency = 1 # 1= true: the trials with answer latency less than thereshold will be discarded.
latencyThreshold = 100
preFixationRemoval = 1#1 = true: the trials with prefixations will be discarded. 0 = false

reactionTimeAnalysis = 1 # 1 = true, 0 = false
downSampling = 1
timeBins = 10
alignedFlag = 1
batchMode = 0
isSubstract = 1 # Are we going to substract the data or not?
                # 1 = true, 0 = false
split = 0       # If we are not substracting should we split the data
                # in target and control groups?
                # 1 = true, 0 = false    

WrongAnswersList = []
NoFixationList = []
LowLatencyAnswerList = []
PrefixationList = []
SelectedColumns = []
lowerBound = 0
upperBound = 0
rangeSize = 0

currentInputFileName = ""
currentOutputFileName = ""
# Running the program
name = raw_input("Name of the file to analyse (type O for Options) : ")
if (name == "O"):
    alignedFlag = int(raw_input("Do you want to align the data based on set divergence points? (0-No, 1-Yes): "))
    batchMode = int(raw_input("Do you want to run the program in batch mode? (0-No, 1-Yes): "))
    iswrongRemoved = int(raw_input("Do you want to discard the trials with the wrong answers? (0-No, 1-Yes): "))
    noFixationRemoval = int(raw_input("Do you want to discard the trials with no fixations? (0-No, 1-Yes): "))
    lowAnswerLatency = int(raw_input("Do you want to discard the trials with low answer latency? (0-No, 1-Yes): "))
    if (lowAnswerLatency == 1):
       latencyThreshold = int(raw_input("Answer Latency Thereshold (positive integer in ms): "))
    preFixationRemoval =  int(raw_input("Do you want to discard the trials with Prefixation? (0-No, 1-Yes): "))
    if (preFixationRemoval == 1):
        print("Which columns should be considered for discarding trials due to Prefixation :")
        TargetSel = int(raw_input('    Target(1 = Yes, 0 = No)?'))
        FrDisSel = int(raw_input('    French Distractor(1 = Yes, 0 = No)?'))
        EngDisSel = int(raw_input('    English Distractor(1 = Yes, 0 = No)?'))
        TarCtrlSel = int(raw_input('    Target Control(1 = Yes, 0 = No)?'))
        SelectedColumns = [TargetSel , FrDisSel, EngDisSel, TarCtrlSel]

        print(("What is the desired time range?"))
        lowerBound = int(raw_input("     lower bound = "))
        upperBound = int(raw_input("     upper bound = "))
        timeRange = [int(lowerBound), int(upperBound)]
        rangeSize = int(raw_input("What is the desired fixation range (ms)?"))
        
    downSampling = int(raw_input("Down sampling rate (positive integer): "))
    timeBins = int(raw_input("Size of the time bins (positive integer): "))
    isSubstract = int(raw_input("Substract the control data from the target data? (0-No, 1-Yes): "))
    if (isSubstract ==0):
        split = int(raw_input("Should we analyse Target and controls seperately? (0-No, 1-Yes):"))

    if (batchMode == 0):        
        name = raw_input("Name of the file to analyse: ")

optionsList = [alignedFlag, batchMode, iswrongRemoved, noFixationRemoval, lowAnswerLatency, preFixationRemoval, isSubstract]
logFileName = 'Log' + time.strftime("%Y%m%d(%H%M%S)") + '.xls'

if (batchMode == 1):
    fileNamelist = glob.glob("*.edf")
    totalFileNumber =  len(glob.glob("*.edf"))
    print("\nRunning in batch mode for " + str(totalFileNumber)+ " number of file(s) with following options:")
    if (isSubstract == 0):
        if (split ==0):
            print "\t- without subtraction and target and control analysed together"
        else:
            print "\t- without subtraction and target and control analysed separately"
    else:
        print "\t- with substraction"
    if (alignedFlag == 1):
        print "\t- with aligning data based on set divergence points"
    else:
        print "\t- without aligning data based on set divergence points"

    if (iswrongRemoved == 1):
        print "\t- with discarding the Trials with wrong answers"
    else:
        print "\t- without discarding the Trials with wrong answers"

    if (noFixationRemoval == 1):
        print "\t- with discarding the Trials with no fixations"
    else:
        print "\t- without discarding the Trials with no fixations"

    if (lowAnswerLatency == 1):
        print "\t- with discarding the Trials with low answer latency"
        print ("\t- latency threshold (ms): %d"%(latencyThreshold))
    else:
        print "\t- without discarding the Trials with low answer latency"

    if (preFixationRemoval == 1):
        print "\t- with discarding the Trials with Prefixation in time range: " , timeRange
        print "\t- with fixation range eqaul to: ", rangeSize
        print "\t- in columns: ",
        if (TargetSel == 1):
            print "Target",
        if (FrDisSel == 1):
            print ", French Distractor",
        if (EngDisSel == 1):
            print ", English Distractor",
        if (TarCtrlSel == 1):
            print ", Target Control"
        if (TargetSel == 0 and FrDisSel == 0 and EngDisSel == 0 and TarCtrlSel == 0):
            print "None"
        print "\n",
    else:
        print "\t- without discarding the Trials with Prefixation"
        
        
    print ("\t- a downsampling of: %d \n\t- time bins of: %d"%(downSampling, timeBins))

    for inputFilename in fileNamelist:
        name = inputFilename.split(".")[0]
        print("\nProcessing \""+name+"\"")

        discardPractice(name+".xls",name+"_removedP.xls",7)
        convert(name+".edf")
        createMessageFiles(name+".asc")
        analyse(name+"_removedP.xls", name+"_audio.msg", name+"_answers.msg", discardWrong, reactionTimeAnalysis, downSampling, timeBins, alignedFlag)
        sortExcel(name+"_removedP_output",name+"_removedP_output_sorted")
        if (isSubstract == 0):
            noSubstract(name+"_removedP_output_sorted.xls", name+"_notSubstractedData.xls", split)
            prepareForAveraging(name+"_notSubstractedData.xls",name+"_readyForAvg_noS.xls")
            currentInputFileName = name+"_readyForAvg_noS"
            currentOutputFileName = name+"_readyForAvg_noS_"
        else:
            substract(name+"_removedP_output_sorted.xls", name+"_substractedData.xls")
            prepareForAveraging(name+"_substractedData.xls",name+"_readyForAvg.xls")
            currentInputFileName = name+"_readyForAvg"
            currentOutputFileName = name+"_readyForAvg_"

        totalTrialNumber = computeTotaltrials(currentInputFileName + ".xls")
        
        if (iswrongRemoved == 1):
            WrongAnswersList = removeWrongAnswers(currentInputFileName + ".xls" , name+"_removedP_reaction.xls", currentOutputFileName+ "RW.xls")
            delete_file_ignore_error(currentInputFileName + ".xls")
            currentInputFileName = currentOutputFileName+ "RW"
            currentOutputFileName = currentOutputFileName+ "RW"
            
        if (noFixationRemoval == 1):
            NoFixationList = discardNoFixation(currentInputFileName + ".xls", currentOutputFileName + "Fix.xls")
            delete_file_ignore_error(currentInputFileName + ".xls")
            currentInputFileName = currentOutputFileName + "Fix"
            currentOutputFileName = currentOutputFileName + "Fix"

        if (lowAnswerLatency == 1):
            LowLatencyAnswerList = discardLowLatencyAnswer(currentInputFileName + ".xls", name+"_removedP_reaction.xls", currentOutputFileName + "LAT.xls", latencyThreshold)
            delete_file_ignore_error(currentInputFileName + ".xls")
            currentInputFileName = currentOutputFileName + "LAT"
            currentOutputFileName = currentOutputFileName + "LAT"

        if (preFixationRemoval == 1):
            PrefixationList = discardPreFixtion(currentInputFileName + ".xls", currentOutputFileName + "Prefix.xls", timeRange, rangeSize, SelectedColumns, alignedFlag)
            print PrefixationList
            delete_file_ignore_error(currentInputFileName + ".xls")
            currentInputFileName = currentOutputFileName + "Prefix"
            currentOutputFileName = currentOutputFileName + "Prefix"

        discardedLogGenerator(name, logFileName, WrongAnswersList, NoFixationList, LowLatencyAnswerList, PrefixationList, latencyThreshold, totalTrialNumber, optionsList)
        
        expandFixations(currentOutputFileName + '.xls', currentOutputFileName + "_expanded.xls")
        remove_bakground_column(currentOutputFileName + "_expanded.xls", currentOutputFileName + '.xls')
        
        cleanup(name)

        
else:   
    print("\nRunning in single file mode for \""+name+"\"")
    if (isSubstract == 0):
        if (split ==0):
            print "\t- without subtraction and target and control analysed together"
        else:
            print "\t- without subtraction and target and control analysed separately"
    else:
        print "\t- with substraction"

    if (alignedFlag == 1):
        print "\t- with aligning data based on set divergence points"
    else:
        print "\t- without aligning data based on set divergence points"

    if (iswrongRemoved == 1):
        print "\t- with discarding the Trials with wrong answers"
    else:
        print "\t- without discarding the Trials with wrong answers"

    if (noFixationRemoval == 1):
        print "\t- with discarding the Trials with no fixations"
    else:
        print "\t- without discarding the Trials with no fixations"

    if (lowAnswerLatency == 1):
        print "\t- with discarding the Trials with low answer latency"
        print ("\t- latency threshold (ms): %d"%(latencyThreshold))
    else:
        print "\t- without discarding the Trials with low answer latency"

    if (preFixationRemoval == 1):
        print "\t- with discarding the Trials with Prefixation in time range: " , timeRange
        print "\t- with fixation range eqaul to: ", rangeSize
        print "\t- in columns: ",
        if (TargetSel == 1):
            print "Target",
        if (FrDisSel == 1):
            print ", French Distractor",
        if (EngDisSel == 1):
            print ", English Distractor",
        if (TarCtrlSel == 1):
            print ", Target Control",
        if (TargetSel == 0 and FrDisSel == 0 and EngDisSel == 0 and TarCtrlSel == 0):
            print "None",
        print "\n",

    else:
        print "\t- without discarding the Trials with Prefixation"


    print ("\t- a downsampling of: %d \n\t- time bins of: %d"%(downSampling, timeBins))

   
    discardPractice(name+".xls",name+"_removedP.xls",7)
    convert(name+".edf")
    createMessageFiles(name+".asc")
    analyse(name+"_removedP.xls", name+"_audio.msg", name+"_answers.msg", discardWrong, reactionTimeAnalysis, downSampling, timeBins, alignedFlag)
    sortExcel(name+"_removedP_output",name+"_removedP_output_sorted")
    
    
    if (isSubstract == 0):
        noSubstract(name+"_removedP_output_sorted.xls", name+"_notSubstractedData.xls", split)
        prepareForAveraging(name+"_notSubstractedData.xls",name+"_readyForAvg_noS.xls")
        currentInputFileName = name+"_readyForAvg_noS"
        currentOutputFileName = name+"_readyForAvg_noS_"
    else:
        substract(name+"_removedP_output_sorted.xls", name+"_substractedData.xls")
        prepareForAveraging(name+"_substractedData.xls",name+"_readyForAvg.xls")
        currentInputFileName = name+"_readyForAvg"
        currentOutputFileName = name+"_readyForAvg_"
    
    totalTrialNumber = computeTotaltrials(currentInputFileName + ".xls")
    
    if (iswrongRemoved == 1):
        WrongAnswersList = removeWrongAnswers(currentInputFileName + ".xls" , name+"_removedP_reaction.xls", currentOutputFileName+ "RW.xls")
        delete_file_ignore_error( currentInputFileName + ".xls")
        currentInputFileName = currentOutputFileName+ "RW"
        currentOutputFileName = currentOutputFileName+ "RW"
        
    if (noFixationRemoval == 1):
        NoFixationList = discardNoFixation(currentInputFileName + ".xls", currentOutputFileName + "Fix.xls")
        delete_file_ignore_error(currentInputFileName + ".xls")
        currentInputFileName = currentOutputFileName + "Fix"
        currentOutputFileName = currentOutputFileName + "Fix"
    
    if (lowAnswerLatency == 1):
        LowLatencyAnswerList = discardLowLatencyAnswer(currentInputFileName + ".xls", name+"_removedP_reaction.xls", currentOutputFileName + "LAT.xls", latencyThreshold)
        delete_file_ignore_error(currentInputFileName + ".xls")
        currentInputFileName = currentOutputFileName + "LAT"
        currentOutputFileName = currentOutputFileName + "LAT"
    
    if (preFixationRemoval == 1):
        PrefixationList = discardPreFixtion(currentInputFileName + ".xls", currentOutputFileName + "Prefix.xls", timeRange, rangeSize, SelectedColumns, alignedFlag)
        print PrefixationList
        delete_file_ignore_error(currentInputFileName + ".xls")
        currentInputFileName = currentOutputFileName + "Prefix"
        currentOutputFileName = currentOutputFileName + "Prefix"
    
    
    discardedLogGenerator(name, logFileName, WrongAnswersList, NoFixationList, LowLatencyAnswerList, PrefixationList, latencyThreshold, totalTrialNumber, optionsList)

    expandFixations(currentOutputFileName + '.xls', currentOutputFileName + "_expanded.xls")
    remove_bakground_column(currentOutputFileName + "_expanded.xls", currentOutputFileName + '.xls')
    cleanup(name)
raw_input("Press a key to exit.")
