# -*- coding: utf-8 -*-
"""atten_resnet.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1F5RLhl-KZHrgxmEBVEcZJEUB5O8FQQVC
"""

import tensorflow as tf
from tensorflow.keras.layers import Input, Conv2D, Lambda, MaxPool2D, UpSampling2D, AveragePooling2D
from tensorflow.keras.layers  import Activation, Flatten, Dense, Add, Multiply, BatchNormalization, Dropout

from tensorflow.keras.models import Model



#---------------------------------------------------------------- #residual unit --------------------------------------------------------
#----------------------------------------------------------------------------------------------------------------------------------------
def residual_unit(residual_input_data, filters, stride=1):
  # Hold input_x here for later processing
  identity_x = residual_input_data
        
  filter1,filter2,filter3 = filters
        
  # Layer 1
  batch_norm_op_1 = BatchNormalization()(residual_input_data)
  activation_op_1 = Activation('relu')(batch_norm_op_1)
  conv_op_1 = Conv2D(filters=filter1,kernel_size=1, strides=1,padding='same')(activation_op_1)
        
  # Layer 2
  batch_norm_op_2 = BatchNormalization()(conv_op_1)
  activation_op_2 = Activation('relu')(batch_norm_op_2)
  conv_op_2 = Conv2D(filters=filter2,kernel_size=3, strides=stride,padding='same')(activation_op_2)
    
  # Layer 3
  batch_norm_op_3 = BatchNormalization()(conv_op_2)
  activation_op_3 = Activation('relu')(batch_norm_op_3)
  conv_op_3 = Conv2D(filters=filter3,kernel_size=1, strides=1,padding='same')(activation_op_3)
        
  # Element-wise Addition
  if identity_x.shape[-1] != conv_op_3.shape[-1]:
    filter_n = conv_op_3.shape[-1]
    identity_x = Conv2D(filters=filter_n,kernel_size=1, strides=stride,padding='same')(identity_x)
            
  output = Add()([identity_x, conv_op_3])

  return output



#----------------------------------------------------------- Trunk branch --------------------------------------------
#---------------------------------------------------------------------------------------------------------------------
def trunk_branch(trunk_input_data, filters):
        # sequence of residual units, default=2
        t_res_unit_op = trunk_input_data
        
        t_res_unit_op = residual_unit(t_res_unit_op, filters=filters)
        t_res_unit_op = residual_unit(t_res_unit_op, filters=filters)

        return t_res_unit_op

#------------------------------------------------------------- Mask branches-------------------------------------------
#--------------------------------------------------------------------------------------------------------------------
def mask_branch_1(mask_input_data, filters):
      
            # Downsampling Step Initialization - Top
            downsampling_1 = MaxPool2D(pool_size=3, strides=2, padding='same')(mask_input_data)
            # Perform residual units ops 
            output_res_1 = residual_unit(residual_input_data=downsampling_1, filters=filters)
            #get an output for a skip connection
            output_1 = residual_unit(residual_input_data=output_res_1, filters=filters)

            # Last pooling step before middle step - Bottom
            downsampling_2 = MaxPool2D(pool_size=3, strides=2, padding='same')(output_res_1)
            
            output_res_2 = residual_unit(residual_input_data=downsampling_2, filters=filters)
            
            #get an output for a skip connection
            output_2 = residual_unit(residual_input_data=output_res_2, filters=filters)

            downsampling_3 = MaxPool2D(pool_size=3, strides=2, padding='same')(output_res_2)

            mid = residual_unit(residual_input_data=downsampling_3, filters=filters)
            output_res_3 = residual_unit(residual_input_data=mid, filters=filters)

            # Upsampling Step Initialization - Top
            upsampling_1 = UpSampling2D(size=2,interpolation='bilinear')(output_res_3)
            connection_output_1 = Add()([upsampling_1, output_2])

            output_res_4 = residual_unit(residual_input_data=connection_output_1, filters=filters)

            upsampling_2 = UpSampling2D(size=2,interpolation='bilinear')(output_res_4)
            connection_output_2 = Add()([upsampling_2, output_1])

            output_res_5 = residual_unit(residual_input_data=connection_output_2, filters=filters)

            upsampling_3 = UpSampling2D(size=2,interpolation='bilinear')(output_res_5)
            conv_filter = upsampling_3.shape[-1]
        
            conv1 = Conv2D(filters=conv_filter, kernel_size=1, strides=1,padding='same')(upsampling_3)
        
            conv2 = Conv2D(filters=conv_filter, kernel_size=1, strides=1,padding='same')(conv1)

            sigmoid = Activation('sigmoid')(conv2)

            return sigmoid
            


