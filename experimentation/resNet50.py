# -*- coding: utf-8 -*-
"""ResNet50.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1V4KzbXJmeK761XfjE-1Pni0FFikfhoAh
"""

import matplotlib.pyplot as plt
import numpy as np
import os
import PIL
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.layers import Dense, Flatten
from tensorflow.keras.models import Sequential
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping, ReduceLROnPlateau

import pathlib

# Downloading and extracting the dataset
dataset_url = https://storage.googleapis.com/download.tensorflow.org/example_images/flower_photos.tgz
data_dir = tf.keras.utils.get_file('flower_photos', origin=dataset_url, untar=True)
data_dir = pathlib.Path(data_dir)  # Converts the dataset path to a pathlib object
print(data_dir)

# Showing the paths of the images
roses = list(data_dir.glob('roses/*'))  # Lists all files in the 'roses' directory
print(roses[5])  # Prints the path of the 5th rose image
PIL.Image.open(str(roses[0]))  # Opens and displays the first rose image

# Defining the image parameters and size
img_height, img_width = 180, 180
batch_size = 32

# Making the training data set
train_ds = tf.keras.preprocessing.image_dataset_from_directory(
  data_dir,
  validation_split=0.2, # 20% of the data for validation, so 80% for training. CAN BE CHANGED
  subset="training",
  seed=123,
  image_size=(img_height, img_width),
  batch_size=batch_size)

# Making the validation data set + naming
val_ds = tf.keras.preprocessing.image_dataset_from_directory(
  data_dir,
  validation_split=0.2, # 20% of the data for validation
  subset="validation",
  seed=123,
  image_size=(img_height, img_width),
  batch_size=batch_size)

# Getting the class names for the training data sets
class_names = train_ds.class_names
print(class_names)

plt.figure(figsize=(10, 10))
# Printing samples of data for training by looping through them
for images, labels in train_ds.take(1):
  for i in range(6):
    ax = plt.subplot(3, 3, i + 1)
    plt.imshow(images[i].numpy().astype("uint8"))
    plt.title(class_names[labels[i]])
    plt.axis("off")

# Easiest way to stack layers on one another on the data
resnet_model = Sequential()

# Loading the pre-trained ResNet50 model without the top classification layer because we
# do not want to have 1000 classes. Later on we specify we only want 5 classes. SO include_top = FALSE
pretrained_model = tf.keras.applications.ResNet50(include_top=False,
                   input_shape=(180, 180, 3),
                   pooling='max', weights='imagenet')

# Freezing the layers of the pre-trained model
for layer in pretrained_model.layers:
    layer.trainable = False

resnet_model.add(pretrained_model)  # Adding the pre-trained ResNet50 model to Sequential model
# Converting the 2D array to a 1D vector so that it can go to the next Dense layer
resnet_model.add(Flatten())  # Flattening the output of the pre-trained model to feed into the dense layers

# Adding a fully connected (Dense) layer with 512 neurons and ReLU activation function
# 512 neurons mean that this layer will have 512 nodes or units.
# The ReLU activation function helps the model to learn patterns by introducing non-linearity.
resnet_model.add(Dense(512, activation='relu'))
# Adding the output layer with 5 neurons (one for each class) and softmax activation function
# The softmax activation function ensures that the output is a probability distribution over the 5 classes.
resnet_model.add(Dense(len(class_names), activation='softmax'))
resnet_model.summary()

# Compiling the model and getting the necessary data for predictions
resnet_model.compile(optimizer=Adam(learning_rate=0.001), loss='sparse_categorical_crossentropy', metrics=['accuracy'])

# Define callbacks
checkpoint_cb = ModelCheckpoint("best_model.keras", save_best_only=True, save_format="tf")
early_stopping_cb = EarlyStopping(patience=10, restore_best_weights=True)
reduce_lr = ReduceLROnPlateau(monitor='val_loss', factor=0.1, patience=5, min_lr=0.00001)

# Training it using 10 epochs.
epochs = 10
history = resnet_model.fit(
  train_ds,
  validation_data=val_ds,
  epochs=epochs,
  callbacks=[checkpoint_cb, early_stopping_cb, reduce_lr]
)

# Print history keys to debug
print(history.history.keys())

# Making the first graph for accuracy
plt.figure()
plt.plot(history.history['accuracy'], label='Training Accuracy')
plt.plot(history.history['val_accuracy'], label='Validation Accuracy')
plt.axis(ymin=0.4, ymax=1)
plt.grid()
plt.title('Model Accuracy')
plt.ylabel('Accuracy')
plt.xlabel('Epochs')
plt.legend(loc='upper left')
plt.show()

# Making second graph for loss
plt.figure()
plt.plot(history.history['loss'], label='Training Loss')
plt.plot(history.history['val_loss'], label='Validation Loss')
plt.grid()
plt.title('Model Loss')
plt.ylabel('Loss')
plt.xlabel('Epochs')
plt.legend(loc='upper left')
plt.show()

# After training the model, we see if it works by predicting
import cv2
for i, image_path in enumerate(roses):  # For loop through all images and paths in roses class
    image = cv2.imread(str(image_path))  # Reading the image using OpenCV
    image_resized = cv2.resize(image, (img_height, img_width))  # Resizing to fit model
    image = np.expand_dims(image_resized, axis=0)  # Adding an extra dimension to fit the input
    print(f"Shape of image {i}: {image.shape}")

    # Make prediction
    pred = resnet_model.predict(image)
    print(pred)

    # Getting the class with the highest score that matches the picture most
    # The AI will score the classes by similarity to the image, so then if the class ROSE is 0.8,
    # and the rest are <0.8 then ROSE is the output
    output_class = class_names[np.argmax(pred)]  # Returns it
    print(f"The predicted class for image {i} is {output_class}")

# Possible improvements:
# - Adding Batch Normalization can help to stabilize and speed up training using resnet_model.add(BatchNormalization())
# - Unfreezing some layers (layer.trainable = True and you can do as many layers as you want to fine tune the pre trained model)
# - Use other models like InceptionV3 or EfficientNet
# - Adding more models and then combining them by simply doing the same process but with more models and then putting them together and training.
