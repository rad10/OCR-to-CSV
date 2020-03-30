import tkinter
from math import floor
from os.path import basename, dirname, expanduser, normpath
from time import sleep
from tkinter import filedialog, ttk

from PIL import Image, ImageTk


class MainGUI:
    """ This is the GUI that is used for the entire program. Everything is based
    off of this GUI. Any changes here will reflect directly on the program.
    """
    # Gui Variables
    signinsheet = ""
    output_CSV = normpath(expanduser("~\\Documents\\signinSheetOutput.csv"))
    guess_button = False
    submit_button = False

    # GUI Components
    root = None
    decision = None
    input_file = None
    output_file = None
    start = None
    label_image = None
    error_label = None
    confidence_description = None
    AI_guess = None
    or_label = None
    correction_entry = None
    submit = None

    # Status bars
    sheet_status = None
    progress_bar = None

    def __init__(self, cmd=None):
        # Init GUI Components
        self.root = tkinter.Tk(screenName="OCR To CSV Interpreter")
        self.decision = tkinter.BooleanVar(self.root)
        self.input_file = tkinter.Button(self.root)
        self.output_file = tkinter.Button(self.root)
        self.start = tkinter.Button(self.root)
        self.label_image = tkinter.Label(self.root)
        self.error_label = tkinter.Label(self.root)
        self.confidence_description = tkinter.Label(self.root)
        self.AI_guess = tkinter.Button(self.root)
        self.or_label = tkinter.Label(self.root)
        self.correction_entry = tkinter.Entry(self.root)
        self.submit = tkinter.Button(self.root)

        # Status bars
        self.sheet_status = tkinter.Label(self.root)
        self.progress_bar = ttk.Progressbar(self.root)

        self.root.title("OCR To CSV Interpreter")
        self.root.geometry("600x450+401+150")
        self.root.configure(background="#d9d9d9")
        self.root.minsize(120, 1)
        self.root.maxsize(1370, 749)
        self.root.resizable(1, 1)

        self.input_file.configure(
            text="Select Signin Sheet", command=self.reconfig_input)
        self.input_file.configure(
            activebackground="#ececec", activeforeground="#000000", background="#d9d9d9",
            disabledforeground="#a3a3a3", foreground="#000000",
            highlightbackground="#d9d9d9", highlightcolor="black", pady="0")
        self.input_file.place(relx=0.033, rely=0.044, height=34, width=157)

        self.output_file.configure(
            text=basename(self.output_CSV), command=self.reconfig_output)
        self.output_file.configure(
            activebackground="#ececec", activeforeground="#000000", background="#d9d9d9",
            disabledforeground="#a3a3a3", foreground="#000000", highlightbackground="#d9d9d9",
            highlightcolor="black", pady="0")
        self.output_file.place(relx=0.033, rely=0.156, height=34, width=157)

        self.start.configure(text="Start", command=cmd)
        self.start.configure(
            activebackground="#ececec", activeforeground="#000000", background="#17a252",
            disabledforeground="#a3a3a3", foreground="#ffffff", highlightbackground="#d9d9d9",
            highlightcolor="black", pady="0")
        self.start.place(relx=0.033, rely=0.256, height=34, width=157)

        self.label_image.configure(text="No corrections required yet.")
        self.label_image.configure(
            background="#e6e6e6", disabledforeground="#a3a3a3", foreground="#000000")
        self.label_image.place(relx=0.417, rely=0.022, height=221, width=314)

        self.error_label.configure(
            wraplength=224, activebackground="#f9f9f9", activeforeground="black",
            background="#e1e1e1", disabledforeground="#a3a3a3", foreground="#ff0000",
            highlightbackground="#d9d9d9", highlightcolor="black")
        self.error_label.place(relx=0.017, rely=0.356, height=71, width=224)

        self.confidence_description.configure(
            activebackground="#f9f9f9", activeforeground="black", background="#d9d9d9",
            disabledforeground="#a3a3a3", foreground="#000000", highlightbackground="#d9d9d9",
            highlightcolor="black")
        self.confidence_description.place(
            relx=0.267, rely=0.556, height=31, width=164)

        self.AI_guess.configure(text="No guesses yet.")
        self.AI_guess.configure(
            activebackground="#ececec", activeforeground="#000000", background="#d9d9d9",
            disabledforeground="#a3a3a3", foreground="#000000", highlightbackground="#d9d9d9",
            highlightcolor="black", pady="0", command=self.guess_switch)
        self.AI_guess.place(relx=0.55, rely=0.556, height=34, width=227)

        self.or_label.configure(
            activebackground="#f9f9f9", activeforeground="black", background="#d9d9d9",
            disabledforeground="#a3a3a3", foreground="#000000", highlightbackground="#d9d9d9",
            highlightcolor="black")
        self.or_label.place(relx=0.017, rely=0.689, height=31, width=64)

        self.correction_entry.configure(
            background="white", disabledforeground="#a3a3a3", font="TkFixedFont",
            foreground="#000000", highlightbackground="#d9d9d9", highlightcolor="black",
            insertbackground="black", selectbackground="#c4c4c4", selectforeground="black")
        self.correction_entry.place(
            relx=0.133, rely=0.689, height=30, relwidth=0.557)

        self.submit.configure(text="Submit")
        self.submit.configure(
            activebackground="#ececec", activeforeground="#000000", background="#d9d9d9",
            disabledforeground="#a3a3a3", foreground="#000000", highlightbackground="#d9d9d9",
            highlightcolor="black", pady="0", command=self.submit_switch)
        self.submit.place(relx=0.717, rely=0.689, height=34, width=127)
        self.root.bind("<Return>", self.submit_switch)

        self.sheet_status.configure(
            activebackground="#f9f9f9", activeforeground="black", background="#d9d9d9",
            disabledforeground="#a3a3a3", foreground="#000000", highlightbackground="#d9d9d9",
            highlightcolor="black", anchor="w")
        self.sheet_status.place(relx=0.033, rely=0.844, height=21, width=554)

        self.progress_bar.place(relx=0.017, rely=0.911, relwidth=0.95,
                                relheight=0.0, height=22)

    # GUI Functions

    def run(self):
        """ This starts the GUI """
        self.root.mainloop()

    def guess_switch(self):
        """ Switches decision switch towards the guess """
        self.guess_button = True
        self.decision.set(1)

    def submit_switch(self, event=None):
        """ Switches the decision switch towards what is submitted """
        if(event != None and self.correction_entry.get() == ""):
            return
        self.submit_button = True
        self.decision.set(1)

    def reconfig_output(self):
        """ Changes the output CSV used """
        output_CSV = filedialog.askopenfilename(filetypes=(
            ("Comma Style Values", "*.csv"), ("Comma Style Values", "*.csv")))
        if(output_CSV != ""):
            self.output_file.configure(text=basename(output_CSV))
            self.output_CSV = output_CSV

    def reconfig_input(self):
        """ Changes the input PDF used """
        signinsheet = filedialog.askopenfilename(filetypes=(
            ("PDF Files", "*.pdf"), ("Jpeg Files", "*.jpg"), ("Png Files", "*.png")))
        if(signinsheet != ""):
            self.input_file.configure(text=basename(signinsheet))
            self.signinsheet = signinsheet

    def request_correction(self, display_image, guess=""):
        """This is the function used when a string doesnt confidently match a name.\n
        @param displayImage: The image placed on the display for user to see.\n
        @param {int} col: The column number that the image was found in. This is needed
        for placing the AI's guess.\n
        @param {string} guess: This is to straight up overwrite the AI's guess with the
        string. This can be helpful so that the AI doesnt have to process the image
        again.\n
        @return: the users answer.
        """

        result = ""  # the string to be returned for final answer

        # Setting up image to place in GUI
        image = Image.fromarray(display_image)
        if(display_image.shape[1] > self.label_image.winfo_width()):
            hgt, wth = display_image.shape[:2]
            ratio = self.label_image.winfo_width()/wth
            image = image.resize(
                (floor(wth * ratio), floor(hgt * ratio)), Image.ANTIALIAS)
        image = ImageTk.PhotoImage(image)

        # setting values to labels in gui
        self.label_image.configure(image=image)
        self.label_image.image = image
        self.error_label.configure(
            text="""Uh oh. It looks like we couldnt condifently decide who or
            what this is. We need you to either confirm our guess or type in
            the correct value""")
        self.confidence_description.configure(
            text="Were not confident, but is it:")
        self.AI_guess.configure(text=guess)
        self.or_label.configure(text="or")

        # basically waits till user presses a button and changes variable scope
        self.root.update_idletasks()
        self.root.wait_variable(self.decision)
        result = self.correction_entry.get()

        # Resetting changes made
        self.label_image.configure(image=None)
        self.label_image.image = None
        self.error_label.configure(text="")
        self.confidence_description.configure(text="")
        self.AI_guess.configure(text="")
        self.or_label.configure(text="")
        self.correction_entry.delete(0, "end")
        self.root.update_idletasks()
        sleep(1)
        self.decision.set(0)

        if(self.guess_button):
            self.guess_button = False
            self.submit_button = False
            return (guess, 100, True)
        elif(self.submit_button):
            self.guess_button = False
            self.submit_button = False
            return (result, 100, True)