def mask_branch_2(mask_input_data, filters):

            # Downsampling Step Initialization - Top
            downsampling_1 = MaxPool2D(pool_size=3, strides=2,padding='same')(mask_input_data)
            # Perform residual units ops 
            output_res_1 = residual_unit(residual_input_data=downsampling_1, filters=filters)
            #get an output for a skip connection
            output_1 = residual_unit(residual_input_data=output_res_1, filters=filters)

            # Last pooling step before middle step - Bottom
            downsampling_2 = MaxPool2D(pool_size=3, strides=2,padding='same')(output_res_1)
            
            mid = residual_unit(residual_input_data=downsampling_2, filters=filters)
            output_res_2 = residual_unit(residual_input_data=mid, filters=filters)

            # Upsampling Step Initialization - Top
            upsampling_1 = UpSampling2D(size=2,interpolation='bilinear')(output_res_2)
            connection_output_1 = Add()([upsampling_1, output_1])

            output_res_3 = residual_unit(residual_input_data=connection_output_1, filters=filters)

            upsampling_2 = UpSampling2D(size=2,interpolation='bilinear')(output_res_3)
            conv_filter = upsampling_2.shape[-1]
        
            conv1 = Conv2D(filters=conv_filter, kernel_size=1, strides=1,padding='same')(upsampling_2)
        
            conv2 = Conv2D(filters=conv_filter, kernel_size=1, strides=1,padding='same')(conv1)

            sigmoid = Activation('sigmoid')(conv2)

            return sigmoid

            
def mask_branch_3(mask_input_data, filters):
            # Downsampling Step Initialization - Top
            downsampling_1 = MaxPool2D(pool_size=3, strides=2,padding='same')(mask_input_data)
            
            mid = residual_unit(residual_input_data=downsampling_1, filters=filters)
            output_res_1 = residual_unit(residual_input_data=mid, filters=filters)

            # Upsampling Step Initialization - Top
            upsampling_1 = UpSampling2D(size=2,interpolation='bilinear')(output_res_1)
        
            conv_filter = upsampling_1.shape[-1]
        
            conv1 = Conv2D(filters=conv_filter, kernel_size=1, strides=1,padding='same')(upsampling_1)
        
            conv2 = Conv2D(filters=conv_filter, kernel_size=1, strides=1,padding='same')(conv1)

            sigmoid = Activation('sigmoid')(conv2)

            return sigmoid

#----------------------------------------------------------attention residual --------------------------------------------
#--------------------------------------------------------------------------------------------------------------
def attention_residual_learning(mask_input, trunk_input):
        Mx = Lambda(lambda x: 1 + x)(mask_input) # 1 + mask
        prod = Multiply()([Mx, trunk_input]) # M(x) * T(x)
        return prod



#---------------------------------------------------------------- #attention modules --------------------------------
#--------------------------------------------------------------------------------------------------------------------

def attention_module_1(attention_input_data, filters):
        # Send input_x through #p residual_units
        p_res_unit_op_1 = attention_input_data
        
        p_res_unit_op_1 = residual_unit(p_res_unit_op_1, filters=filters)

        # Perform Trunk Branch Operation
        trunk_branch_op = trunk_branch(trunk_input_data=p_res_unit_op_1, filters=filters)

        # Perform Mask Branch Operation
        mask_branch_op = mask_branch_1(mask_input_data=p_res_unit_op_1, filters=filters)

        # Perform Attention Residual Learning: Combine Trunk and Mask branch results
        ar_learning_op = attention_residual_learning(mask_input=mask_branch_op, trunk_input=trunk_branch_op)

        # Send branch results through #p residual_units
        p_res_unit_op_2 = ar_learning_op
        
        p_res_unit_op_2 = residual_unit(p_res_unit_op_2, filters=filters)

        return p_res_unit_op_2

