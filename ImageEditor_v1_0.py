#ImageEditor_v1_0.py
#

#v0_1test
#Now draws directly to image data, and updates the canvas with it.
#Color selection window also works with it.
#v0_2test
#addColorFilter implemented.
#invertColorFilter implemented.
#grayscaleFilter implemented.
#v0_3test
#bwFilter implemented.
#hFlip implemented.
#vFlip implemented.
#aaBlurFilter implemented. Slight blur by averaging adjacent pixels.
#v0_4test
#Line drawing now works, leaving no major gaps between cursor locations when dragged.
#aaSharpenFilter added, but may not produce intended result in current form.
#v0_5test
#Changed main window height from 800 to 750 to fit better on my machine -Roland
#   Buttons at the bottom of the window were obscured by the Windows taskbar.
#Added File Browser load functionality.
#Added buttons for filters. (Still need input prompt for addColor)
#Image undo and redo implemented.
#v0_6test
#Implemented undo for load image.
#Added New Image button. (Still need input prompt for dimensions)
#v0_7
#Changed the initial loading to create a blank image instead of a test image.
#Changed main window background color to a light gray so it does not blend in with white blank images.
#Changed line drawing to check each point along the line. Now draws partial line if one endpoint is off image.
#Fixed line drawing to draw at x and y position 0. x & y >= 0 instead of x & y > 0.
#v0_8
#Added input prompts for "New Image" and "Add Color" buttons.
#   Can possibly be improved:
#       Have all inputs requested in a single dialog window
#       Or figure out a way to prevent second input dialog window from initially being behind the main window
#Added "Quantize Colors" filter with input dialog box.
#v0_9
#Increased window width from 1000 to 1200 for additional button room.
#Added internal functions for conversions between RGB and HSV.
#Added Invert Value filter.
#Fixed New Image input. Considers 0 and None different inputs.
#   0 is invalid value
#   None means the "Cancel" button was pressed
#Added error message boxes for invalid inputs into "New Image".
#Added error message box for failed image loading during "Load Image".
#Increased arbitrary undo stack size limit to 5 from 3.
#Added notice message boxes when attempting to undo or redo when the appropratestack is emtpy.
#v1_0
#Removed empty brush size customization window.


#todo: Implement filters. can try using https://pillow.readthedocs.io/en/stable/reference/Image.html#PIL.Image.eval
#   AddSaturation
#   ShiftHue
#   AddValue
#   InvertHue
#todo: Implement brush customization.
#todo: Implement aplha functionality for brush.
#   Also add "replace" and "add" modes
#   With brush color at half opacity:
#       Replace mode sets the pixel to the brush color and half opacity
#       Add mode mixes the existing pixel color with the brush color
#           May need to change line draw function to not draw when the cursor doesn't move
#todo: Implement color dropper tool to pick a brush color from a pixel of the image.
#todo: Implement Fill tool.
#todo: Put filters in drop-down list.
#todo: Implement Save Image with overwrite confirmation.
#todo: Display current color in brush window.

#Notes to self:
#Check if modifications can be done directly to PhotoImage object instead of Image object and converting
#Try using dynamic programming to temporarily keep accessed pixel values during blur and sharpen functions to increase efficiency.

#Possible later features:
#Implement layers
#Make Undo and Redo buttons grayed-out when the corresponding stack is empty.
#In a separate window, list operations that are undoable and redoable.
#Improve efficiency of image Undo/Redo by tracking pixel changes for non-filter operations.


import tkinter as tk
from tkinter import colorchooser, filedialog, simpledialog
from PIL import Image, ImageTk

class ImageEditorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Editor")
        self.root.geometry("1200x750")

        #Draw line variables
        self.oldx = None
        self.oldy = None

        #Undo and Redo stacks for image edits.
        #(Can make separate stacks for changes to brushColor later)
        #(Can make separate stacks for changes to layer order later, if layers are implemented)
        self.undoImageStack = []
        self.redoImageStack = []
        #Arbitrary limit to how many operations can be saved to a stack.
        self.imageStackLimit = 5
        
        '''
        #Try inputing raw data into PIL image object, then loading into tkinter -Roland
        self.imgpath = "C:\\Users\\VYTO\\Documents\\CSU\\2024 08Aug Fall\\CIS 434 Software Engineering\\ImageEditor\\Mickey_500x500.png"
        #self.imgpath = "/Users/zupe/Documents/CIS434/Abdullahpicture.png"
        #self.imgpath = "/Users/khizzerahmed/Downloads/image_123650291 (1).JPG"
        try:
            self.img = Image.open(self.imgpath).convert("RGBA")
            self.imgdata = ImageTk.PhotoImage(self.img)
            #print("Initial image loaded successfully")
        except FileNotFoundError:
            print(f"Error: Image not found at {self.imgpath}")
            self.img = Image.new("RGBA", (500, 500), (255, 255, 255, 255))
            self.imgdata = ImageTk.PhotoImage(self.img)
            print("Loaded blank image as fallback")
        self.imgdata = ImageTk.PhotoImage(self.img)
        '''

        #Initially create blank image
        self.imgpath = ""
        self.img = Image.new("RGBA", (500, 500), (255, 255, 255, 255))
        self.imgdata = ImageTk.PhotoImage(self.img)
        
        self.brushSize = 1
        self.brushColor = (0, 0, 0, 255) #Full opacity black in RGBA
        
        self.createMainCanvas()
        self.createToolbar()

        #self.openBrushSizeWindow()
        self.openColorChangeWindow()

        #Bind mouse events for drawing
        self.canvas.bind("<B1-Motion>", self.paint)
        self.canvas.bind("<ButtonRelease-1>", self.paintFinish)
        self.canvas.bind("<Button-1>", self.paintStart)

    def createMainCanvas(self):
        self.canvas = tk.Canvas(self.root, bg="#F0F0F0")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        #Draw initial image
        self.canvas.create_image(0, 0, anchor = tk.NW, image = self.imgdata)

    def createToolbar(self):
        toolbar = tk.Frame(self.root, bg="Black")
        toolbar.pack(side=tk.TOP, fill=tk.X)

        #New Image button
        #loadImageButton = tk.Button(toolbar, text="New Image", command=lambda: self.newImage(500, 500, (255, 255, 255, 255)))
        loadImageButton = tk.Button(toolbar, text="New Image", command=self.newImageChoice)
        loadImageButton.pack(side=tk.LEFT, padx=5, pady=5)

        #Load Image button
        loadImageButton = tk.Button(toolbar, text="Load Image", command=self.loadImage)
        loadImageButton.pack(side=tk.LEFT, padx=5, pady=5)

        #Buttons for toolbar: Undo & Redo
        undoButton = tk.Button(toolbar, text="Undo", command=self.imageUndo)
        undoButton.pack(side=tk.LEFT, padx=5, pady=5)
        
        undoButton = tk.Button(toolbar, text="Redo", command=self.imageRedo)
        undoButton.pack(side=tk.LEFT, padx=5, pady=5)
        
        #Create filter buttons and add them to the toolbar
        addColorButton = tk.Button(toolbar, text="Add Color", command=self.addColorFilter)
        addColorButton.pack(side=tk.LEFT, padx=5, pady=5)

        invertColorButton = tk.Button(toolbar, text="Invert Colors", command=self.invertColorFilter)
        invertColorButton.pack(side=tk.LEFT, padx=5, pady=5)

        grayscaleButton = tk.Button(toolbar, text="Grayscale", command=self.grayscaleFilter)
        grayscaleButton.pack(side=tk.LEFT, padx=5, pady=5)

        bwButton = tk.Button(toolbar, text="Black & White", command=self.bwFilter)
        bwButton.pack(side=tk.LEFT, padx=5, pady=5)

        hFlipButton = tk.Button(toolbar, text="Horizontal Flip", command=self.hFlip)
        hFlipButton.pack(side=tk.LEFT, padx=5, pady=5)

        vFlipButton = tk.Button(toolbar, text="Vertical Flip", command=self.vFlip)
        vFlipButton.pack(side=tk.LEFT, padx=5, pady=5)

        blurButton = tk.Button(toolbar, text="Blur", command=self.aaBlurFilter)
        blurButton.pack(side=tk.LEFT, padx=5, pady=5)

        sharpenButton = tk.Button(toolbar, text="Sharpen", command=self.aaSharpenFilter)
        sharpenButton.pack(side=tk.LEFT, padx=5, pady=5)
        
        quantizeButton = tk.Button(toolbar, text="Quantize", command=self.quantize)
        quantizeButton.pack(side=tk.LEFT, padx=5, pady=5)
        
        invertValueButton = tk.Button(toolbar, text="Invert Value", command=self.invertValue)
        invertValueButton.pack(side=tk.LEFT, padx=5, pady=5)

    #Unimplemented Brush Size customization window
    """def openBrushSizeWindow(self):
        brushWindow = tk.Toplevel(self.root)
        brushWindow.title("Brush Size")
        brushWindow.geometry("300x100")

        '''
        tk.Label(brushWindow, text="Brush Size:").pack(pady=10)
        brushSlider = tk.Scale(brushWindow, from_=1, to=50, orient=tk.HORIZONTAL)
        brushSlider.set(self.brushSize)
        brushSlider.pack()

        def updateBrushSize():
            self.brushSize = brushSlider.get()

        tk.Button(brushWindow, text="Set Brush Size", command=updateBrushSize).pack(pady=10)
        '''"""

    def openColorChangeWindow(self):
        colorWindow = tk.Toplevel(self.root)
        colorWindow.title("Brush Color")
        colorWindow.geometry("300x150")

        def chooseColor():
            color = colorchooser.askcolor()[1]  
            if color:
                #Set a full-opacity color
                #Color is a string of hex values starting with character #
                #Convert to RGB decimal values
                color = (int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16), 255)
                self.brushColor = color

        tk.Label(colorWindow, text="Choose Brush Color:").pack(pady=10)
        tk.Button(colorWindow, text="Select Color", command=chooseColor).pack(pady=10)

    def refreshImage(self):
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor = tk.NW, image = self.imgdata)

    def newImage(self, w, h, bgcolor):
        self.storeImageUndo()
        self.redoImageStack = []
        self.img = Image.new("RGBA", (w, h), bgcolor)
        self.imgdata = ImageTk.PhotoImage(self.img)
        self.refreshImage()

    def newImageChoice(self):
        x = simpledialog.askinteger("Input", "Enter new image width")
        if x == None:
            return None
        if x < 1:
            print("Invalid width")
            msg = tk.messagebox.showerror("Error", "Invalid image width.")
            return None
        y = simpledialog.askinteger("Input", "Enter new image height")
        if y == None:
            return None
        if y < 1:
            print("Invalid height")
            msg = tk.messagebox.showerror("Error", "Invalid image height.")
            return None
        self.newImage(x, y, (255, 255, 255, 255))

    def loadImage(self):
        """Allows the user to select and load an image from their file system."""
        filepath = filedialog.askopenfilename(
            title="Select an Image",
            filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp;*.gif")]
        )
        if filepath:
            self.storeImageUndo()
            try:
                self.img = Image.open(filepath).convert("RGBA")
                #print("Image loaded successfully")
                #print("Image size:", self.img.size)
                #print("Image mode:", self.img.mode)
                self.imgdata = ImageTk.PhotoImage(self.img)
                self.refreshImage()
                self.redoImageStack = []
            except Exception as e:
                #Remove the undo copy since it wasn't a completed operation.
                self.undoImageStack = self.undoImageStack[:-1]
                print("Error loading image:", e)
                msg = tk.messagebox.showerror("Error", "Error loading image.")

    def paint(self, event):
        #Old version:
        '''
        x, y = event.x, event.y
        """#Old draw-to-canvas paint
        radius = self.brushSize // 2
        self.canvas.create_oval(x - radius, y - radius, x + radius, y + radius, fill=self.brushColor, outline=self.brushColor)
        """
        #Test direct drawing to image object - Roland
        #print(self.brushColor) #Debug to see brushColor value
        self.img.putpixel((x, y), self.brushColor)
        self.imgdata = ImageTk.PhotoImage(self.img)
        self.refreshImage()
        '''
        x, y = event.x, event.y
        if self.oldx != None and self.oldy != None and ((self.oldx >= 0 and self.oldx < self.img.width and self.oldy >= 0 and self.oldy < self.img.height) or (x >= 0 and x < self.img.width and y >= 0 and y < self.img.height)):
                self.drawLine(self.oldx, self.oldy, x, y)
        elif x >= 0 and x < self.img.width and y >= 0 and y < self.img.height:
            self.img.putpixel((x, y), self.brushColor)
            self.imgdata = ImageTk.PhotoImage(self.img)
            self.refreshImage()
        self.oldx = x
        self.oldy = y

    def paintStart(self, event):
        #Copy current image version to undo stack at this time.
        x, y = event.x, event.y
        self.storeImageUndo()
        self.redoImageStack = []
        if x >= 0 and x < self.img.width and y >= 0 and y < self.img.height:
            self.img.putpixel((x, y), self.brushColor)
            self.imgdata = ImageTk.PhotoImage(self.img)
            self.refreshImage()
        #self.aaBlurFilter()
        #self.aaSharpenFilter()
        self.oldx = x
        self.oldy = y

    def paintFinish(self, event):
        #x, y = event.x, event.y
        #No longer click-and-dragging cursor, so no old position to draw lines from.
        self.oldx = None
        self.oldy = None

    def drawLine(self, x1, y1, x2, y2):
        #For coding simplicity, make sure x1 is always less than x2.
        if x1 > x2:
            tempx = x2
            x2 = x1
            x1 = tempx
            tempy = y2
            y2 = y1
            y1 = tempy
        #If start and end points are the same, draw to a single pixel.
        if x1 == x2 and y1 == y2:
            self.checkPlace((x2, y2), self.brushColor)
        #If no change in y, draw a horizontal line.
        elif y1 == y2:
            for i in range((x2 - x1)):
                self.checkPlace(((x1 + i), y2), self.brushColor)
        #If no change in x, draw a vertical line.
        elif x1 == x2:
            if y1 > y2:
                tempy = y2
                y2 = y1
                y1 = tempy
            for i in range((y2 - y1)):
                self.checkPlace((x2, (y1 + i)), self.brushColor)
        #If exactly diagonal, increment x and y at the same rate.
        elif abs(x2 - x1) == abs(y2 - y1):
            if y1 > y2:
                for i in range((x2 - x1)):
                    self.checkPlace(((x1 + i), (y1 - i)), self.brushColor)
            else:
                for i in range((x2 - x1)):
                    self.checkPlace(((x1 + i), (y1 + i)), self.brushColor)
        #If shallow slope, increment x at a rate of 1 and select the nearest y to the line path.
        elif abs(x2 - x1) > abs(y2 - y1):
            ystep = (y2 - y1)/(x2 - x1)
            for i in range((x2 - x1)):
                self.checkPlace(((x1 + i), int(y1 + (ystep * i) + 0.5)), self.brushColor)
        #If steep slope, increment y at a rate of 1 and select the nearest x to the line path.
        else:
            ystep = int((y2 - y1)/(abs(y2 - y1))) #+/-1, sign of y2 - y1
            xstep = (x2 - x1)/(abs(y2 - y1))
            for i in range(abs(y2 - y1)):
                self.checkPlace((int(x1 + (xstep * i) + 0.5), (y1 + (ystep * i))), self.brushColor)
        self.imgdata = ImageTk.PhotoImage(self.img)
        self.refreshImage()

    def checkPlace(self, xy, color):
        #Checks if a pixel is within the bounds of the image before drawing to the pixel.
        if xy[0] >= 0 and xy[0] < self.img.width and xy[1] >= 0 and xy[1] < self.img.height:
            self.img.putpixel(xy, color)

    def storeImageUndo(self):
        #self.history.append(self.canvas.create_image(0, 0, anchor=tk.NW))
        #If stack size limit is reached, drop the oldest element.
        if len(self.undoImageStack) == self.imageStackLimit:
            self.undoImageStack = self.undoImageStack[1:]
        self.undoImageStack.append(self.img.copy())

    def imageUndo(self):
        if len(self.undoImageStack) > 0:
            self.storeImageRedo()
            self.img = self.undoImageStack.pop()
            self.imgdata = ImageTk.PhotoImage(self.img)
            self.refreshImage()
        else:
            print("No undo-able image changes.")
            msg = tk.messagebox.showinfo("Error", "No undo-able changes.")
        '''if self.history:
            last_action = self.history.pop()
            self.canvas.delete(last_action)'''

    def storeImageRedo(self):
        if len(self.redoImageStack) == self.imageStackLimit:
            self.redoImageStack = self.redoImageStack[1:]
        self.redoImageStack.append(self.img.copy())

    def imageRedo(self):
        if len(self.redoImageStack) > 0:
            self.storeImageUndo()
            self.img = self.redoImageStack.pop()
            self.imgdata = ImageTk.PhotoImage(self.img)
            self.refreshImage()
        else:
            print("No redo-able image changes.")
            msg = tk.messagebox.showinfo("Error", "No redo-able changes.")

    def addColorFilter(self):
        #Negative values will subtract properly.
        #May modify later to add alpha/opacity
        r = simpledialog.askinteger("Input", "Enter a red value:")
        if r == None:
            return None
        else:
            try:
                r = byteChangeLimit(int(r))
            except:
                print("Invalid value type given.")
                return None
        g = simpledialog.askinteger("Input", "Enter a green value:")
        if g == None:
            return None
        else:
            try:
                g = byteChangeLimit(int(g))
            except:
                print("Invalid value type given.")
                return None
        b = simpledialog.askinteger("Input", "Enter a blue value:")
        if b == None:
            return None
        else:
            try:
                b = byteChangeLimit(int(b))
            except:
                print("Invalid value type given.")
                return None
        self.storeImageUndo()
        self.redoImageStack = []
        for i in range(self.img.width):
            for j in range(self.img.height):
                colors = self.img.getpixel((i, j))
                newRed = byteLimit(colors[0] + r)
                newGreen = byteLimit(colors[1] + g)
                newBlue = byteLimit(colors[2] + b)
                self.img.putpixel((i, j), (newRed, newGreen, newBlue, colors[3]))
        self.imgdata = ImageTk.PhotoImage(self.img)
        self.refreshImage()

    def invertColorFilter(self):
        self.storeImageUndo()
        self.redoImageStack = []
        for i in range(self.img.width):
            for j in range(self.img.height):
                colors = self.img.getpixel((i, j))
                newRed = 255 - colors[0]
                newGreen = 255 - colors[1]
                newBlue = 255 - colors[2]
                self.img.putpixel((i, j), (newRed, newGreen, newBlue, colors[3]))
        self.imgdata = ImageTk.PhotoImage(self.img)
        self.refreshImage()

    def grayscaleFilter(self):
        self.storeImageUndo()
        self.redoImageStack = []
        for i in range(self.img.width):
            for j in range(self.img.height):
                colors = self.img.getpixel((i, j))
                #Adding 0.5 to the following causes the conversion from float to int to round to the nearest whole number instead of rounding down.
                newColor = byteLimit(int((colors[0] + colors[1] + colors[2] + 0.5)/3))
                self.img.putpixel((i, j), (newColor, newColor, newColor, colors[3]))
        self.imgdata = ImageTk.PhotoImage(self.img)
        self.refreshImage()

    def bwFilter(self):
        self.storeImageUndo()
        self.redoImageStack = []
        for i in range(self.img.width):
            for j in range(self.img.height):
                colors = self.img.getpixel((i, j))
                #Adding 0.5 to the following causes the conversion from float to int to round to the nearest whole number instead of rounding down.
                newColor = byteLimit(int((colors[0] + colors[1] + colors[2] + 0.5)/3))
                if newColor > (255/2):
                    newColor = 255
                else:
                    newColor = 0
                self.img.putpixel((i, j), (newColor, newColor, newColor, colors[3]))
        self.imgdata = ImageTk.PhotoImage(self.img)
        self.refreshImage()

    def hFlip(self):
        self.storeImageUndo()
        self.redoImageStack = []
        newImg = self.img.copy()
        for i in range(self.img.width):
            for j in range(self.img.height):
                pixel = self.img.getpixel((i, j))
                #print((self.img.width - 1) - i)
                newImg.putpixel(((self.img.width - 1) - i, j), pixel)
        self.img = newImg
        self.imgdata = ImageTk.PhotoImage(self.img)
        self.refreshImage()

    def vFlip(self):
        self.storeImageUndo()
        self.redoImageStack = []
        newImg = self.img.copy()
        for i in range(self.img.width):
            for j in range(self.img.height):
                pixel = self.img.getpixel((i, j))
                #print((self.img.width - 1) - i)
                newImg.putpixel((i, (self.img.height - 1) - j), pixel)
        self.img = newImg
        self.imgdata = ImageTk.PhotoImage(self.img)
        self.refreshImage()

    def aaBlurFilter(self):
        self.storeImageUndo()
        self.redoImageStack = []
        #Average of Adjecent Pixels blur
        tempImg = self.img.copy()
        for i in range(tempImg.width):
            for j in range(tempImg.height):
                colors = tempImg.getpixel((i, j))
                a1 = colors[3]
                #Accumulate RGB values from multiple pixels, starting with the middle one.
                reds = [colors[0]]
                greens = [colors[1]]
                blues = [colors[2]]
                #Don't try to add pixels out-of-bounds
                if i > 0:
                    colors = tempImg.getpixel((i - 1, j))
                    reds.append(colors[0])
                    greens.append(colors[1])
                    blues.append(colors[2])
                if i < (tempImg.width - 1):
                    colors = tempImg.getpixel((i + 1, j))
                    reds.append(colors[0])
                    greens.append(colors[1])
                    blues.append(colors[2])
                if j > 0:
                    colors = tempImg.getpixel((i, j - 1))
                    reds.append(colors[0])
                    greens.append(colors[1])
                    blues.append(colors[2])
                if j < (tempImg.height - 1):
                    colors = tempImg.getpixel((i, j + 1))
                    reds.append(colors[0])
                    greens.append(colors[1])
                    blues.append(colors[2])
                r = 0
                #Get the sum of the RGB values
                for c in reds:
                    r += c
                #Divide by the number of RGB values to get the average. Add 0.5 to round to the nearest whole number instead of rounding down.
                r = byteLimit(int((r + 0.5)/len(reds)))
                g = 0
                for c in greens:
                    g += c
                g = byteLimit(int((g + 0.5)/len(greens)))
                b = 0
                for c in blues:
                    b += c
                b = byteLimit(int((b + 0.5)/len(blues)))
                self.img.putpixel((i, j), (r, g, b, a1))
        self.imgdata = ImageTk.PhotoImage(self.img)
        self.refreshImage()

    def aaSharpenFilter(self):
        self.storeImageUndo()
        self.redoImageStack = []
        #Average of Adjecent Pixels sharpen
        newImg = self.img.copy()
        for i in range(newImg.width):
            for j in range(newImg.height):
                colors = newImg.getpixel((i, j))
                r1 = colors[0]
                g1 = colors[1]
                b1 = colors[2]
                a1 = colors[3]
                reds = [colors[0]]
                greens = [colors[1]]
                blues = [colors[2]]
                if i > 0:
                    colors = newImg.getpixel((i - 1, j))
                    reds.append(colors[0])
                    greens.append(colors[1])
                    blues.append(colors[2])
                if i < (newImg.width - 1):
                    colors = newImg.getpixel((i + 1, j))
                    reds.append(colors[0])
                    greens.append(colors[1])
                    blues.append(colors[2])
                if j > 0:
                    colors = newImg.getpixel((i, j - 1))
                    reds.append(colors[0])
                    greens.append(colors[1])
                    blues.append(colors[2])
                if j < (newImg.height - 1):
                    colors = newImg.getpixel((i, j + 1))
                    reds.append(colors[0])
                    greens.append(colors[1])
                    blues.append(colors[2])
                r = 0
                for c in reds:
                    r += c
                r = byteLimit(int((r + 0.5)/len(reds)))
                g = 0
                for c in greens:
                    g += c
                g = byteLimit(int((g + 0.5)/len(greens)))
                b = 0
                for c in blues:
                    b += c
                b = byteLimit(int((b + 0.5)/len(blues)))
                r = byteLimit(r1 + (2 * (r - r1)))
                g = byteLimit(g1 + (2 * (g - g1)))
                b = byteLimit(b1 + (2 * (b - b1)))
                self.img.putpixel((i, j), (r, g, b, a1))
        self.imgdata = ImageTk.PhotoImage(self.img)
        self.refreshImage()

    def quantize(self):
        #Currently doesn't quantize transparency.
        step = simpledialog.askinteger("Input", "Input a gap value (1-255):")
        if not step:
            return None
        if step > 255 or step < 1:
            print("Invalid step value")
            return None
        self.storeImageUndo()
        self.redoImageStack = []
        for i in range(self.img.width):
            for j in range(self.img.height):
                colors = self.img.getpixel((i, j))
                r = colors[0]
                r = byteLimit((r//step)*step)
                g = colors[1]
                g = byteLimit((g//step)*step)
                b = colors[2]
                b = byteLimit((b//step)*step)
                self.img.putpixel((i, j), (r, g, b, colors[3]))
        self.imgdata = ImageTk.PhotoImage(self.img)
        self.refreshImage()

    def invertValue(self):
        self.storeImageUndo()
        self.redoImageStack = []
        for i in range(self.img.width):
            for j in range(self.img.height):
                colors = self.img.getpixel((i, j))
                hsv = rgb2hsv(colors[0], colors[1], colors[2])
                hsv = (hsv[0], hsv[1], 1 - hsv[2])
                rgb = hsv2rgb(hsv[0], hsv[1], hsv[2])
                self.img.putpixel((i, j), (rgb[0], rgb[1], rgb[2], colors[3]))
        self.imgdata = ImageTk.PhotoImage(self.img)
        self.refreshImage()


def byteLimit(value):
    #Ensures value is within the range of 0 to 255, endpoint inclusive.
    #Invalid values are replaced by the nearest valid value.
    if value > 255:
        return 255
    elif value < 0:
        return 0
    else:
        return value
    
def byteChangeLimit(value):
    #Ensures value is within the range of -255 to 255, endpoint inclusive.
    #Invalid values are replaced by the nearest valid value.
    if value > 255:
        return 255
    elif value < -255:
        return -255
    else:
        return value

def rgb2hsv(r, g, b):
    red = r/255
    green = g/255
    blue = b/255
    high = max(red, green, blue)
    low = min(red, green, blue)
    delta = high - low
    h = 0
    if delta == 0:
        h = 0
    elif high == red:
        h = 60 * (((green - blue)/delta)%6)
    elif high == green:
        h = 60 * (((blue - red)/delta) + 2)
    elif high == blue:
        h = 60 * (((red - green)/delta) + 4)
    s = 0
    if high == 0:
        s = 0
    else:
        s = delta/high
    v = high
    return (h, s, v)

def hsv2rgb(h, s, v):
    c = v * s
    x = c * (1 - abs(((h/60)%2) - 1))
    m = v - c
    r = 0
    g = 0
    b = 0
    if h >= 0 and h < 60:
        r = c
        g = x
        b = 0
    elif h >= 60 and h < 120:
        r = x
        g = c
        b = 0
    elif h >= 120 and h < 180:
        r = 0
        g = c
        b = x
    elif h >= 180 and h < 240:
        r = 0
        g = x
        b = c
    elif h >= 240 and h < 300:
        r = x
        g = 0
        b = c
    elif h >= 300 and h < 360:
        r = c
        g = 0
        b = x
    red = (r + m)*255
    green = (g + m)*255
    blue = (b + m)*255
    return (int(red), int(green), int(blue))

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageEditorApp(root)
    root.mainloop()

