# -*- coding: utf-8 -*-
"""train_dense.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/11eX2mHHn8nhqcwQPEPrI8c1HsdKSIesO
"""
import tensorflow as tf
import pickle

def scheduler(epoch, lr):
  if (epoch!=0 and epoch%30==0):
    return lr*0.5
  else:
    return lr

def train(train_dataset,model,name,
          steps_per_epoch,
           validation_data,
           validation_steps, checkpoint_filepath, epoch,opt
          ):


#history file neme for each model
  if name == "densenet":
    file_name = 'densenet.pkl'
  elif name == "covidnet":
    file_name = 'covidnet.pkl'
  else:
    file_name = 'attenresnet.pkl'
#--------------------------------------------------

  
  model1 = model
  
#----------------------------COMPILE------------------------------------------------------
  model1.compile(optimizer=opt, loss = 'categorical_crossentropy', metrics=['accuracy'])
#-----------------------------------------------------------------------------------------

#-----------------------------CALLBACKS-----------------------------------------------------
  
  earlystoping_callbacks = tf.keras.callbacks.EarlyStopping(
    monitor='val_accuracy',
    min_delta=0,
    patience=30,
    mode='max')
  
  model_checkpoint_callback = tf.keras.callbacks.ModelCheckpoint(
    filepath=checkpoint_filepath,
    save_weights_only=True,
    monitor='val_accuracy',
    mode='max',
    save_best_only=True)  
  
  lr_callback = tf.keras.callbacks.LearningRateScheduler(scheduler)

#-----------------------------------------------------------------------------------------------------

#--------------------------------------FIT THE MODEL---------------------------------------------

  history_network = model1.fit(train_dataset , epochs = epoch, 
           steps_per_epoch = steps_per_epoch,
           validation_data = validation_data,
           validation_steps = validation_steps,
           callbacks = [earlystoping_callbacks, lr_callback, model_checkpoint_callback]
           )


  # save dictionary to a pkl file
  with open(file_name, 'wb') as file_hist:
      pickle.dump(history_network.history, file_hist)
  
  return history_network ,model1
