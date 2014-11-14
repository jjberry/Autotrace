#  Created by Julia Fisher
#  7/20/11
#  Last modified:  7/20/11

#  Description:
#  This program takes in a folder, reads systematically through the folder,
#  and produces a text file of information that can be read into R in order to
#  perform a SSANOVA.

#  The folder must be set up in the following manner:
#  The main folder contains separate folders of words.  Each
#  word folder contains some subfolders (plus some other stuff -- random files).
#  One of the subfolders must contain the two vowel tokens from the first
#  repetition of the word.  The other two (or three or more) must contain
#  head-corrected versions of the vowel tokens from repetitions of the word.
#  These will be preceeded by NEW_.

#  Example:
#  Subject15
#		airgead
#			airgead1
#				file1
#				file2
#			airgead2
#				NEW_file1
#				NEW_file2
#			airgead3
#				NEW_file1
#				NEW_file2
#		airm
#			airm1
#				file1
#				file2
#			airm2
#				NEW_file1
#				NEW_file2

import os

def produce_SSANOVA_file(folderpath, outputpath):
    
    WordFolders = os.listdir(folderpath)  # This opens the main folder.

    # Create the output file that will be written to throughout the script.
    # There is one outputfile per subject.  It outputs the data in the form
    # needed by the SSANOVA script.

    Output = open(outputpath, 'w')
    Output.write('word\ttoken\tX\tY\n')  # This is the header line of the output file.
    
    #  Now, go through the main folder and find the needed .traced.txt files and write them appropriately
    # to the output file.
    for item in WordFolders:  # item is the name of the word.  It's 'word' in the output file.
        wordfolder = folderpath + '/' + item
        if os.path.isdir(wordfolder):
            WordRepetitionFolders = os.listdir(wordfolder)
            for thing in WordRepetitionFolders:
                if os.path.isdir(wordfolder + '/' + thing):
                    tokennum = ''  # The tokennum is the number after the word.  So, the folder airgead1
                    i = 0          # would contain all tokens 1 of the two vowels.  Also, tokennum is token in the output.
                    while i < len(thing):
                        if thing[i].isalpha() == False:
                            tokennum = tokennum + thing[i]
                            i += 1
                        else:
                            i += 1
                    VowelTokens = os.listdir(wordfolder + '/' + thing)
                    Vowels = []  # a list in which to hold V1 and V2
                    NEW = None
                    for possiblevowel in VowelTokens:
                        if 'C1' in possiblevowel or 'C2' in possiblevowel:
                            pass
                        elif 'NEW' in possiblevowel:
                            NEW = 'Yes'
                            Vowels.append(wordfolder + '/' + thing + '/' + possiblevowel)
                    if Vowels == []:  # If Vowels is empty, then we're in rep. 1.  Just add the items in it to Vowels.  
                        for possiblevowel in VowelTokens:
                            Vowels.append(wordfolder + '/' + thing + '/' + possiblevowel)

                    if Vowels != []:  # This checks that the folder that should contain the two vowel tokens is not 
                                      # empty. In other words, the vowel tokens were in fact there.
                        # Now, check which of the two vowel files is the first (i.e. the lower number)
                        vowela = Vowels[0].rsplit('_', 1)[1].split('.')[0] # These *should* be the frame numbers.
                        #print vowela
                        vowelb = Vowels[1].rsplit('_', 1)[1].split('.')[0] # This tells us which vowel is the first and which is the second.
                        #print vowelb

                        if vowela < vowelb:
                            V1 = Vowels[0]
                            #print V1
                            V2 = Vowels[1]
                            #print V2
                        else:
                            V1 = Vowels[1]
                            V2 = Vowels[0]

                        # Read through v1.  Get rid of the leftmost element in each line.
                        # Also, get rid of -1 lines.  Then, write the data to the output file.
                        v1 = open(V1, 'r').readlines()

                        for line in v1:
                            data = line.split()
                            if data[0] == '-1':
                                pass
                            else:
                                if NEW == 'Yes':
                                    one = str(round(float(data[1]))).split('.')[0] + '.00'
                                    two = str(round(float(data[2]))).split('.')[0] + '.00'
                                else:
                                    one = data[1]
                                    two = data[2]
                                Output.write(item + 'V1\t' + tokennum + '\t' + one + '\t' + two + '\n')

                        # Now, do the same for v2.
                        v2 = open(V2, 'r').readlines()

                        for line in v2:
                            data = line.split()
                            if data[0] == '-1':
                                pass
                            else:
                                if NEW == 'Yes':
                                    one = str(round(float(data[1]))).split('.')[0] + '.00'
                                    two = str(round(float(data[2]))).split('.')[0] + '.00'
                                else:
                                    one = data[1]
                                    two = data[2]
                                Output.write(item + 'V2\t' + tokennum + '\t' + one + '\t' + two + '\n')

    Output.close()


# This is where we call on the program.
produce_SSANOVA_file('/Users/apiladmin/Desktop/GaelicEpenthesisHC/GaelicS8', '/Users/apiladmin/Desktop/GaelicEpenthesisHC/GaelicS8/GaelicS8_SSANOVAfile3.txt')
                                
                                
                            
                        
                        
                        
        

    
