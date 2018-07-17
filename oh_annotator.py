from tkinter import *
import nltk
import tkinter.messagebox
import csv
import random

filename = input('Dataset filename (without .csv): ')

# Read from dataset
corpus = []
with open(filename+'.csv', 'r') as f:
    reader = csv.reader(f)
    corpus = list(reader)[1:]
    
# Get random sequence
randomSeq = random.sample(range(len(corpus)), len(corpus))

#Get list of labelled sentence
labeled = []
try:
    with open(filename+'-annotated.csv', 'r') as f:
        reader = csv.reader(f)
        labeled = list(reader)[1:]
        for i in range(len(labeled)):
            labeled[i] = str(labeled[i][1])+' '+str(labeled[i][2])
        labeled = list(set(labeled))
except FileNotFoundError:
    pass

root = Tk()

# Put GUI component to frame
labelCurrent = Label(root, text='')
labelCurrent.pack()
labelSuccess = Label(root, text='')
labelSuccess.pack()
labelSentence = Label(root, text='')
labelSentence.pack()
nextS = Button(root, text='Next sentence', command=lambda:nextSent())
nextS.pack()
nextL = Button(root, text='Change label', command=lambda:changeLabel())
nextL.pack()
anotherL = Button(root, text='Another entity', command=lambda:anotherEntity())
anotherL.pack()
endB = Button(root, text='Skip sentence', command=lambda:skipSent())
endB.pack()
resetB = Button(root, text='Restart sentence', command=lambda:resetSent())
resetB.pack()

#Init variables
buttons = []
labelName = ['Person','Organization','Job', 'Geopolitical']
i = 0
labelCount = 0
specialCode = 0
labelNow = 0
beginLabel = True
resultLabel = []

# Function for changing sentence
def nextSent():
    global buttons, i, labelCount, labelNow, beginLabel, resultLabel, specialCode
    
    # Skip sentence
    if specialCode == 999:
        i = i+1
    # First sentence or restart sentence
    elif labelCount == 0 or specialCode == 500:
        i = i
    # Go to next sentence normally
    else:
        labelSuccess.config(text='Remaining tokens are labeled as O')
        finishSent()
        i = i+1
    # Skip labelled sentence
    while str(corpus[randomSeq[i]][1])+' '+str(corpus[randomSeq[i]][2]) in labeled:
        i = i+1
    
    beginLabel = True
    labelNow = 0
    specialCode = 0
    # Get current sentence
    sent = corpus[randomSeq[i]][3]
    labelSentence.config(text=sent)
    
    # Remove token buttons from previous sentence
    for button in buttons:
        button.destroy()
    buttons = []
    
    # Tokenize sentence using nltk
    tokens = []
    try:
        tokens = nltk.tokenize.word_tokenize(sent)
    except TypeError:
        pass
    
    idx = 0
    resultLabel = []
    for token in tokens:
        # Generate button for each token
        tokenButton = Button(root, text=token, command=lambda token=token, idx=idx:giveLabel(token,labelName[labelNow],idx))
        tokenButton.pack(side=LEFT)
        buttons.append(tokenButton)
        # Assign each button with label O initially
        resultLabel.append([corpus[randomSeq[i]][0],corpus[randomSeq[i]][1],corpus[randomSeq[i]][2],idx,token,'O'])
        idx = idx+1
    labelCount = len(buttons)
    
    # Put info on current label
    labelCurrent.config(text='Current Label: Begin-Person')

# Function for changing current label
def changeLabel():
    global labelNow, beginLabel
    beginLabel = True
    labelNow += 1
    
    # If current label is Geo, change back to Person
    if labelNow == 4:
        labelNow = 0
    
    #Put info on new current label
    if beginLabel == True:
        labelCurrent.config(text='Current Label: Begin-'+labelName[labelNow])
    else:
        labelCurrent.config(text='Current Label: Inside-'+labelName[labelNow])
    

# Function for staring new entity with same label
def anotherEntity():
    global beginLabel
    beginLabel = True
    labelCurrent.config(text='Current Label: Begin-'+labelName[labelNow])

# Function for skipping sentence
def skipSent():
    global specialCode
    specialCode = 999
    nextSent()

#Function for restarting sentence
def resetSent():
    global specialCode
    specialCode = 500
    nextSent()

# Function for labelling token
def giveLabel(token,result,idx):
    global beginLabel, resultLabel, labelCurrent
    
    # Put info on success labelling
    begin = ''
    if beginLabel == True:
        begin = 'Begin-'
    else:
        begin = 'Inside-'
    labelSuccess.config(text=token+' Labeled as '+begin+result)
    
    # Assign new label to token
    resultLabel[idx][5] = begin[0]+'-'+result[0:3].upper()
    
    # Disable button of labeled token
    buttons[idx].config(state='disabled')
    
    if beginLabel == True:
        beginLabel = False
    #Put info on new current label
    if beginLabel == True:
        labelCurrent.config(text='Current Label: Begin-'+labelName[labelNow])
    else:
        labelCurrent.config(text='Current Label: Inside-'+labelName[labelNow])
        
# Write labelled sentence to output file
def finishSent():
    global resultLabel, labeled
    with open(filename+'-annotated.csv', 'a' , newline='') as myfile:
        wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
        wr.writerows(resultLabel)
    labeled.append("new")
    print('Total sentence labelled: '+str(len(labeled)))
    prevEntity = 'O'
    for result in resultLabel:
        if result[5] != 'O':
            if result[5][-3:] != prevEntity:
                print (result[5][-3:]+':')
                prevEntity = result[5][-3:]
            print(result[4])
        else:
            prevEntity = 'O'
    print('--------------------')

# main
nextSent()

root.mainloop()