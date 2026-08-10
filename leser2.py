import re
import sys
import pymupdf
import tkinter as tk
from tkinter import filedialog



def openfile(filename):
        try:
            file = pymupdf.open(filename)
            text = chr(12).join([page.get_text() for page in file])
            return text
        except TypeError as e:
            print("Unsupported file format: ", e)
            return False
        except OSError as e:
            print("Could not open file: ", e)
            return False 
        except Exception as e:
            print("Unexpected error: ", e)
            return False

def splitfile(string):
    chunks = re.split(r"\s*\n\s*\n\s*", string)
    return chunks

def cleanmerge(chunks):
    index = 0
    merge = []
    while index < len(chunks): # while index in range(len(chunks)) würde funktionieren, muss aber jedesmal neu berechnen
        #need to strip whitespace so chunks are clean and 
        #chunks with only whitespace characters become empty strings
        chunk = chunks[index].strip()
        if len(chunk) < 1:
            index += 1
            continue
        elif index == len(chunks)-1: #catches the last chunk
            merge.append(chunk)
            index +=1
        elif chunk[-1] in ".?:": #typical character that shows the end of a paragraph
            merge.append(chunk)
            index += 1
        else:
            merge.append(chunk+"\n"+chunks[index+1].strip())
            index+=2
    return merge

#tkinter: prompts a file explorer to choose a pdf
root = tk.Tk()
root.withdraw()

def choosefile():
    while True:
        root.attributes('-topmost', True) #zwingt das tkinter-Auswahlfenster in den Vordergrund
        filename = filedialog.askopenfilename()
        if filename == "":
            answer = input("If you still want to choose a file, press the ENTER key. I you want to quit, type 'quit' to end the program.")
            if answer.strip().lower() == "quit":
                print("You wanted to quit, have a nice day!")
                exit()
            else:
                continue
        elif not filename.endswith(".pdf"):
            print("The file needs to be a pdf document")
            continue
        else:
            text = openfile(filename)
            if not text:
                print("The file you chose could not be opened, please choose another file.\n")
                continue
        return text

#prompt the user to choose a file from the explorer
stringfile = choosefile()
    

#stringfile = openfile(filename) #uses the above written function
chunks = splitfile(stringfile)
cleanchunks = cleanmerge(chunks)

def searchterm(term, clean_chunks):
    searchresult = []
    for result in clean_chunks:
        if term.lower() in result.lower():
            searchresult.append(result)

    snippetstring = ("\n\n").join(searchresult)
    return snippetstring

print("""You will now be prompted to enter a tearm
and the program will return all snippets where the tearm was found.""")
lookup = input("Enter a term to search: ")
while True:
    pdfsnippets = searchterm(lookup, cleanchunks)
    if pdfsnippets == "":
        print("The term you entered was not found.")
        lookup = input("Enter a term to search or enter 'quit' to exit the program: \nTerm: ")
        if lookup.lower().strip() == "quit":
            exit()
    else:
        break
            
print(pdfsnippets)