def attention_module_2(attention_input_data, filters):
        # Send input_x through #p residual_units
        p_res_unit_op_1 = attention_input_data
        
        p_res_unit_op_1 = residual_unit(p_res_unit_op_1, filters=filters)

        # Perform Trunk Branch Operation
        trunk_branch_op = trunk_branch(trunk_input_data=p_res_unit_op_1, filters=filters)

        # Perform Mask Branch Operation
        mask_branch_op = mask_branch_2(mask_input_data=p_res_unit_op_1, filters=filters)

        # Perform Attention Residual Learning: Combine Trunk and Mask branch results
        ar_learning_op = attention_residual_learning(mask_input=mask_branch_op, trunk_input=trunk_branch_op)

        # Send branch results through #p residual_units
        p_res_unit_op_2 = ar_learning_op
        
        p_res_unit_op_2 = residual_unit(p_res_unit_op_2, filters=filters)

        return p_res_unit_op_2

def attention_module_3(attention_input_data, filters):
        # Send input_x through #p residual_units
        p_res_unit_op_1 = attention_input_data
        
        p_res_unit_op_1 = residual_unit(p_res_unit_op_1, filters=filters)

        # Perform Trunk Branch Operation
        trunk_branch_op = trunk_branch(trunk_input_data=p_res_unit_op_1, filters=filters)

        # Perform Mask Branch Operation
        mask_branch_op = mask_branch_3(mask_input_data=p_res_unit_op_1, filters=filters)

        # Perform Attention Residual Learning: Combine Trunk and Mask branch results
        ar_learning_op = attention_residual_learning(mask_input=mask_branch_op, trunk_input=trunk_branch_op)

        # Send branch results through #p residual_units
        p_res_unit_op_2 = ar_learning_op
        
        p_res_unit_op_2 = residual_unit(p_res_unit_op_2, filters=filters)

        return p_res_unit_op_2

#-------------------------------------------- THE MODEL -------------------------------------------------
#---------------------------------------------------------------------------------------------------------

def atten_resnet(input_shape,n_classes):
  # Initialize a Keras Tensor of input_shape
  input_data = Input(shape=input_shape)
        
  # Initial Layers before Attention Module
        
  conv_layer_1 = Conv2D(filters=32, kernel_size=7, strides=2, padding='same')(input_data)
        
  max_pool_layer_1 = MaxPool2D(pool_size=3, strides=2, padding='same')(conv_layer_1)

  # Residual Unit then Attention Module #1
  res_unit_1 = residual_unit(max_pool_layer_1, filters=[32, 32, 128])
  att_mod_1 = attention_module_1(res_unit_1, filters=[32, 32, 128])
        
  # Residual Unit then Attention Module #2
  res_unit_2 = residual_unit(att_mod_1, filters=[64, 64, 256], stride=2)
  att_mod_2 = attention_module_2(res_unit_2, filters=[64, 64, 256])

  # # Residual Unit then Attention Module #3
  res_unit_3 = residual_unit(att_mod_2, filters=[128, 128, 512], stride=2)
  att_mod_3 = attention_module_3(res_unit_3, filters=[128, 128, 512])

  # # Ending it all
  res_unit_end_1 = residual_unit(att_mod_3, filters=[256, 256, 1024],stride=2)
  res_unit_end_2 = residual_unit(res_unit_end_1, filters=[256, 256, 1024])
  res_unit_end_3 = residual_unit(res_unit_end_2, filters=[256, 256, 1024])
  res_unit_end_4 = residual_unit(res_unit_end_3, filters=[256, 256, 1024])

  # # Avg Pooling
  avg_pool_layer = AveragePooling2D(pool_size=7, strides=1)(res_unit_end_4)

  # # Flatten the data
  flatten_op = Flatten()(avg_pool_layer)

  # # FC Layers for prediction
  fully_connected_layer_1 = Dense(n_classes, activation="softmax")(flatten_op)

         
  # Fully constructed model
  model = Model(inputs=input_data, outputs=fully_connected_layer_1)
        
  return model
