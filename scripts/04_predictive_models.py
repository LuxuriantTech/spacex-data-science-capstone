"""Compare four classifiers using the IBM course protocol.

Based on IBM Skills Network SpaceX labs. See ATTRIBUTION.md and SOURCES.json.
"""
from pathlib import Path
import os
import matplotlib
matplotlib.use('Agg')
from IPython.display import display
HERE=Path(__file__).resolve().parents[1]
DATA=HERE/'data'
OUT=HERE/'results'/'04_machine_learning'
OUT.mkdir(parents=True,exist_ok=True)
os.chdir(OUT)

# Save each plotted figure for portable command-line reproduction.
_figure_number=0
def save_current_figure():
    global _figure_number
    import matplotlib.pyplot as plt
    _figure_number+=1
    plt.savefig(OUT/f'figure_{_figure_number:02d}.png',dpi=150)
    plt.close()

# Pandas is a software library written for the Python programming language for data manipulation and analysis.
import pandas as pd
# NumPy is a library for the Python programming language, adding support for large, multi-dimensional arrays and matrices, along with a large collection of high-level mathematical functions to operate on these arrays
import numpy as np
# Matplotlib is a plotting library for python and pyplot gives us a MatLab like plotting framework. We will use this in our plotter function to plot data.
import matplotlib.pyplot as plt
#Seaborn is a Python data visualization library based on matplotlib. It provides a high-level interface for drawing attractive and informative statistical graphics
import seaborn as sns
# Standardize the model features using the IBM course protocol.
from sklearn import preprocessing
# Allows us to split our data into training and testing data
from sklearn.model_selection import train_test_split
# Allows us to test parameters of classification algorithms and find the best one
from sklearn.model_selection import GridSearchCV
# Logistic Regression classification algorithm
from sklearn.linear_model import LogisticRegression
# Support Vector Machine classification algorithm
from sklearn.svm import SVC
# Decision Tree classification algorithm
from sklearn.tree import DecisionTreeClassifier
# K Nearest Neighbors classification algorithm
from sklearn.neighbors import KNeighborsClassifier

def plot_confusion_matrix(y,y_predict):
    from sklearn.metrics import confusion_matrix
    plt.figure(figsize=(5.5,4.5))
    ax=sns.heatmap(confusion_matrix(y,y_predict),annot=True,fmt='d',cbar=False,
       xticklabels=['IBM Class 0','IBM Class 1'],yticklabels=['IBM Class 0','IBM Class 1'])
    ax.set(xlabel='Predicted label',ylabel='True label',title='Confusion matrix: IBM target (18 test records)')
    plt.tight_layout();save_current_figure()


data=pd.read_csv(DATA/'dataset_part_2.csv')
data.head()

X=pd.read_csv(DATA/'dataset_part_3.csv')
X.head()

Y=data['Class'].to_numpy()
assert len(Y)==len(X)==90


transform = preprocessing.StandardScaler()

X=transform.fit_transform(X)

X_train,X_test,Y_train,Y_test=train_test_split(X,Y,test_size=0.2,random_state=2)

Y_test.shape

parameters ={'C':[0.01,0.1,1],
             'penalty':['l2'],
             'solver':['lbfgs']}

parameters={'C':[0.01,0.1,1],'penalty':['l2'],'solver':['lbfgs']}
lr=LogisticRegression()
logreg_cv=GridSearchCV(lr,parameters,cv=10,n_jobs=1)
logreg_cv.fit(X_train,Y_train)

print("tuned hpyerparameters :(best parameters) ",logreg_cv.best_params_)
print("accuracy :",logreg_cv.best_score_)

logreg_cv.score(X_test,Y_test)

yhat=logreg_cv.predict(X_test)
plot_confusion_matrix(Y_test,yhat)

parameters = {'kernel':('linear', 'rbf','poly','rbf', 'sigmoid'),
              'C': np.logspace(-3, 3, 5),
              'gamma':np.logspace(-3, 3, 5)}
svm = SVC()

svm_cv=GridSearchCV(svm,parameters,cv=10,n_jobs=1)
svm_cv.fit(X_train,Y_train)

print("tuned hpyerparameters :(best parameters) ",svm_cv.best_params_)
print("accuracy :",svm_cv.best_score_)

svm_cv.score(X_test,Y_test)

yhat=svm_cv.predict(X_test)
plot_confusion_matrix(Y_test,yhat)

parameters={'criterion':['gini','entropy'],'splitter':['best','random'],
 'max_depth':[2*n for n in range(1,10)],'max_features':['sqrt'],
 'min_samples_leaf':[1,2,4],'min_samples_split':[2,5,10]}
# Historical classifier max_features='auto' meant sqrt; current sklearn rejects auto.
# Replace its obsolete alias and deduplicate the identical sqrt candidates.
tree=DecisionTreeClassifier(random_state=2)


tree_cv=GridSearchCV(tree,parameters,cv=10,n_jobs=1)
tree_cv.fit(X_train,Y_train)

print("tuned hpyerparameters :(best parameters) ",tree_cv.best_params_)
print("accuracy :",tree_cv.best_score_)

tree_cv.score(X_test,Y_test)

yhat=tree_cv.predict(X_test)
plot_confusion_matrix(Y_test,yhat)

parameters = {'n_neighbors': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
              'algorithm': ['auto', 'ball_tree', 'kd_tree', 'brute'],
              'p': [1,2]}

KNN = KNeighborsClassifier()

knn_cv=GridSearchCV(KNN,parameters,cv=10,n_jobs=1)
knn_cv.fit(X_train,Y_train)

print("tuned hpyerparameters :(best parameters) ",knn_cv.best_params_)
print("accuracy :",knn_cv.best_score_)

knn_cv.score(X_test,Y_test)

yhat = knn_cv.predict(X_test)
plot_confusion_matrix(Y_test,yhat)

models={'Logistic regression':logreg_cv,'SVM':svm_cv,'Decision tree':tree_cv,'KNN':knn_cv}
results=pd.DataFrame([{'model':name,'cv_accuracy':model.best_score_,
 'test_accuracy':model.score(X_test,Y_test),'best_parameters':repr(model.best_params_)} for name,model in models.items()])
display(results)
results.to_csv(OUT/'model_results.csv',index=False)
results.set_index('model')[['cv_accuracy','test_accuracy']].plot.barh(figsize=(9,4),xlim=(0,1),xlabel='Accuracy',title='IBM lab protocol: CV and 18-launch held-out scores')
plt.tight_layout();save_current_figure()


import json
from sklearn.metrics import accuracy_score,confusion_matrix
summary=[]
for name,model in models.items():
    predictions=model.predict(X_test)
    assert len(predictions)==18
    assert np.isfinite(model.cv_results_['mean_test_score']).all()
    assert abs(accuracy_score(Y_test,predictions)-model.score(X_test,Y_test))<1e-12
    summary.append({'model':name,'best_cv_accuracy':float(model.best_score_),'test_accuracy':float(model.score(X_test,Y_test)),'correct':int((predictions==Y_test).sum()),'test_n':len(Y_test),'confusion_matrix':confusion_matrix(Y_test,predictions).tolist(),'candidates':len(model.cv_results_['params'])})
(OUT/'RESULTS.json').write_text(json.dumps({'models':summary,'protocol_limit':'Standardization before split follows IBM template; contains leakage. Small reused holdout, descriptive lab results only.'},indent=2))
print(json.dumps(summary,indent=2))
