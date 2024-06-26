# -*- coding: utf-8 -*-
"""CV_project.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1sZb4SsQPC992o7vb0WRdZxTzuqF-BQbK
"""

import os
import glob
import sklearn
import numpy as np
import pandas as pd
import seaborn as sns
import urllib.request
import tensorflow as tf
from PIL import Image as im
from matplotlib import pyplot
from tensorflow import keras
from tensorflow.keras import layers
from sklearn.model_selection import KFold
from sklearn.metrics import accuracy_score
import matplotlib.pyplot as plt

import cv2
from sklearn.preprocessing import StandardScaler
from skimage.feature import hog
from skimage.feature import local_binary_pattern

from sklearn.model_selection import GridSearchCV
from sklearn.ensemble._forest import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.naive_bayes import GaussianNB

from google.colab.patches import cv2_imshow

quickdraw_dataset_path = "/content/drive/MyDrive/Quick_Draw"

classes = ["airplane", "ambulance", "angel", "ant", "anvil", "apple", "arm", "asparagus", "axe", "backpack", "banana", "bandage", "barn", "baseball", "basket", "basketball", "bat", "bathtub", "beach", "bear", "beard", "bed", "bee", "belt", "bench", "bicycle", "binoculars", "bird", "birthday cake", "blackberry", "blueberry", "book", "boomerang", "bottlecap", "bowtie", "bracelet", "brain", "bread", "bridge", "broccoli", "broom", "bucket", "bulldozer", "bus", "bush", "butterfly", "cactus", "cake", "calculator", "calendar", "camel", "camera", "camouflage", "campfire", "candle", "cannon", "canoe", "car", "carrot", "castle", "cat", "cello", "chair", "chandelier", "church", "circle", "clarinet", "clock", "cloud", "coffee cup", "compass", "computer", "cookie", "cooler", "couch", "cow", "crab", "crayon", "crocodile", "crown", "cup", "diamond", "dishwasher", "dog", "dolphin", "donut", "door", "dragon", "dresser", "drill", "drums", "duck", "dumbbell", "ear", "elbow", "elephant", "envelope", "eraser", "eye", "eyeglasses", "face", "fan", "feather", "fence", "finger", "fireplace", "firetruck", "fish", "flamingo", "flashlight", "flower", "foot", "fork", "frog", "garden", "giraffe", "goatee", "grapes", "grass", "guitar", "hamburger", "hammer", "hand", "harp", "hat", "headphones", "hedgehog", "helicopter", "helmet", "hexagon", "hockey stick", "horse", "hospital", "hourglass", "house", "hurricane", "jacket", "jail", "kangaroo", "key", "keyboard", "knee", "knife", "ladder", "lantern", "laptop", "leaf", "leg", "lighter", "lighthouse", "lightning", "line", "lion", "lipstick", "lobster", "lollipop", "mailbox", "map", "marker", "matches", "megaphone", "mermaid", "microphone", "microwave", "monkey", "moon", "mosquito", "motorbike", "mountain", "mouse", "moustache", "mouth", "mug", "mushroom", "nail", "necklace", "nose", "ocean", "octagon", "octopus", "onion", "oven", "owl", "paintbrush", "paint can", "palm tree", "panda", "pants", "parachute", "parrot", "passport", "peanut", "pear", "peas", "pencil", "penguin", "piano", "pig", "pillow", "pineapple", "pizza", "pliers", "pond", "pool", "popsicle", "postcard", "potato", "purse", "rabbit", "raccoon", "radio", "rain", "rainbow", "rake", "rhinoceros", "rifle", "river", "rollerskates", "sailboat", "sandwich", "saw", "saxophone", "school bus", "scissors", "scorpion", "screwdriver", "sea turtle", "shark", "sheep", "shoe", "shorts", "shovel", "sink", "skateboard", "skull", "skyscraper", "smiley face", "snail", "snake", "snorkel", "snowflake", "snowman", "sock", "speedboat", "spider", "spoon", "spreadsheet", "square", "squiggle", "squirrel", "stairs", "star", "steak", "stereo", "stethoscope", "stitches", "stove", "strawberry", "streetlight", "string bean", "submarine", "suitcase", "sun", "swan", "sweater", "swing set", "sword", "syringe", "table", "teapot", "teddy-bear", "telephone", "television", "tennis racquet", "tent", "The Eiffel Tower", "The Great Wall of China", "The Mona Lisa", "tiger", "toaster", "toe", "toilet", "tooth", "toothbrush", "toothpaste", "tornado", "tractor", "traffic light", "train", "tree", "triangle", "trombone", "truck", "trumpet", "t-shirt", "umbrella", "underwear", "van", "vase", "violin", "washing machine", "watermelon", "waterslide", "whale", "wheel", "windmill", "wine bottle", "wine glass", "wristwatch", "yoga", "zebra", "zigzag"]

