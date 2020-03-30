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
    root = None
    decision = None
    inputFile = None
    outputFile = None
    start = None
    labelImage = None
    errorLabel = None
    confidenceDescription = None
    AIGuess = None
    orLabel = None
    correctionEntry = None
    submit = None

    # Status bars
    sheetStatus = None
    rowStatus = None
    progressBar = None

    def __init__(self, cmd=None):
        # Init GUI Components
        self.root = tkinter.Tk(screenName="OCR To CSV Interpreter")
        self.decision = tkinter.BooleanVar(self.root)
        self.inputFile = tkinter.Button(self.root)
        self.outputFile = tkinter.Button(self.root)
        self.start = tkinter.Button(self.root)
        self.labelImage = tkinter.Label(self.root)
        self.errorLabel = tkinter.Label(self.root)
        self.confidenceDescription = tkinter.Label(self.root)
        self.AIGuess = tkinter.Button(self.root)
        self.orLabel = tkinter.Label(self.root)
        self.correctionEntry = tkinter.Entry(self.root)
        self.submit = tkinter.Button(self.root)

        # Status bars
        self.sheetStatus = tkinter.Label(self.root, text="Sheet: 0 of 0")
        self.rowStatus = tkinter.Label(self.root, text="Row: 0 of 0")
        self.progressBar = ttk.Progressbar(self.root)

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

        self.start.configure(text="Start", command=cmd)
        self.start.configure(
            activebackground="#ececec", activeforeground="#000000", background="#17a252",
            disabledforeground="#a3a3a3", foreground="#ffffff", highlightbackground="#d9d9d9",
            highlightcolor="black", pady="0")
        self.start.place(relx=0.033, rely=0.256, height=34, width=157)

        self.labelImage.configure(text="No corrections required yet.")
        self.labelImage.configure(
            background="#e6e6e6", disabledforeground="#a3a3a3", foreground="#000000")
        self.labelImage.place(relx=0.417, rely=0.022, height=221, width=314)

        self.errorLabel.configure(
            wraplength=224, activebackground="#f9f9f9", activeforeground="black",
            background="#e1e1e1", disabledforeground="#a3a3a3", foreground="#ff0000",
            highlightbackground="#d9d9d9", highlightcolor="black")
        self.errorLabel.place(relx=0.017, rely=0.356, height=71, width=224)

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

    # GUI Functions

    def run(self):
        self.root.mainloop()

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


class PopupTag:
    # GUI Components
    popupBox = None
    popupDescription = None
    popupOK = None
    top = None

    def __init__(self, top, title, text, color="#000000"):
        self.top = top

        self.popupBox = tkinter.Toplevel()
        self.popupDescription = tkinter.Text(self.popupBox)
        self.popupOK = tkinter.Button(self.popupBox)

        self.popupBox.geometry("335x181+475+267")
        self.popupBox.minsize(120, 1)
        self.popupBox.maxsize(1370, 749)
        self.popupBox.resizable(1, 1)
        self.popupBox.configure(background="#d9d9d9")
        self.popupBox.title = title

        self.popupDescription.insert("end", text)
        self.popupDescription.configure(
            foreground=color, wrap="word", state="disabled", background="#FFFFFF",
            font="TkTextFont", highlightbackground="#d9d9d9", highlightcolor="black",
            insertbackground="black", selectbackground="#c4c4c4", selectforeground="black")
        self.popupDescription.place(
            relx=0.03, rely=0.055, height=91, width=314)
        self.popupOK.configure(text="OK", command=self.end)
        self.popupOK.configure(
            activebackground="#ececec", activeforeground="#000000", background="#ebebeb",
            disabledforeground="#a3a3a3", foreground="#000000", highlightbackground="#d9d9d9",
            highlightcolor="black", pady="0")
        self.popupOK.place(relx=0.328, rely=0.663, height=34, width=117)

    def run(self):
        self.popupBox.mainloop()

    def end(self):
        self.popupBox.destroy()
        self.top.root.destroy()


