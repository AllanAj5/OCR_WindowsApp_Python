
from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from PIL import Image, ImageTk

import matplotlib.pyplot as plt
import cv2
import easyocr
from pylab import rcParams
import os
#from IPython.display import Image


class Root(Tk):
    def __init__(self):
        super(Root, self).__init__()
        self.minsize(640, 400)

        self.labelFrame = ttk.LabelFrame(self, text = "Open File")
        self.labelFrame.grid(column = 0, row = 1, padx = 20, pady = 20)
        
        self.CamlabelFrame = ttk.LabelFrame(self, text = "Press Space to Capture Image")
        self.CamlabelFrame.grid(column = 5, row = 1, padx = 20, pady = 20)

        self.button()
        self.Cambutton()


    def button(self):
        self.button = ttk.Button(self.labelFrame, text = "Browse A File",command = self.fileDialog)
        self.button.grid(column = 1, row = 1)
        
    def Cambutton(self):
        self.Cambutton = ttk.Button(self.CamlabelFrame, text = "Open Camera",command = self.loadCamera)
        self.Cambutton.grid(column = 6, row = 1)
        
    #-----------------------------------Image Processing Logic --------------------------------- 
    def imgProcess(self,pic_name):
        
        """Set Image on Window"""
        img = Image.open(pic_name)
        img = img.resize((250, 250))
        photo = ImageTk.PhotoImage(img)

        self.label2 = Label(image=photo)
        self.label2.image = photo 
        self.label2.grid(column=0, row=3)
        """END OF Set Image"""
        
        rcParams['figure.figsize'] = 8, 16
        
        
        
        reader = easyocr.Reader(['en'])
        
        #Image(img)
        
        output = reader.readtext(pic_name)
        
        image = cv2.imread(pic_name)
        
        outputprint = ""
        
        for word in output:
          outputprint += word[-2] + " "  
          cord = word[0]
          x_min, y_min = [int(min(idx)) for idx in zip(*cord)]
          x_max, y_max = [int(max(idx)) for idx in zip(*cord)]
          
          cv2.rectangle(image,(x_min,y_min),(x_max,y_max),(0,0,255),2)
          plt.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        print(outputprint)
        self.label3 = ttk.Label(text = "")
        self.label3.configure(text=outputprint)
        self.label3.grid(column=0,row=5)
        
        



    def fileDialog(self):

        self.filename = filedialog.askopenfilename(initialdir =  "/", title = "Select A File", filetype =
        (("jpeg files","*.jpg"),("all files","*.*")) )
        self.label = ttk.Label(self.labelFrame, text = "")
        self.label.grid(column = 1, row = 2)
        self.label.configure(text = self.filename)

        
        self.imgProcess(self.filename)
        
        
        
    
        
        
   
        
        
    def loadCamera(self):
        cam = cv2.VideoCapture(0,cv2.CAP_DSHOW)

        cv2.namedWindow("Image Capture")
        
        img_counter = 0
        
        while True:
            ret, frame = cam.read()
            if not ret:
                print("failed to grab frame")
                break
            cv2.imshow("Image Capture", frame)
        
            k = cv2.waitKey(1)
            
            # if k%256 == 27:
            #     # ESC pressed
            #     print("Escape hit, closing...")
            #     break
            if k%256 == 32:
                # SPACE pressed
                img_name = "photo{}.png".format(img_counter)
                cv2.imwrite(img_name, frame)
                print("{} written!".format(img_name))
                img_counter += 1
                f_name = os.getcwd()+"\\photo0.png"
                
                self.imgProcess(f_name)
                break
        
        cam.release()
        
        cv2.destroyAllWindows()
        
 

root = Root()
root.mainloop()