url = 'https://storage.googleapis.com/quickdraw_dataset/full/numpy_bitmap/'

for class_ in classes[:100]:
	if(" " in class_):
		continue
	complete_url = url+class_+".npy"
	print("Downloading : ",complete_url)
	urllib.request.urlretrieve(complete_url, quickdraw_dataset_path +"/"+class_+".npy")

data_sets = glob.glob(os.path.join('/content/drive/MyDrive/Quick_Draw/*.npy'))
print(len(data_sets))
data_sets = data_sets[:20]

def denoise_image(image):

    # gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    denoised = cv2.medianBlur(image, 3)

    if len(image.shape) == 3:
        denoised = cv2.cvtColor(denoised, cv2.COLOR_GRAY2BGR)

    return denoised

dataset_path = '/content/drive/MyDrive/'
data_sets = glob.glob(os.path.join('/content/drive/MyDrive/Quick_Draw/*.npy'))
data_sets = data_sets[:20]
print(data_sets)
input = np.empty([0, 784])

labels = np.empty([0])
index = 0

for file in data_sets:
	data = np.load(file)
	data = data[0: 6000, :]
	input = np.concatenate((input, data), axis=0)
	labels = np.append(labels, [index]*data.shape[0])
	index += 1

n_fold = 5
kf = KFold(n_splits=n_fold, shuffle=True, random_state=9)
x_train, x_test, y_train, y_test = None, None, None, None
random_ordering = np.random.permutation(input.shape[0])
input = input[random_ordering, :]
labels = labels[random_ordering]

for train_index, test_index in kf.split(input):
    x_train, x_test = input[train_index], input[test_index]
    y_train, y_test = labels[train_index], labels[test_index]
    break

print(len(x_train))

print(len(x_test))

print(x_train.shape)

image_size = 28
x_train_reshaped = x_train.reshape(x_train.shape[0], image_size, image_size)
x_test_reshaped = x_test.reshape(x_test.shape[0], image_size, image_size)

for i in range(16):
  plt.grid(False)
  plt.imshow(x_train_reshaped[i], cmap=plt.cm.binary)
  plt.show()

print(x_train_reshaped[0].shape)

len(x_train_reshaped[34])

denoised_x_train=[]
for img in x_train_reshaped:
  cv2.imwrite('color_img.jpg', img)
  x=cv2.imread("color_img.jpg", cv2.IMREAD_GRAYSCALE)
  x=denoise_image(x)
  denoised_x_train.append(x)


denoised_x_train=np.array(denoised_x_train)
denoised_x_train=denoised_x_train.reshape(-1,784)

denoised_x_test=[]
for img in x_test_reshaped:
  cv2.imwrite('color_img.jpg', img)
  x=cv2.imread("color_img.jpg", cv2.IMREAD_GRAYSCALE)
  x=denoise_image(x)
  denoised_x_test.append(x)


denoised_x_test=np.array(denoised_x_test)
denoised_x_test=denoised_x_test.reshape(-1,784)

def enhance_contrast(image):
    equalized = cv2.equalizeHist(image)

    return equalized

contrast_x_train=[]
for img in x_train_reshaped:
  cv2.imwrite('color_img.jpg', img)
  x=cv2.imread("color_img.jpg", cv2.IMREAD_GRAYSCALE)
  x=enhance_contrast(x)
  contrast_x_train.append(x)
contrast_x_train=np.array(contrast_x_train)
contrast_x_train=contrast_x_train.reshape(-1,784)

contrast_x_test=[]
for img in x_test_reshaped:
  cv2.imwrite('color_img.jpg', img)
  x=cv2.imread("color_img.jpg", cv2.IMREAD_GRAYSCALE)
  x=denoise_image(x)
  contrast_x_test.append(x)


contrast_x_test=np.array(contrast_x_test)
contrast_x_test=contrast_x_test.reshape(-1,784)

def apply_filter(image, filter_type, kernel_size):

    if filter_type == 'gaussian':
        kernel = cv2.getGaussianKernel(kernel_size, 0)
        kernel = np.outer(kernel, kernel.transpose())
    elif filter_type == 'sobel_x':
        kernel = np.array([[-1, 0, 1],
                           [-2, 0, 2],
                           [-1, 0, 1]])
    elif filter_type == 'sobel_y':
        kernel = np.array([[-1, -2, -1],
                           [0, 0, 0],
                           [1, 2, 1]])
    elif filter_type == 'laplacian':
        kernel = np.array([[0, 1, 0],
                           [1, -4, 1],
                           [0, 1, 0]])
    else:
        raise ValueError('Invalid filter type')

    filtered = cv2.filter2D(image, -1, kernel)

    return filtered

