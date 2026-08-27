import re
import sys
import pymupdf
import pandas as pd
import tkinter as tk
from tkinter import filedialog, scrolledtext, simpledialog
from tkinter import messagebox as mb


# FUNCTIONS USED IN THE LESER2 PROGRAM - START #

def choosefile() -> list:
    selectedfiles = []
    while True:
        root.attributes('-topmost', True) #zwingt das tkinter-Auswahlfenster in den Vordergrund
        filename = filedialog.askopenfilename()
        if filename not in [tup[0] for tup in selectedfiles]:
            if filename == "": #catches the instance where the user closes the explorer without choosing a file
                if not mb.askyesno("DID YOU WANT TO DO THAT ?", "If you still want to choose a file, press YES. I you want to quit, press NO."):
                    mb.showinfo("See you again!", "You wanted to end the program.\n Have a nice day!")
                    exit()
                else:
                    continue
            elif not filename.endswith(".pdf"):
                mb.showwarning("UNSUPPORTED FORMAT", "The file needs to be a pdf document")
                continue
            else:
                text = openfile(filename)
                if not text:
                    mb.showinfo("", "The file you chose could not be opened, please choose another file.\n")
                    continue
                selectedfiles.append((filename, text))
                if not mb.askyesno("Continue?", "Do you want to select more files from another folder?"):
                    break
        else:
            if not mb.askyesno("Double input!", "You already chose this file. Do you want to choose another file?"):
                break
            else:
                continue
    return selectedfiles

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
    chunks = re.split(r"\x0c|\s*\n\s*\n\s*", string)
    return chunks

def cleanmerge(chunks):
    index = 0
    merge = []
    while index < len(chunks): # while index in range(len(chunks)) würde funktionieren, muss aber jedesmal neu berechnen
        #need to strip whitespace so chunks are clean and 
        #chunks with only whitespace characters become empty strings with length < 1
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

# searchterm sucht in den mit def cleanmerge() gefundenen chunks nach solchen, die einen Suchbegriff beinhalten
# der Suchbegriff wird mittel lookup = input("Enter a term to search") vom user angefragt.
def searchterm(term, filename_chunks):
    searchresult = []
    
    for result in filename_chunks:
        textstring = result[1]
        if term.lower() in textstring.lower():
            searchresult.append(result)
        
    return searchresult

# searchbox soll den user mittels simpledialog.askstring() nach einem Suchwort fragen
# dabei validieren, ob der user einfach rausklicken möchte oder gar kein gültiges Suchwort eingibt

def searchbox():
    while True:
        term = simpledialog.askstring("Search-term", "Please enter a term to search or type quit to exit the program.")
        if term == None:
            mb.showinfo("No valid input", "Your search-term must be a text input. Please try again.")
            continue

        try:
            stringterm = term.lower().strip()
        except ValueError:
            mb.showinfo("Invalid input", "Your input must be a text input.\n Please try again!")
            continue
        except Exception as e:
            mb.showinfo("Oups, unexpected error", f"This happened: {e}")
            continue

        if stringterm == "quit":
            mb.showinfo("Exit", "You wanted to close the program.\n Have a nice day!")
            exit()

        return stringterm
        

# def showresult(searchresult):
#     firstlines = []
#     for idx, chunk in enumerate(searchresult, start = 1):
#         firstline = chunk[1].split("\n")[0]
#         source_headline_no_firstline = f"Headline No. {idx}:\n{firstline}\n"+"-"*10+"\n"
#         print(f"Source: {chunk[0]}\nHeadline No. {idx}:\n{firstline}\n")
#         print("-"*10, "\n")
#         firstlines.append((chunk[0], source_headline_no_firstline))
#     return firstlines

def chooseresult(result_dataframe):
    maxresult = len(result_dataframe)
    while True:
        interestingresult = simpledialog.askstring("Choose a result", "Please enter the Result No. you wish to see the whole result from or type quit to exit the program: ")
        if interestingresult == None:
                    mb.showinfo("Invalid number", f"Please enter a valid number between 0 and {maxresult-1} or type quit to exit the program.")
                    continue

        elif interestingresult.lower().strip() == "quit":
            exit()
        
        try:
            number = int(interestingresult.strip())
            title = result_dataframe.iloc[number-1]["Title"]
            source = result_dataframe.iloc[number-1]["Source"]
            result = result_dataframe.iloc[number-1]["Result"]
        except ValueError as e:
            mb.showinfo("Wrong Value Type", f"Invalid format, please enter exactly one number between 0 and {maxresult-1}")
            continue
        except IndexError:
            mb.showinfo("Index Error", f"The number you choose must be between 0 and {maxresult-1}")
            continue
        except Exception as e:
            mb.showwarning("Oups!", "Unexpected issue: ")
            exit()
        return number, title, source, result