class PopupTag:
    """ This GUI is designed to popup for the main GUI and give various information.
    It is sometimes used for displaying Errors to the user. It is also used for
    confirming completion of work for the user.
    """
    # GUI Components
    popup_box = None
    popup_description = None
    popup_OK = None
    top = None

    def __init__(self, top, title, text, color="#000000"):
        self.top = top

        self.popup_box = tkinter.Toplevel()
        self.popup_description = tkinter.Text(self.popup_box)
        self.popup_OK = tkinter.Button(self.popup_box)

        self.popup_box.geometry("335x181+475+267")
        self.popup_box.minsize(120, 1)
        self.popup_box.maxsize(1370, 749)
        self.popup_box.resizable(1, 1)
        self.popup_box.configure(background="#d9d9d9")
        self.popup_box.title = title

        self.popup_description.insert("end", text)
        self.popup_description.configure(
            foreground=color, wrap="word", state="disabled", background="#FFFFFF",
            font="TkTextFont", highlightbackground="#d9d9d9", highlightcolor="black",
            insertbackground="black", selectbackground="#c4c4c4", selectforeground="black")
        self.popup_description.place(
            relx=0.03, rely=0.055, height=91, width=314)
        self.popup_OK.configure(text="OK", command=self.end)
        self.popup_OK.configure(
            activebackground="#ececec", activeforeground="#000000", background="#ebebeb",
            disabledforeground="#a3a3a3", foreground="#000000", highlightbackground="#d9d9d9",
            highlightcolor="black", pady="0")
        self.popup_OK.place(relx=0.328, rely=0.663, height=34, width=117)

    def run(self):
        """ This starts the GUI """
        self.popup_box.mainloop()

    def end(self):
        """ This closes the popup and the GUI tied to it """
        self.popup_box.destroy()
        self.top.root.destroy()