filter_x_train=[]
for img in x_train_reshaped:
  cv2.imwrite('color_img.jpg', img)
  x=cv2.imread("color_img.jpg", cv2.IMREAD_GRAYSCALE)
  x=apply_filter(x,'gaussian', 3)
  filter_x_train.append(x)
filter_x_train=np.array(filter_x_train)
filter_x_train=filter_x_train.reshape(-1,784)

filter_x_test=[]
for img in x_test_reshaped:
  cv2.imwrite('color_img.jpg', img)
  x=cv2.imread("color_img.jpg", cv2.IMREAD_GRAYSCALE)
  x=denoise_image(x)
  filter_x_test.append(x)


filter_x_test=np.array(filter_x_test)
filter_x_test=filter_x_test.reshape(-1,784)

def apply_clahe(image, clip_limit=2.0, tile_size=(8, 8)):

    clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_size)
    enhanced = clahe.apply(image)

    return enhanced

clahe_x_train=[]
for img in x_train_reshaped:
  cv2.imwrite('color_img.jpg', img)
  x=cv2.imread("color_img.jpg", cv2.IMREAD_GRAYSCALE)
  x=apply_clahe(x)
  clahe_x_train.append(x)
clahe_x_train=np.array(clahe_x_train)
clahe_x_train=clahe_x_train.reshape(-1,784)

clahe_x_test=[]
for img in x_test_reshaped:
  cv2.imwrite('color_img.jpg', img)
  x=cv2.imread("color_img.jpg", cv2.IMREAD_GRAYSCALE)
  x=denoise_image(x)
  clahe_x_test.append(x)


clahe_x_test=np.array(clahe_x_test)
clahe_x_test=clahe_x_test.reshape(-1,784)

def smooth_and_sharpen(image):
    blurred = cv2.GaussianBlur(image, (5,5), 0)
    laplacian = cv2.Laplacian(blurred, cv2.CV_8U, ksize=3)

    sharpened = cv2.addWeighted(image, 1.5, laplacian, -0.5, 0)

    return sharpened

sharp_x_train=[]
for img in x_train_reshaped:
  cv2.imwrite('color_img.jpg', img)
  x=cv2.imread("color_img.jpg", cv2.IMREAD_GRAYSCALE)
  x=apply_clahe(x)
  sharp_x_train.append(x)
sharp_x_train=np.array(sharp_x_train)
sharp_x_train=sharp_x_train.reshape(-1,784)

sharp_x_test=[]
for img in x_test_reshaped:
  cv2.imwrite('color_img.jpg', img)
  x=cv2.imread("color_img.jpg", cv2.IMREAD_GRAYSCALE)
  x=denoise_image(x)
  sharp_x_test.append(x)


sharp_x_test=np.array(sharp_x_test)
sharp_x_test=sharp_x_test.reshape(-1,784)

features ={}

def horizontal_projection(im):
  img = 255 - im
  proj = np.sum(img,1)
  m = np.max(proj)
  w = 28
  result = np.zeros((proj.shape[0],28))
  for row in range(img.shape[0]):
   cv2.line(result, (0,row), (int(proj[row]*w/m),row), (255,255,255), 1)
  return result

features["Horizontal Projection"]=horizontal_projection(x_train_reshaped[0])

hp_x_train=[]
for img in x_train_reshaped:
  x=horizontal_projection(img)
  hp_x_train.append(x)
hp_x_train=np.array(hp_x_train)
hp_x_train=hp_x_train.reshape(-1,784)

def detect_shapes(img):
    # Check if the image is uint8
    if img.dtype != np.uint8:
      # Convert the image to uint8
      img = img.astype(np.uint8)

    # Apply the Canny edge detector
    edges = cv2.Canny(img, 100, 200)
    img = cv2.resize(img, (28, 28))

    if len(img.shape) == 3:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    else:
        gray = img
    edges = cv2.Canny(img, 100, 200)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    features = []

    for contour in contours:

        area = cv2.contourArea(contour)
        if area < 5:
            continue


        perimeter = cv2.arcLength(contour, True)

        circularity = 4 * 3.14 * (area / (perimeter * perimeter))
        features.append(circularity)

    return features

features["Shape Detection"]=detect_shapes(x_train_reshaped[0])

import cv2
import numpy as np

