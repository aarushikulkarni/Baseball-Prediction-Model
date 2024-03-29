# -*- coding: utf-8 -*-
"""nmd-1.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1kmrBDTbHD3sf1TvYuTotI7PkFaBaC2iG
"""

import pandas as pd
import numpy as np
import random
!pip install wandb -qU
import wandb
wandb.login()

judge_data = pd.read_csv('judge.csv')
# choose features of pitch
judge_features = ['description','release_speed','release_pos_x','release_pos_z','zone','vx0','vy0','vz0','ax','ay','az','effective_speed','release_pos_y']
judge_data = judge_data[judge_features].dropna(axis=0)
df = judge_data

# normalize values
for c in df.columns:
  if (c != 'description'):
    df.loc[:,c] = df.loc[:,c]/df.loc[:,c].abs().max()

# split the data
dfTrain = pd.DataFrame()
dfTest = pd.DataFrame()
num1 = int(len(df)-len(df)*.2)
other = []
while len(other)<=num1:
  x = random.randint(0,len(df))
  if x not in other:
    other.append(x)
for i in range(len(df)):
  if i in other:
    dfTrain = dfTrain.append(df.iloc[i,:])
  else:
    dfTest = dfTest.append(df.iloc[i,:])

# separate output from input
yTrain = dfTrain['description']
yTest = dfTest['description']

dfTrain_features = dfTrain.drop('description',axis=1)
dfTest_features = dfTest.drop('description',axis=1)

# add bias column
train_data = pd.concat([pd.Series(1,index=dfTrain_features.index,name='00'),dfTrain_features],axis=1)
test_data = pd.concat([pd.Series(1,index=dfTest_features.index,name='00'),dfTest_features],axis=1)
possible_classes = list(yTrain.unique())

y1 = np.zeros([dfTrain_features.shape[0],len(possible_classes)])
y1 = pd.DataFrame(y1)

y2 = np.zeros([dfTest_features.shape[0],len(possible_classes)])
y2 = pd.DataFrame(y2)

wandb.init(project="nmd-1", entity="aarushi-k")
wandb.save("nmd-1")
wandb.config = {"learning_rate": 0.0005, "epochs":10000,"num_train_runs":len(dfTrain_features),"num_test_runs":len(dfTest_features)}

# create ground truth matrices
for row in range(len(y1)):
  yValue = yTrain.iloc[row]
  theIndex = possible_classes.index(yValue)
  y1.iloc[row,theIndex] = 1

for row in range(len(y2)):
  yValue = yTest.iloc[row]
  theIndex = possible_classes.index(yValue)
  y2.iloc[row,theIndex] = 1

# prediction function
def hypothesis(X,theta):
  return 1 / (1+np.exp(-(np.dot(X,theta)))) - 0.0000001

def cost(X,y,theta):
  y1 = hypothesis(X,theta)
  return -(1/len(X))*np.sum(y*np.log(y1)+(1-y)*np.log(1-y1))

# gradient descent
def gradient_descent(X,y,theta,alpha,epochs,data):
  m = len(X)
  
  if data=="train":
    wandb_dict_train = {"loss":0,"Accuracy":0}
  else:
    wandb_dict_test = {"loss":0,"Accuracy":0}

  for i in range(0,epochs): # run for each epoch
    if data=="train":
      wandb_dict_train["loss"] = c.mean()
      wandb_dict_train["Accuracy"] = accuracy(theta,X,y)
      wandb.log(wandb_dict_train)
    else:
      wandb_dict_test["loss"] = c.mean()
      wandb_dict_test["Accuracy"] = accuracy(theta,X,y)
      wandb.log(wandb_dict_test)

    h = hypothesis(X,theta) # predict an outcome based on input and weights
    loss = h - y
    gradient = np.dot(X.transpose(),loss) / m
    theta = theta - alpha * gradient # update theta

  theta = pd.DataFrame(theta)
  return theta

def accuracy(theta,X,y,classes=11):
  output = []
  for i in range(classes):
    theta = pd.DataFrame(theta)
    h = hypothesis(X,theta.iloc[:,i]) # predict outcomes based on updated weights
    output.append(h)
  output = pd.DataFrame(output)

  accuracy = 0
  for col in range(classes):
    for row in range(len(y)):
      if y.iloc[row,col] == 1 and output.iloc[col,row] >=.5: # calculate accuracy
        accuracy += 1
  accuracy = accuracy/len(X)
  return accuracy

# initialize theta for train and test
theta1 = np.ones([dfTrain_features.shape[1]+1, y1.shape[1]])
wandb.config.update({"learning_rate": 0.0005, "epochs":10000,"num_train_runs":len(dfTrain),"num_test_runs":len(dfTest)})

theta2 = np.ones([dfTest_features.shape[1]+1, y2.shape[1]])
wandb.config.update({"learning_rate": 0.0005, "epochs":10000,"num_train_runs":len(dfTrain),"num_test_runs":len(dfTest)})

# update weights
theta1 = gradient_descent(train_data,y1, theta1, 0.0005, 10000,"train")

theta2 = gradient_descent(test_data,y2, theta2, 0.0005, 10000,"test")

wandb.save("nmd-1")

# accuracy
print(accuracy(theta1,train_data,y1)) # train
print(accuracy(theta2,test_data,y2)) # test