class InstallError:
    """ This GUI is only useful for aknowledging errors due to a necessary
    program not being installed. This takes the name of the program as well
    as the download URL for the program in order to provide it to the user.
    """
    # Variables
    name = None
    URL = None
    file_name = None

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
    or_label = None
    location = None
    download_label = None
    navigate_label = None

    def __init__(self, name, URL, filename):
        self.name = name
        self.URL = URL
        self.file_name = filename

        self.root = tkinter.Tk(baseName="Missing Software")
        self.header = tkinter.Label(self.root)
        self.description = tkinter.Label(self.root)
        self.link = tkinter.Label(self.root)
        self.or_label = tkinter.Label(self.root)
        self.location = tkinter.Label(self.root)
        self.download_label = tkinter.Button(self.root)
        self.navigate_label = tkinter.Button(self.root)

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

        self.or_label.configure(text="Or")
        self.or_label.configure(
            font="-family {Segoe UI} -size 16 -weight bold",
            background="#d9d9d9", disabledforeground="#a3a3a3", foreground="#29c1dc")
        self.or_label.place(relx=0.457, rely=0.69, height=36, width=40)

        self.location.configure(
            text="If you've already installed the software, please lead us to where it is as we cannot find it.")
        self.location.configure(
            background="#eeeeee", wraplength="294",
            disabledforeground="#a3a3a3", foreground="#000000")
        self.location.place(relx=0.16, rely=0.774, height=41, width=294)

        self.download_label.configure(
            text="Download {name}".format(name=name), command=self.download)
        self.download_label.configure(
            font=self.font11, activebackground="#ececec", activeforeground="#000000",
            background="#48d250", disabledforeground="#a3a3a3", foreground="#000000",
            highlightbackground="#d9d9d9", highlightcolor="black", pady="0")
        self.download_label.place(relx=0.16, rely=0.607, height=34, width=297)

        self.navigate_label.configure(
            text="Navigate to {name}".format(name=name), command=self.navigate)
        self.navigate_label.configure(
            font=self.font13, activebackground="#ececec", activeforeground="#000000",
            background="#eaecec", disabledforeground="#a3a3a3", foreground="#000000",
            highlightbackground="#d9d9d9", highlightcolor="black", pady="0")
        self.navigate_label.place(relx=0.16, rely=0.879, height=34, width=297)

    def run(self):
        """ This starts the GUI """
        self.root.mainloop()

    def download(self):
        """ Runs command to open URL in users web browser """
        import webbrowser
        webbrowser.open(self.URL, autoraise=True)

    def navigate(self):
        """ If the user has already installed the program, but the program
        doesnt see it, it'll attempt to add the program to the user's path
        so that the user doesnt have to explain where the program is every
        time it is open.
        """
        from os import getenv
        from subprocess import call
        path = filedialog.askopenfilename(
            filetypes=((self.name, self.file_name), (self.name, self.file_name)))
        path = dirname(normpath(path))
        if (getenv("path")[-1] != ";"):
            path = ";" + path
        if(len(getenv("path") + path) >= 1024):
            self.description.configure(
                text="Error: we could not add the file to your path for you. You will have to do this manually.")
        if getenv("userprofile") in path:
            if call(["setx", "PATH", '%path%' + path + '"'], shell=True):
                print("Failed to do command")
        else:
            if call(["setx", "PATH", "/M", '"%path%' + path + '"'], shell=True):
                print("failed to do command")
