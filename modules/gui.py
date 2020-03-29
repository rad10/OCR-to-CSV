import tkinter
from math import floor
from os.path import basename, dirname, expanduser, normpath
from time import sleep
from tkinter import filedialog, ttk

from PIL import Image, ImageTk


class mainGUI:
    # Gui Variables
    signinsheet = ""
    outputCSV = normpath(expanduser("~\\Documents\\signinSheetOutput.csv"))
    guessButton = False
    submitButton = False

    # GUI Components
    root = tkinter.Tk(screenName="OCR To CSV Interpreter")
    decision = tkinter.BooleanVar(root)
    inputFile = tkinter.Button(root)
    outputFile = tkinter.Button(root)
    labelImage = tkinter.Label(root)
    errorLabel = tkinter.Label(root)
    confidenceDescription = tkinter.Label(root)
    AIGuess = tkinter.Button(root)
    orLabel = tkinter.Label(root)
    correctionEntry = tkinter.Entry(root)
    submit = tkinter.Button(root)

    # Status bars
    sheetStatus = tkinter.Label(root, text="Sheet: 0 of 0")
    rowStatus = tkinter.Label(root, text="Row: 0 of 0")
    progressBar = ttk.Progressbar(root)

    def __init__(self):
        self.root.title("OCR To CSV Interpreter")
        self.root.geometry("600x450+401+150")
        self.root.configure(background="#d9d9d9")
        self.root.minsize(120, 1)
        self.root.maxsize(1370, 749)
        self.root.resizable(1, 1)

        self.inputFile.configure(
            text="Select Signin Sheet", command=self.reconfigInput)
        self.inputFile.configure(
            activebackground="#ececec", activeforeground="#000000", background="#d9d9d9",
            disabledforeground="#a3a3a3", foreground="#000000",
            highlightbackground="#d9d9d9", highlightcolor="black", pady="0")
        self.inputFile.place(relx=0.033, rely=0.044, height=34, width=157)

        self.outputFile.configure(
            text=basename(self.outputCSV), command=self.reconfigOutput)
        self.outputFile.configure(
            activebackground="#ececec", activeforeground="#000000", background="#d9d9d9",
            disabledforeground="#a3a3a3", foreground="#000000", highlightbackground="#d9d9d9",
            highlightcolor="black", pady="0")
        self.outputFile.place(relx=0.033, rely=0.156, height=34, width=157)

        self.labelImage.configure(text="No corrections required yet.")
        self.labelImage.configure(
            background="#e6e6e6", disabledforeground="#a3a3a3", foreground="#000000")
        self.labelImage.place(relx=0.417, rely=0.022, height=221, width=314)

        self.errorLabel.configure(
            wraplength=224, activebackground="#f9f9f9", activeforeground="black",
            background="#e1e1e1", disabledforeground="#a3a3a3", foreground="#ff0000",
            highlightbackground="#d9d9d9", highlightcolor="black")
        self.errorLabel.place(relx=0.017, rely=0.267, height=111, width=224)

        self.confidenceDescription.configure(
            activebackground="#f9f9f9", activeforeground="black", background="#d9d9d9",
            disabledforeground="#a3a3a3", foreground="#000000", highlightbackground="#d9d9d9",
            highlightcolor="black")
        self.confidenceDescription.place(
            relx=0.267, rely=0.556, height=31, width=164)

        self.AIGuess.configure(text="No guesses yet.")
        self.AIGuess.configure(
            activebackground="#ececec", activeforeground="#000000", background="#d9d9d9",
            disabledforeground="#a3a3a3", foreground="#000000", highlightbackground="#d9d9d9",
            highlightcolor="black", pady="0", command=self.guessSwitch)
        self.AIGuess.place(relx=0.55, rely=0.556, height=34, width=227)

        self.orLabel.configure(
            activebackground="#f9f9f9", activeforeground="black", background="#d9d9d9",
            disabledforeground="#a3a3a3", foreground="#000000", highlightbackground="#d9d9d9",
            highlightcolor="black")
        self.orLabel.place(relx=0.017, rely=0.689, height=31, width=64)

        self.correctionEntry.configure(
            background="white", disabledforeground="#a3a3a3", font="TkFixedFont", foreground="#000000",
            highlightbackground="#d9d9d9", highlightcolor="black", insertbackground="black",
            selectbackground="#c4c4c4", selectforeground="black")
        self.correctionEntry.place(
            relx=0.133, rely=0.689, height=30, relwidth=0.557)

        self.submit.configure(text="Submit")
        self.submit.configure(
            activebackground="#ececec", activeforeground="#000000", background="#d9d9d9",
            disabledforeground="#a3a3a3", foreground="#000000", highlightbackground="#d9d9d9",
            highlightcolor="black", pady="0", command=self.submitSwitch)
        self.submit.place(relx=0.717, rely=0.689, height=34, width=127)
        self.root.bind("<Return>", self.submitSwitch)

        self.sheetStatus.configure(
            activebackground="#f9f9f9", activeforeground="black", background="#d9d9d9",
            disabledforeground="#a3a3a3", foreground="#000000", highlightbackground="#d9d9d9",
            highlightcolor="black")
        self.sheetStatus.place(relx=0.017, rely=0.844, height=21, width=94)

        self.rowStatus.configure(
            activebackground="#f9f9f9", activeforeground="black", background="#d9d9d9",
            disabledforeground="#a3a3a3", foreground="#000000", highlightbackground="#d9d9d9",
            highlightcolor="black")
        self.rowStatus.place(relx=0.217, rely=0.844, height=21, width=64)

        self.progressBar.place(relx=0.017, rely=0.911, relwidth=0.95,
                               relheight=0.0, height=22)
        self.root.mainloop()

    # GUI Functions

    def guessSwitch(self):
        self.guessButton = True
        self.decision.set(1)

    def submitSwitch(self, event=None):
        if(event != None and self.correctionEntry.get() == ""):
            return
        self.submitButton = True
        self.decision.set(1)

    def reconfigOutput(self):
        outputCSV = filedialog.askopenfilename(filetypes=(
            ("Comma Style Values", "*.csv"), ("Comma Style Values", "*.csv")))
        if(outputCSV != ""):
            self.outputFile.configure(text=basename(outputCSV))
            self.outputCSV = outputCSV

    def reconfigInput(self):
        signinsheet = filedialog.askopenfilename(filetypes=(
            ("PDF Files", "*.pdf"), ("Jpeg Files", "*.jpg"), ("Png Files", "*.png")))
        if(signinsheet != ""):
            self.inputFile.configure(text=basename(signinsheet))
            self.signinsheet = signinsheet

    def requestCorrection(self, displayImage, col, guess=""):
        """This is the function used when a string doesnt confidently match a name.\n
        @param displayImage: The image placed on the display for user to see.\n
        @param {int} col: The column number that the image was found in. This is needed for placing the AI's guess.\n
        @param {string} guess: This is to straight up overwrite the AI's guess with the string. This can be helpful so that the AI doesnt have to process the image again.\n
        @return: the users answer.
        """

        result = ""  # the string to be returned for final answer

        # Setting up image to place in GUI
        image = Image.fromarray(displayImage)
        if(displayImage.shape[1] > self.labelImage.winfo_width()):
            hgt, wth = displayImage.shape[:2]
            ratio = self.labelImage.winfo_width()/wth
            image = image.resize(
                (floor(wth * ratio), floor(hgt * ratio)), Image.ANTIALIAS)
        image = ImageTk.PhotoImage(image)

        # setting values to labels in gui
        self.labelImage.configure(image=image)
        self.labelImage.image = image
        self.errorLabel.configure(
            text="Uh oh. It looks like we couldnt condifently decide who or what this is. We need you to either confirm our guess or type in the correct value")
        self.confidenceDescription.configure(
            text="Were not confident, but is it:")
        self.AIGuess.configure(text=guess)
        self.orLabel.configure(text="or")

        # basically waits till user presses a button and changes variable scope
        self.root.update_idletasks()
        self.root.wait_variable(self.decision)
        result = self.correctionEntry.get()

        # Resetting changes made
        self.labelImage.configure(image=None)
        self.labelImage.image = None
        self.errorLabel.configure(text="")
        self.confidenceDescription.configure(text="")
        self.AIGuess.configure(text="")
        self.orLabel.configure(text="")
        self.correctionEntry.delete(0, "end")
        self.root.update_idletasks()
        sleep(1)
        self.decision.set(0)

        if(self.guessButton):
            self.guessButton = False
            self.submitButton = False
            return (guess, 100, True)
        elif(self.submitButton):
            self.guessButton = False
            self.submitButton = False
            return (result, 100, True)