class InstallError:
    # Variables
    name = None
    URL = None
    fileName = None

    # Fonts
    font11 = "-family {Segoe UI} -size 18 -weight bold"
    font13 = "-family {Segoe UI} -size 16 -weight bold"

    # Text
    text_description = "Warning: Youre missing {name}. it is a required software to make this tool run. To fix this issue, please follow the instructions below."

    # GUI Components
    root = None
    header = None
    description = None
    link = None
    orLabel = None
    location = None
    downloadLabel = None
    navigateLabel = None

    def __init__(self, name, URL, filename):
        self.name = name
        self.URL = URL
        self.fileName = filename

        self.root = tkinter.Tk(baseName="Missing Software")
        self.header = tkinter.Label(self.root)
        self.description = tkinter.Label(self.root)
        self.link = tkinter.Label(self.root)
        self.orLabel = tkinter.Label(self.root)
        self.location = tkinter.Label(self.root)
        self.downloadLabel = tkinter.Button(self.root)
        self.navigateLabel = tkinter.Button(self.root)

        self.root.title("Missing Software")
        self.root.geometry("438x478")
        self.root.minsize(120, 1)
        self.root.maxsize(1370, 749)
        self.root.resizable(1, 1)
        self.root.configure(background="#d9d9d9")

        self.header.configure(text="Software Not Installed")
        self.header.configure(
            font=self.font11, activeforeground="#372fd7", background="#d9d9d9",
            disabledforeground="#a3a3a3", foreground="#2432d9")
        self.header.place(relx=0.16, rely=0.042, height=61, width=294)

        self.header.configure(text=self.text_description.format(name=name))
        self.description.configure(
            font="-family {Segoe UI} -size 14", background="#ffffff",
            disabledforeground="#a3a3a3", foreground="#000000", wraplength="294")
        self.description.place(relx=0.16, rely=0.167, height=151, width=294)

        self.link.configure(
            text="If you havent already installed this software, please follow the download link.")
        self.link.configure(
            background="#eeeeee", disabledforeground="#a3a3a3", foreground="#000000",
            wraplength="294")
        self.link.place(relx=0.16, rely=0.523, height=31, width=294)

        self.orLabel.configure(text="Or")
        self.orLabel.configure(
            font="-family {Segoe UI} -size 16 -weight bold",
            background="#d9d9d9", disabledforeground="#a3a3a3", foreground="#29c1dc")
        self.orLabel.place(relx=0.457, rely=0.69, height=36, width=40)

        self.location.configure(
            text="If you've already installed the software, please lead us to where it is as we cannot find it.")
        self.location.configure(
            background="#eeeeee", wraplength="294",
            disabledforeground="#a3a3a3", foreground="#000000")
        self.location.place(relx=0.16, rely=0.774, height=41, width=294)

        self.downloadLabel.configure(
            text="Download {name}".format(name=name), command=self.download)
        self.downloadLabel.configure(
            font=self.font11, activebackground="#ececec", activeforeground="#000000",
            background="#48d250", disabledforeground="#a3a3a3", foreground="#000000",
            highlightbackground="#d9d9d9", highlightcolor="black", pady="0")
        self.downloadLabel.place(relx=0.16, rely=0.607, height=34, width=297)

        self.navigateLabel.configure(
            text="Navigate to {name}".format(name=name), command=self.navigate)
        self.navigateLabel.configure(
            font=self.font13, activebackground="#ececec", activeforeground="#000000",
            background="#eaecec", disabledforeground="#a3a3a3", foreground="#000000",
            highlightbackground="#d9d9d9", highlightcolor="black", pady="0")
        self.navigateLabel.place(relx=0.16, rely=0.879, height=34, width=297)

    def run(self):
        self.root.mainloop()

    def download(self):
        import webbrowser
        webbrowser.open(self.URL, autoraise=True)

    def navigate(self):
        from os import getenv, system
        path = filedialog.askopenfilename(
            filetypes=((self.name, self.fileName), (self.name, self.fileName)))
        path = dirname(normpath(path))
        if (getenv("path")[-1] != ";"):
            path = ";" + path
        if(len(getenv("path") + path) >= 1024):
            self.description.configure(
                text="Error: we could not add the file to your path for you. You will have to do this manually.")
        if getenv("userprofile") in path:
            if(system("setx PATH \"%path%" + path + "\"")):
                print("Failed to do command")
        else:
            if(system("setx PATH /M \"%path%" + path + "\"")):
                print("failed to do command")