# takes the result from searchresult (filename, text) and converts it into a 
# tuple-list [(source, first_line, content), ...], then builds a pd.DataFrame with it and returns it
# as df
def searchresult_to_dataframe(searchresult):
    columnlist = ["Source", "Title", "Result"]
    dataframe_tuple_list = [(result[0].split("/")[-1], result[1].split("\n")[0], result[1]) for result in searchresult]
    df = pd.DataFrame(dataframe_tuple_list, columns = columnlist)
    return df 

# a terminal function to aks the user for yes or no
# since the introduction of tkinter not in use

# def yesnoanswer() -> bool:
#     while True:
#         answer = input("Please type yes or no.")
#         answered = answer.lower().strip()
#         if answered == "":
#             print("Please enter yes or no.")
#             continue
#         elif answered not in ["yes", "no", "y", "n"]:
#             print("Please enter yes or no.")
#             continue
#         elif answered == "yes" or answered =="y":
#             return True
#         elif answered == "no" or answered == "n":
#             return False


# FUNCTIONS USED IN THE LESER2 PROGRAM - END #

# START OF THE ACTUAL PROGAM CODE

#tkinter: prompts a file explorer to choose a pdf
root = tk.Tk()
root.title("Your result")
root.geometry("500x400")

# prompt the user to choose a file from the explorer
# stringfile = choosefile() combines opening a file explorer to choose one or more files and
# uses the openfile() function to test if the files can be opened and in the end returns
# a list with tuples in the form (filename, text) where text is a string with file pages joined by \X0c
stringfiles = choosefile()

# now split the page-string of each tuple in stringfiles into parts with a simple logic (those parts with two newline characters in between are likely paragraphs)
filechunklist = []
for file in stringfiles:
    filename = file[0]
    textstring = file[1]
    chunks = splitfile(textstring)
# remove chunks that contain no valuable information and merge those that likely represent headline and chapter-part
    cleanchunks = cleanmerge(chunks)
    filechunklist.extend([(filename, chunk) for chunk in cleanchunks])


mb.showinfo("Search", "You will now be prompted to enter a search-term and the program will present the result as chapter headlines.")

while True:
    lookup = searchbox()

    searchresult = searchterm(lookup, filechunklist)
    if searchresult == []:
        mb.showinfo("NO RESULT", "The term you searched was not found. Please try again!")
        continue
    else:
        break

print("These are the chapter headlines for your search: \n\n")
sorted_searchresult = sorted(searchresult, key = lambda chunk: (chunk[0], -len(chunk[1])) )
result_dataframe = searchresult_to_dataframe(sorted_searchresult)

# print(result_dataframe) prints the search result to the Terminal. May be used for debugging 

root.attributes("-topmost", False)
viewbox = scrolledtext.ScrolledText(root, background="darkgrey", foreground= "white",
                                    width= 50, height= 30)
viewbox.pack(fill=tk.BOTH, side=tk.LEFT, expand=True)
viewbox.insert(tk.INSERT, result_dataframe.to_string(columns=["Source", "Title"]))

# Wiederholte Möglichkeit, die Ergebnisse anzusehen und auszuwählen. Anzeige im Tcl/Tk window
# yesnoanswer returns True if the user answered yes or returns False if the user answered no.
watched = []
while True:
    number, title, source, content = chooseresult(result_dataframe)
    if number in watched: 
        if not mb.askyesno("AGAIN", "You already saw this result, do you want to display it again ?"):
            continue
            
    
    viewbox.delete("1.0", tk.END)
    viewbox.insert(tk.INSERT, f"Result No.: {number}\nSource: {source}\n\n{content}")
    if number not in watched:
        watched.append(number)
    
    if mb.askyesno("RESULTS", "Do you want to see another result?"):
        if mb.askyesno("", "Do you want to see the result-list again?"):
            viewbox.delete("1.0", tk.END)
            viewbox.insert(tk.INSERT, result_dataframe.to_string(columns=["Source", "Title"]))
            continue
        else:
            continue
    else:
        mb.showinfo("CLOSE PROGRAM", "The program will be closed then. Have a nice day.")
        break
 
# END OF PROGRAM CODE