def extract_corners(image):
    # Check and convert the image to the correct type if necessary
    if image.dtype != np.uint8 and image.dtype != np.float32:
        gray = image.astype(np.float32)  # Convert to float32 if not already an 8-bit or 32-bit float image
    else:
        gray = image

    max_corners = 100
    quality_level = 0.3
    min_distance = 7
    block_size = 7

    corners = cv2.goodFeaturesToTrack(gray, max_corners, quality_level, min_distance, blockSize=block_size)
    if corners is not None:
        corners = np.int0(corners)
        for i in corners:
            x, y = i.ravel()
            cv2.circle(gray, (x, y), 3, 255, -1)

    return gray

# Use the function with your image
features["Corner Detection"] = extract_corners(x_train_reshaped[0])

import cv2
import numpy as np

def detect_edges(image):
    # Ensure the image is in 8-bit unsigned format
    if image.dtype != np.uint8:
        gray = np.uint8(image * 255)  # Normalize and convert if needed
    else:
        gray = image

    # Apply Gaussian blur to the grayscale image
    blurred = cv2.GaussianBlur(gray, (3, 3), 0)

    # Detect edges using the Canny algorithm
    edges = cv2.Canny(blurred, threshold1=30, threshold2=100)

    return edges

# Use the function with your grayscale image
features["Edge Detection"] = detect_edges(x_train_reshaped[0])

def create_lbp(image):

    # gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray=image

    radius = 1
    num_neighbors = 8
    lbp = np.zeros_like(gray)
    for i in range(radius, gray.shape[0]-radius):
        for j in range(radius, gray.shape[1]-radius):
            center = gray[i,j]
            code = 0
            for k in range(num_neighbors):
                angle = k * (2*np.pi/num_neighbors)
                x = int(np.round(i + radius * np.cos(angle)))
                y = int(np.round(j - radius * np.sin(angle)))
                neighbor = gray[x,y]
                if neighbor > center:
                    code += 2**k
            lbp[i,j] = code
    lbp = cv2.normalize(lbp, None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8U)

    return lbp

features["LBP"]=create_lbp(x_train_reshaped[0])

##Data Augmentation

def rotate_image(image, angle):
    # Get the dimensions of the input image
    height, width = image.shape[:2]

    # Calculate the rotation matrix using the specified angle
    rotation_matrix = cv2.getRotationMatrix2D((width/2, height/2), angle, 1)

    # Apply the rotation matrix to the input image using cv2.warpAffine()
    rotated_image = cv2.warpAffine(image, rotation_matrix, (width, height))

    return rotated_image
rotated_x_train=[]
for img in x_train_reshaped:
  x=rotate_image(img,5)
  rotated_x_train.append(x)
rotated_x_train=np.array(rotated_x_train)
rotated_x_train=rotated_x_train.reshape(-1,784)

def horizontal_flip(image):
    # Flip the input image horizontally using cv2.flip()
    flipped_image = cv2.flip(image, 1)

    return flipped_image
flip_x_train=[]
for img in x_train_reshaped:
  x=horizontal_flip(img)
  flip_x_train.append(x)
flip_x_train=np.array(flip_x_train)
flip_x_train=flip_x_train.reshape(-1,784)

from skimage import data, segmentation, color
from skimage.future import graph
from matplotlib import pyplot as plt
from PIL import Image
import networkx as nx
from skimage import io
def vec(img):
  labels1 = segmentation.slic(img, compactness=5, n_segments=50000,
                          start_label=1)
  out1 = color.label2rgb(labels1, img, kind='avg', bg_label=0)
  out1 = Image.fromarray(out1, 'RGB')
  return out1

vec_x_train=[]
i=0
for img in x_train_reshaped[:100]:
  # if(i%1000==0):
  #   print(i)
  # i=i+1
  x=vec(img)
  vec_x_train.append(x)
vec_x_train=np.array(vec_x_train)

"""Classification

KNN
"""

dic={}
dic1={}
dic2={}
enchanced={}
dic_hp={}

def KNN(x_train_1d, y_train, x_test_1d,y_test):

  tuning_parameters = {'n_neighbors': [1,3,5,7,9,11]}

  knn = KNeighborsClassifier(n_neighbors = 5, n_jobs=-1)
  knn.fit(x_train_1d, y_train)


  y_pred = knn.predict(x_test_1d)
  y_pred[:10]

  accuracy = accuracy_score(y_test, y_pred)
  print(accuracy)
  return accuracy

dic['KNN']=KNN(x_train,y_train,x_test,y_test)

dic1['KNN']=KNN(flip_x_train,y_train,x_test,y_test)

