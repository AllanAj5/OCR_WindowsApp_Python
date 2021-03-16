# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 25 12:43:31 2021

@author: Allan
"""


from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from PIL import Image, ImageTk

import matplotlib.pyplot as plt
import cv2
import easyocr
from pylab import rcParams
import os
import time

import FocusStack

#from IPython.display import Image





class Root(Tk):
    def __init__(self):
        super(Root, self).__init__()
        self.minsize(640, 400)

        self.labelFrame = ttk.LabelFrame(self, text = "Open File")
        self.labelFrame.grid(column = 0, row = 1, padx = 20, pady = 20)
        
        self.CamlabelFrame = ttk.LabelFrame(self, text = "Normal")
        self.CamlabelFrame.grid(column = 1, row = 1, padx = 20, pady = 20)
        
        self.imgStacklabelFrame = ttk.LabelFrame(self, text = "Image Stack")
        self.imgStacklabelFrame.grid(column = 2, row = 1, padx = 20, pady = 20)
        
        self.meanMaxlabelFrame = ttk.LabelFrame(self, text = "Mean Max Acc")
        self.meanMaxlabelFrame.grid(column = 3, row = 1, padx = 20, pady = 20)

        self.button()
        self.Cambutton()
        self.stackButton()
        self.meanMaxButton()
        self.initialize_ocr()


    def button(self):
        self.button = ttk.Button(self.labelFrame, text = "Browse A File",command = self.fileDialog)
        self.button.grid(column = 1, row = 1)
        
    def Cambutton(self):
        self.Cambutton = ttk.Button(self.CamlabelFrame, text = "Open Camera",command = self.loadCamera)
        self.Cambutton.grid(column = 6, row = 1)
        
    def stackButton(self):
        self.stackButton = ttk.Button(self.imgStacklabelFrame, text = "Stack Cam",command = self.stackCamera)
        self.stackButton.grid(column = 1, row = 1)
    
    def meanMaxButton(self):
        self.meanMaxbutton = ttk.Button(self.meanMaxlabelFrame, text = "Max Cam",command = self.meanMaxCamera)
        self.meanMaxbutton.grid(column = 6, row = 1)
    
    def initialize_ocr(self):
        rcParams['figure.figsize'] = 8, 16
        global reader 
        reader = easyocr.Reader(['en'],gpu = False)
    #-----------------------------------Image Processing Logic --------------------------------- 
    def imgProcess(self,pic_name):
        
        output = reader.readtext(pic_name,paragraph=False)
        
        image = cv2.imread(pic_name)
        
        outputprint = ""
        out_score = 0.0
        for word in output:
          outputprint += word[-2] + " "
          out_score = word[-1]
          cord = word[0]
          x_min, y_min = [int(min(idx)) for idx in zip(*cord)]
          x_max, y_max = [int(max(idx)) for idx in zip(*cord)]
          
          cv2.rectangle(image,(x_min,y_min),(x_max,y_max),(0,0,255),2)
          processed_image = plt.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
          plt.show()
          
          # canvas = Canvas(root)
          # canvas.pack(expand = YES, fill = BOTH)
          # image1 = Image.fromarray(np.uint8( processed_image.get_cmap()(processed_image.get_array())*255))
          # im = ImageTk.PhotoImage('RGB', image1.size)
          # im.paste(image1)
          # test = canvas.create_image(0, 0, image=im)

        """Set Image on Window"""
        img = Image.open(pic_name)
        #img = Image.open(img_x)
        img = img.resize((250, 250))
        photo = ImageTk.PhotoImage(img)

        self.label2 = Label(image=photo)
        self.label2.image = photo 
        self.label2.grid(column=0, row=3)
        """END OF Set Image"""
        print("Processing ....")
        
        return outputprint,out_score
        
        
        
    


    def fileDialog(self):

        self.filename = filedialog.askopenfilename(initialdir =  "/", title = "Select A File", filetype =
        (("jpeg files","*.jpg"),("all files","*.*")) )
        self.label = ttk.Label(self.labelFrame, text = "")
        self.label.grid(column = 1, row = 2)
        self.label.configure(text = self.filename)

        
        self.imgProcess(self.filename)
      
    def stackHDRs(self,image_files):
            focusimages = []
            for img in image_files:
                print ("Reading in file {}".format(img))
                focusimages.append(cv2.imread("Input/{}".format(img)))
        
            merged = FocusStack.focus_stack(focusimages)
            cv2.imwrite("merged.jpg", merged)
            
            scores = []
            scores.append(self.imgProcess(os.getcwd()+"\\merged.jpg"))
            scores.sort(key = lambda x: x[1]) #Sorting Tuple Based on Int Value
            print(scores[-1])
            
            #Setting Text
            global final_out_pretext
            final_out_pretext = scores[-1][0]
            global final_out_percentage
            final_out_percentage = round(scores[-1][1]*100,2)
            global final_out_text
            final_out_text  = final_out_pretext + "  -  " +str(final_out_percentage)+"%"
            print(final_out_pretext)
            print(final_out_text)
            
            
            
            
    def stackCamera(self):
        cam = cv2.VideoCapture(0,cv2.CAP_DSHOW)
        cv2.namedWindow("Mean Capture")
        focus=20
        cam.set(cv2.CAP_PROP_AUTOFOCUS, focus)
        
        
        while True:
            ret, frame = cam.read()
            if not ret:
                print("failed to grab frame")
                break
            cv2.imshow("Mean Capture", frame)
            key = cv2.waitKey(20)
            if key%256 == 27:
                # ESC pressed
                print("Escape hit, closing...")
                break
            if key%256 == 32:
                # SPACE pressed
                
                img_counter = 0
                for i in range(0,5):
                    
                    ret, frame = cam.read()
                    if not ret:
                        print("failed to grab frame")
                        break
                    img_name = "photo{}.png".format(img_counter)
                    f_name = os.getcwd()+"\\Input\\"+img_name
                    cv2.imwrite(f_name, frame)
                    #print("{} written!".format(img_name))
                    print("Step {} Done !".format(img_counter))
                    time.sleep(1)
                    img_counter += 1
                print("Please Wait.....  Do NOT close any window")
                #path, dirs, files = next(os.walk("/image_in"))
                cv2.destroyAllWindows()

                image_files = sorted(os.listdir("Input"))
                for img in image_files:
                    if img.split(".")[-1].lower() not in ["jpg", "jpeg", "png"]:
                        image_files.remove(img)
            
            
                self.stackHDRs(image_files)
                
                self.label3 = ttk.Label(text = "")
                self.label3.configure(text=final_out_text)
                self.label3.grid(column=0,row=5)               
                print ("End")
        
        """
            Focus stack driver program
            This program looks for a series of files of type .jpg, .jpeg, or .png
            in a subdirectory "input" and then merges them together using the
            FocusStack module.  The output is put in the file merged.png
            Author:     Charles McGuinness (charles@mcguinness.us)
            Copyright:  Copyright 2015 Charles McGuinness
            License:    Apache License 2.0
        """
    
        
    
    def meanMaxCamera(self):
        cam = cv2.VideoCapture(0,cv2.CAP_DSHOW)
        cv2.namedWindow("Mean Capture")
        focus=20
        cam.set(cv2.CAP_PROP_AUTOFOCUS, focus)
        
        
        while True:
            ret, frame = cam.read()
            if not ret:
                print("failed to grab frame")
                break
            cv2.imshow("Mean Capture", frame)
            key = cv2.waitKey(20)
            if key%256 == 27:
                # ESC pressed
                print("Escape hit, closing...")
                break
            if key%256 == 32:
                # SPACE pressed
                
                img_counter = 0
                for i in range(0,5):
                    
                    ret, frame = cam.read()
                    if not ret:
                        print("failed to grab frame")
                        break
                    img_name = "photo{}.png".format(img_counter)
                    f_name = os.getcwd()+"\\image_in\\"+img_name
                    cv2.imwrite(f_name, frame)
                    #print("{} written!".format(img_name))
                    print("Step {} Done !".format(img_counter))
                    time.sleep(1)
                    img_counter += 1
                print("Please Wait.....  Do NOT close any window")
                #path, dirs, files = next(os.walk("/image_in"))
                cv2.destroyAllWindows()
                list1 = os.listdir(os.getcwd()+"\\image_in\\") # dir is your directory path
                number_files = len(list1)
                scores = []
                for i in list1:
                    scores.append(self.imgProcess(os.getcwd()+"\\image_in\\"+i))
                scores.sort(key = lambda x: x[1]) #Sorting Tuple Based on Int Value
                print(scores[-1])
                
                #Setting Text
                final_out_pretext = scores[-1][0]
                final_out_percentage = round(scores[-1][1]*100,2)
                final_out_text  = final_out_pretext + "  -  " +str(final_out_percentage)+"%"
                print(final_out_pretext)
                print(final_out_text)
                
                self.label3 = ttk.Label(text = "")
                self.label3.configure(text=final_out_text)
                self.label3.grid(column=0,row=5)
                break
                    
                

                    
        cam.release()
        cv2.destroyAllWindows()
          
    
        
    def loadCamera(self):
              
        cam = cv2.VideoCapture(0,cv2.CAP_DSHOW)
        cv2.namedWindow("Image Capture")
        #cam.set(cv2.CAP_PROP_AUTOFOCUS, 1)
        focus = 20
        cam.set(cv2.CAP_PROP_AUTOFOCUS, focus)
        img_counter = 0
        
        while True:
            ret, frame = cam.read()
            if not ret:
                print("failed to grab frame")
                break
            cv2.imshow("Image Capture", frame)
        
            k = cv2.waitKey(1)
            
            if k%256 == 27:
                # ESC pressed
                print("Escape hit, closing...")
                break
            if k%256 == 32:
                # SPACE pressed
                cv2.destroyAllWindows()
               
                img_name = "photo{}.png".format(img_counter)
                cv2.imwrite(img_name, frame)
                print("{} written!".format(img_name))
                print("Please Wait.....  Do NOT close any window")
                img_counter += 1
                f_name = os.getcwd()+"\\photo0.png"
                scores = []
                scores.append(self.imgProcess(f_name))
                scores.sort(key = lambda x: x[1]) #Sorting Tuple Based on Int Value
                print(scores[-1])
                
                #Setting Text
                final_out_pretext = scores[-1][0]
                final_out_percentage = round(scores[-1][1]*100,2)
                final_out_text  = final_out_pretext + "  -  " +str(final_out_percentage)+"%"
                print(final_out_pretext)
                print(final_out_text)
                
                self.label3 = ttk.Label(text = "")
                self.label3.configure(text=final_out_text)
                self.label3.grid(column=0,row=5)
                break
            
            
        cam.release()
        cv2.destroyAllWindows()
    
        
        
 

root = Root()

root.mainloop()

