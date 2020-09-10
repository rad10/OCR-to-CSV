# How to install OCR to CSV
I have attempted to make the installation of this software as easy as possible.
For the short summary, you need these programs installed first before use:

* Python (preferably 3.8)
* [Poppler](http://blog.alivate.com.au/poppler-windows/)
* [Tesseract](https://github.com/UB-Mannheim/tesseract/wiki)

For the long summary, you need to start off by installing python. This problem will not run without python installed, period. Tesseract needs to be installed as an external program and is arguably one of the most important programs regarding this software. Poppler is a library used by the software to allow use of PDF’s in the application. Without this library, the software couldn’t read a signin sheet that was scanned in as a PDF.

## Installing
**Tesseract** - Run the installer found at the link above and you should have tesseract installed. If youre worried that tesseract might not be seen, you can add tesseract to your [*path*](https://www.howtogeek.com/118594/how-to-edit-your-system-path-for-easy-command-line-access/). To test if you added it correctly, open up command prompt and run this command `tesseract` if you get a help screen, you have linked it correctly.

**Poppler** - Poppler is a set of libraries with executables, but it doesnt come with an installer like tesseract. To access the libraries, you will first need to have [7zip](https://www.7-zip.org/download.html) in order to open the compressed folder. To make this work with OCR-To-CSV, you will need to find a space where you would like to keep your folder, then add it to your [*path*](https://www.howtogeek.com/118594/how-to-edit-your-system-path-for-easy-command-line-access/). In order to check that what you did worked, open up a command prompt and place this command `pdftotext`. If you get a help screen, its ready to go.

## Installing python requirements

You will also need to install the required libraries to run the application as well. To do this, open up either a command prompt, or powershell in the directory where you placed OCR-To-CSV. In there, run the command `pip3 install -r requirements.txt` and it will install all the libraries that you will need.

And like that, you should have everything that you will ever need installed and ready to run the application. Just open up the application and see if any errors occur.