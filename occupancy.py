# -*- coding: utf-8 -*-
"""tesina.ipynb

Automatically generated by Colaboratory.

**Imports**
"""

import os
import sys
import shutil
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn import tree
from sklearn.svm import SVC
import matplotlib.pyplot as plt
from sklearn import preprocessing
from sklearn.decomposition import PCA
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import GridSearchCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.model_selection import TimeSeriesSplit, cross_val_score
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.metrics import f1_score, roc_auc_score, roc_curve, confusion_matrix, classification_report, accuracy_score, recall_score, precision_score

"""**Data preparation**"""

data_train = pd.read_csv('./data/datatraining.txt', header=0, index_col=1, parse_dates=True, sep=",")
data_valid = pd.read_csv('./data/datatest.txt', header=0, index_col=1, parse_dates=True, sep=",")
data_test = pd.read_csv('./data/datatest2.txt', header=0, index_col=1, parse_dates=True, sep=",")

data = pd.concat([data_valid, data_train, data_test])
# print(data.head)
X = data.drop(['Occupancy'], axis=1)
Y = data['Occupancy']
X_explore = X.drop(['date'], axis=1)
# print(X_explore.describe())

"""**Class distribution**"""

# Class distribution
class_distrib = [sum(1 for y in Y if y == 0), sum(1 for y in Y if y == 1)]
class_names = ['Unoccupied', 'Occupied']

bar_plot = plt.bar(class_names, class_distrib)
bar_plot[0].set_color('g')
bar_plot[1].set_color('r')
plt.xlabel('Label')
plt.ylabel('Num. of instances')
plt.show()

"""**Boxplots of attributes**"""

attr_names = ['Temperature', 'Humidity', 'Light', 'CO2', 'HumidityRatio']

for i in range(0, len(attr_names)):
  plt.figure()
  sns.boxplot(x='Occupancy', y=attr_names[i], data=data)

# Histogram
X.hist()
plt.tight_layout()

"""**Data analysis**"""

# Series of each attribute of the 3 datasets
plt.figure(figsize=(10,12))
n_features = data.values.shape[1]

for i in range(1, n_features):
  plt.subplot(n_features, 1, i)
  plt.plot(data_valid.index, data_valid.values[:, i])
  plt.plot(data_train.index, data_train.values[:, i])
  plt.plot(data_test.index, data_test.values[:, i])

  plt.title(data.columns[i])
plt.tight_layout()

# Correlation matrix
corr = X.corr()
mask = np.zeros(corr.shape, dtype=bool)
mask[np.triu_indices(len(mask))] = True
plt.subplots(figsize=(12,8))
sns.heatmap(corr, annot = True, vmin = -1, vmax = 1, center = 0, cmap = 'coolwarm')
plt.yticks(rotation = 0)

"""**Normalization**"""

# X = X.drop(['HumidityRatio', 'Temperature', 'Humidity', 'CO2'], axis=1)
scaler = MinMaxScaler()
scaler.fit(X)
X = scaler.transform(X)

"""**PCA**"""

# X = X.drop(['HumidityRatio'], axis=1)
scaler = StandardScaler()
scaler.fit(X)
X = scaler.transform(X)

pca = PCA(n_components=3)
X = pca.fit_transform(X)
print(pca.explained_variance_ratio_)

# pca_df = pd.DataFrame(data = X, columns = ['PC1', 'PC2'], index = Y.index)
# new_df = pd.concat([pca_df, Y], axis=1)
# print(new_df)

# Scree plot PCA
# percent_variance = np.round(pca.explained_variance_ratio_* 100, decimals =2)
# columns = ['PC1', 'PC2', 'PC3', 'PC4', 'PC5']
# plt.bar(x= range(1,6), height=percent_variance, tick_label=columns)
# plt.ylabel('Percentate of Variance Explained')
# plt.xlabel('Principal Component')
# plt.title('PCA Scree Plot')
# plt.show()

# Plot PC1 vs PC2
targets = [0, 1]
fig = plt.figure(figsize = (8,8))
ax = fig.add_subplot(1,1,1) 
ax.set_xlabel('PC1')
ax.set_ylabel('PC2')

ax.set_title('PC1 vs PC2', fontsize = 14)

colors = ['g', 'r']

for target, color in zip(targets, colors):
    indicesToKeep = new_df['Occupancy'] == target
    ax.scatter(new_df.loc[indicesToKeep, 'PC1']
               , new_df.loc[indicesToKeep, 'PC2']
               , c = color
               , s = 25)
    
ax.legend(class_names)
ax.grid()

"""**Splitting dataset**"""

# print(X.shape)
X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=0.2, shuffle=False)
# print(sum([1 for s in y_test if s == 0]), sum([1 for s in y_test if s == 1]))
ts_split = TimeSeriesSplit(5)

