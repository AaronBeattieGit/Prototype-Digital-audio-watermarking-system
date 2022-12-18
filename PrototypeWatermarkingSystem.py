import numpy as np
from scipy.io import wavfile
import random

class watermarking():
    def __init__(self, fileLocation, messageLocation, message, audioFrames, encodedMessage, realComp, imagComp, markLoc, transAudio, transWater, finMarked, sampleRate):
        self.fileLocation = fileLocation    #The file path of the Audio file to be embedded or extraction
        self.messageLocation = messageLocation  #the file path of the watermarking message
        self.messageText = message  #A string containing the watermarking message
        self.audioFrames = audioFrames  #to be used to store a Numpy Array, containing the audio file samples
        self.sampleRate = sampleRate #contains the sample rate of the audio file
        self.encodedMessage = encodedMessage    #contains the encoded message as a 1-D NumPy array
        self.transAudio = transAudio    #Contains the transformed audio in the form of a 2-D NumPy array with a complex data type
        self.realComp = realComp    #Contains the real component of the transformed audion as a 2-D NumPy array
        self.imagComp = imagComp    #Contains the Complex component of the transformed audio
        self.markLocation = markLoc #contains an array of locations for the watermark bits to be embedded
        self.transWater = transWater #contains a 2-D array containing the watermarked signal in the frequency domain
        self.finalWatermarkedAudio = finMarked #contains a 2-D array containing the watermarked signal in the time domain
        

    #Opens the watermarking message and stores it as a string within the class
    def accessMessage(self):
        message = open(self.messageLocation)
        message = message.read()
        print('Message from file: '+message)
        self.messageText = message

    #Access the audio file and stores it as a 2-D NumPy array
    def accessAudio(self):
        self.sampleRate, self.audioFrames = wavfile.read(self.fileLocation)
        print('sample rate = ' + str(self.sampleRate))
        print('number of samples = ' + str(len(self.audioFrames)))

    #Takes the watermark message and encodes it into a 1-D Binary array
    def encode(self):
        watermark1.accessMessage()
        messageForEncode = self.messageText
        encodedMessage = messageForEncode.encode()
        encodedArray = bytearray(encodedMessage)
        messageLength = len(encodedArray)
        binaryMsgArray = np.empty([messageLength, 8], dtype='>i8')
        #loops through the byte array and converts it to a 2-D NumPy array of shape (message length, 8)
        for x in range(messageLength):
            temp = format(encodedArray[x], '08b')
            for y in range(8):
                binaryMsgArray[x, y] = temp[y]
                y+=1
            x+=1
        binaryMsgArray = np.ravel(binaryMsgArray) #This flattens the 2-D array
        self.encodedMessage = binaryMsgArray
        print('encoded message array: ')
        print(self.encodedMessage)

    #This method Takes the audio signal and transforms it from the time domain to the frequecy domain using the fast fourier transform in NumPy.
    #the method then seperates the real and the complex components
    def transform(self):
        transformedAudio = np.fft.fft(self.audioFrames) #performs the fft on the audio signal
        transLength = len(transformedAudio)
        imaginaryComp = np.empty([transLength, 2], dtype=complex)
        realComp = np.empty([transLength, 2], dtype=int)
        x = 0
        #This loops through the transformed signal an takes an abolute value of it to obtain the real component, and then takes the real component away from the transformed audio to obtain the complex component
        while x < transLength:
            realComp[x, 0] = abs(transformedAudio[x, 0])
            realComp[x, 1] = abs(transformedAudio[x, 1])
            if transformedAudio[x][0] > 0:
                imaginaryComp[x, 0] = transformedAudio[x, 0] - realComp[x, 0]
            else:
                imaginaryComp[x, 0] = transformedAudio[x, 0] + realComp[x, 0]
            
            if transformedAudio[x][1] > 0:
                imaginaryComp[x, 1] = transformedAudio[x, 1] - realComp[x, 1]
            else:
                imaginaryComp[x, 1] = transformedAudio[x, 1] + realComp[x, 1]
            x += 1
        self.realComp = realComp
        self.imagComp = imaginaryComp
        self.transAudio = transformedAudio

    #This function uses a seeded random intager generator to generate the watermarking coefficents. this is seeded with the watermarking key
    def randNumGen(self):
        watermarkKey = 0
        watermarkKey = input("Enter the watermarking key: ")
        print("The Watermarking key is: " + watermarkKey)
        self.key = watermarkKey
        watermarkKey = int(watermarkKey) * 8
        randomlist = []
        #this loops a number of times equal to the watermarking key input * 8 and generates that many coeficents 
        for i in range(watermarkKey):
            random.seed(watermarkKey)
            n = random.randint(0,len(self.audioFrames))
            randomlist.append(n)
            watermarkKey = watermarkKey + i + 1
        self.markLocation = randomlist
        print(self.markLocation)

    #This method embeds the watermark using the parity of two succsessive coefficents to embed a signel bit
    def embbed(self):
        audioToEmbed = self.realComp
        embedSequence = self.markLocation
        message = self.encodedMessage
        #Loops through accesing the audio file at locations generated by the random number generator
        for i in range(len(embedSequence)):
            templocation = embedSequence[i]
            tempSampleL = audioToEmbed[templocation][0]
            tempSampleL1 = audioToEmbed[templocation + 1][0]
            tempBit = message[i]
            print(tempBit)
            print(tempSampleL)
            if(tempBit == (tempSampleL - tempSampleL1) % 2): #checks if the parity and the watermarking bit is equal and if so no changes are made
                    tempSampleL = tempSampleL
            elif(tempBit != (tempSampleL - tempSampleL1) % 2):#checks if the parity and the watermarking bit are not equal and if so changes the LSB of the first coefficent
                    tempSampleL += 1 
            print(tempSampleL1)
            self.realComp[templocation, 0] = tempSampleL
            print(self.realComp[templocation, 0])
            print('--------------')

    #This takes the watermarked real component and adds it back together with the complex component to obtain the final watermarked signal
    def recombine(self):
        realComp = self.realComp
        imagComp = self.imagComp
        transWaterAudio = np.empty([len(self.realComp), 2], dtype=complex)
        for i in range(len(realComp)):
            if self.transAudio[i][0] >= 0:
                transWaterAudio[i][0] = realComp[i][0] + imagComp[i][0]
            elif self.transAudio[i][0] < 0:
                transWaterAudio[i][0] = -abs(realComp[i][0]) + imagComp[i][0]
        
            if self.transAudio[i][1] >= 0:
                transWaterAudio[i][1] = realComp[i][1] + imagComp[i][1]
            elif self.transAudio[i][1] < 0:
                transWaterAudio[i][1] = -abs(realComp[i][1]) + imagComp[i][1]
        self.transWater =  transWaterAudio

    #Performs the reverse fourier transform as provided by NumPy
    def revTransform(self):
        self.finalWatermarkedAudio = np.fft.ifft(self.transWater)

    #Takes the watermarked signal and an inputed file path and writes a new watermarked WAV file
    def writeWav(self):
        waterMarkedFileLoc = input("Please input the full file path you would like the new audio file to be stored in: ")
        waterMarkedFileName = input("What would you like the file name to be?: ")
        fileWriteLoc = waterMarkedFileLoc + waterMarkedFileName + ".wav"
        print(fileWriteLoc)
        wavfile.write(fileWriteLoc, self.sampleRate, self.finalWatermarkedAudio.astype(np.int16))

    #extracts the watermark message bits from a watermarked work by comparing the parity of the coeficents
    def extraction(self):
        extractedMark = np.empty([len(self.markLocation)], dtype = int)
        for i in range(len(self.markLocation)):
            tempSampleL = self.realComp[self.markLocation[i]][0]
            tempSampleL1 = self.realComp[self.markLocation[i] + 1][0]
            print(self.realComp[self.markLocation[i]])
            if (((tempSampleL - tempSampleL1)) % 2) == 0: #if the parity is equel then the bit of the watermark at that location is 0
                extractedMark[i] = 0
            elif (((tempSampleL - tempSampleL1)) % 2) != 0: #if the parity is odd the bit at that location is 1
                extractedMark[i] = 1
        print(extractedMark)

        
audioFileLocation = input("Please input the path that the audio file is stored in ")
embedOrExtract = input("would you like to Embed or Extract? ")
print(embedOrExtract)
watermark1 = watermarking(audioFileLocation, r'', r"", 0, 0, 0, 0, 0, 0, 0, 0, 0)
if embedOrExtract == 'Embed':
    watermark1.messageLocation = input("Please input the message location: ")
    print('Embedding...')
    watermark1.accessAudio()
    watermark1.encode()
    watermark1.transform() 
    print('Input the number of characters in the message as the watermarking key ')
    watermark1.randNumGen()
    watermark1.embbed()
    watermark1.extraction()
    watermark1.recombine()
    watermark1.revTransform()
    watermark1.writeWav()
    print('Embeding complete!')
elif embedOrExtract == 'Extract':
    print('Extracting...')
    watermark1.accessAudio()
    watermark1.transform()
    watermark1.randNumGen()
    watermark1.extraction()