dic2['KNN']=KNN(rotated_x_train,y_train,x_test,y_test)

#Logistic Regression
def LogisticReg(x_train_1d, y_train, x_test_1d,y_test):
  clf = LogisticRegression(random_state=0)
  # knn = GridSearchCV(clf_knn, tuning_parameters, n_jobs=-1)
  clf.fit(x_train_1d, y_train)

  y_pred = clf.predict(x_test_1d)
  y_pred[:10]
  accuracy = accuracy_score(y_test, y_pred)
  print(accuracy)
  return accuracy

dic['Logistic Regression']=LogisticReg(x_train,y_train,x_test,y_test)

dic1['Logistic Regression']=LogisticReg(flip_x_train,y_train,x_test,y_test)

dic2['Logistic Regression']=LogisticReg(rotated_x_train,y_train,x_test,y_test)

#Naive Bayes
def NaiveBayes(x_train_1d, y_train, x_test_1d,y_test):
  clf = GaussianNB()
  # knn = GridSearchCV(clf_knn, tuning_parameters, n_jobs=-1)
  clf.fit(x_train_1d, y_train)

  y_pred = clf.predict(x_test_1d)
  y_pred[:10]

  accuracy = accuracy_score(y_test, y_pred)
  print(accuracy)
  return accuracy
dic['Naive Bayes']=NaiveBayes(x_train,y_train,x_test,y_test)

dic1['Naive Bayes']=NaiveBayes(flip_x_train,y_train,x_test,y_test)

dic2['Naive Bayes']=NaiveBayes(rotated_x_train,y_train,x_test,y_test)

#Random Forest
def RandomForest(x_train_1d, y_train, x_test_1d,y_test):

  parameters = {'n_estimators': [100,120,140,160]}

  clf_rf = RandomForestClassifier(n_estimators = 150, n_jobs=-1, random_state=0)
  # model = GridSearchCV(clf_rf, parameters, n_jobs=-1)
  clf_rf.fit(x_train_1d, y_train)



  y_pred = clf_rf.predict(x_test_1d)
  y_pred[:10]

  accuracy = accuracy_score(y_test, y_pred)
  print(accuracy)
  return accuracy

dic['Random Forest']=RandomForest(x_train,y_train,x_test,y_test)

dic1['Random Forest']=RandomForest(flip_x_train,y_train,x_test,y_test)

dic2['Random Forest']=RandomForest(rotated_x_train,y_train,x_test,y_test)

enchanced['Denoised']=RandomForest(denoised_x_train,y_train,denoised_x_test,y_test)

enchanced['Contrast']=RandomForest(contrast_x_train,y_train,contrast_x_test,y_test)

enchanced['Filter']=RandomForest(filter_x_train,y_train,filter_x_test,y_test)

enchanced['clahe']=RandomForest(clahe_x_train,y_train,clahe_x_test,y_test)

enchanced['sharp']=RandomForest(sharp_x_train,y_train,sharp_x_test,y_test)

plt.bar(range(len(enchanced)), list(enchanced.values()), align='center')
plt.xticks(range(len(enchanced)), list(enchanced.keys()))
plt.show()

plt.bar(range(len(dic)), list(dic.values()), align='center')
plt.xticks(range(len(dic)), list(dic.keys()))
plt.show()

plt.bar(range(len(dic1)), list(dic1.values()), align='center')
plt.xticks(range(len(dic1)), list(dic1.keys()))
plt.show()

plt.bar(range(len(dic2)), list(dic2.values()), align='center')
plt.xticks(range(len(dic2)), list(dic2.keys()))
plt.show()

dicf={}
dicv={}

plt.bar(range(len(features)), list(features.values()), align='center')
plt.xticks(range(len(features)), list(features.keys()))
plt.show()

plt.plot(range(len(dicf)), list(dicf.values()))
plt.plot(range(len(dic)), list(dic.values()))
plt.plot(range(len(dic1)), list(dic1.values()))
plt.plot(range(len(dic2)), list(dic2.values()))
plt.xticks(range(len(dic2)), list(dic2.keys()))
plt.legend(["Feature extracted", "Without image processing","Flipped","Rotated"])
plt.show()

plt.plot(range(len(dic)), list(dic.values()))
plt.plot(range(len(dicv)), list(dicv.values()))
plt.xticks(range(len(dic2)), list(dic2.keys()))
plt.legend(["Original","After vectorization"])
plt.show()

!pip install anvil-uplink

import anvil.server
anvil.server.connect("server_AUOSXS2C7WZHVBN2EYGNCP4G-EWCEHDZDUEIAGFYC")
def predict(ing):
  return ans
anvil.server.wait_forever()