"""**Classification models**"""

# Decision Tree
params = {'criterion': ['gini', 'entropy']}
dt = DecisionTreeClassifier()
grid_search = GridSearchCV(dt, params, cv=ts_split, scoring='f1')
grid_search.fit(X_train, y_train)
print(grid_search.best_score_, grid_search.best_params_)

dt = DecisionTreeClassifier(criterion=grid_search.best_params_['criterion'])
dt.fit(X_train, y_train)
y_pred = dt.predict(X_test)

print('****************** Decision Tree ******************')
print('Accuracy: {}'.format(accuracy_score(y_test, y_pred)))
print('Precision: {}'.format(precision_score(y_test, y_pred)))
print('Recall: {}'.format(recall_score(y_test, y_pred)))
print('F1 score: {}'.format(f1_score(y_test, y_pred)))

conf_matrix = confusion_matrix(y_test, y_pred)
sns.heatmap(conf_matrix, annot=True)
plt.title("Confusion matrix - Decision Tree")
plt.xlabel('Predicted class')
plt.ylabel('True class')
plt.show()

# Random Forest 
params = {'criterion': ['gini', 'entropy'], 'n_estimators': [100, 200]}
rf = RandomForestClassifier()
grid_search = GridSearchCV(rf, params, cv=ts_split, scoring='f1')
grid_search.fit(X_train, y_train)
print(grid_search.best_score_, grid_search.best_params_)

rf = RandomForestClassifier(criterion=grid_search.best_params_['criterion'], n_estimators=grid_search.best_params_['n_estimators'])
rf.fit(X_train, y_train)
y_pred = rf.predict(X_test)
print('****************** Random Forest ******************')
print('Accuracy: {}'.format(accuracy_score(y_test, y_pred)))
print('Precision: {}'.format(precision_score(y_test, y_pred)))
print('Recall: {}'.format(recall_score(y_test, y_pred)))
print('F1 score: {}'.format(f1_score(y_test, y_pred)))

conf_matrix = confusion_matrix(y_test, y_pred)
sns.heatmap(conf_matrix, annot=True)
plt.title("Confusion matrix - Random Forest")
plt.xlabel('Predicted class')
plt.ylabel('True class')
plt.show()

# Logistic Regression
params = {'C': [0.001, 0.001 , 0.01 , 0.1 , 1]}
lr = LogisticRegression()
grid_search = GridSearchCV(lr, params, cv=ts_split, scoring='f1')
grid_search.fit(X_train, y_train)
print(grid_search.best_score_, grid_search.best_params_)

lr = LogisticRegression(C=grid_search.best_params_['C'])
lr.fit(X_train, y_train)
y_pred = lr.predict(X_test)
acc = f1_score(y_test, y_pred)
print('****************** Logistic Regression ******************')
print('F1 Score on test set: {} with C = {}'.format(acc*100, grid_search.best_params_['C']))

print('Accuracy: {}'.format(accuracy_score(y_test, y_pred)))
print('Precision: {}'.format(precision_score(y_test, y_pred)))
print('Recall: {}'.format(recall_score(y_test, y_pred)))
print('F1 score: {}'.format(f1_score(y_test, y_pred)))

conf_matrix = confusion_matrix(y_test, y_pred)
sns.heatmap(conf_matrix, annot=True)
plt.title("Confusion matrix - Logistic Regression")
plt.xlabel('Predicted class')
plt.ylabel('True class')
plt.show()

"""**Comparison**"""

# ROC curve
classifiers = ['Decision Tree', 'Random Forest', 'Logistic Regression']
pred_dt = dt.predict_proba(X_test)
probs_dt = pred_dt[:, 1]
auc_dt = roc_auc_score(y_test, probs_dt)
fpr_dt, tpr_dt, _ = roc_curve(y_test, probs_dt)
plt.plot(fpr_dt, tpr_dt, c='b', label=classifiers[0])

pred_rf = rf.predict_proba(X_test)
probs_rf = pred_rf[:, 1]
auc_rf = roc_auc_score(y_test, probs_rf)
fpr_rf, tpr_rf, _ = roc_curve(y_test, probs_rf)
plt.plot(fpr_rf, tpr_rf, c='g', label=classifiers[1])

pred_lr = lr.predict_proba(X_test)
probs_lr = pred_lr[:, 1]
auc_lr = roc_auc_score(y_test, probs_lr)
fpr_lr, tpr_lr, _ = roc_curve(y_test, probs_lr)
plt.plot(fpr_lr, tpr_lr, c='r', label=classifiers[2])

plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.legend(loc='best')
plt.tight_layout()
plt.show()
