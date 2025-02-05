import numpy as np
import pandas as pd
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
import xgboost as xgb
from supertree import SuperTree

from collections import Counter
from rich import print
# metrics are used to find accuracy or error
from sklearn import metrics
"""  _____________________________________________________# NOTES #_____________________________________________________

    - Model should be created for a single peak, then comparing against all ENDF data,

    ------------------------------------------------------- DATA -------------------------------------------------------
    - Peak Width
    - Integral Size
    #? Integral Contribution about peak
    - Distance between successive peaks small and large
    # TODO - Create seperate distance values for small and large peak,
    # TODO - This will require classifying peaks as small or large in some fashion, either by integral, height, width,
    # TODO - or some metric which involves them all.
    # TODO - This may require more data features:
    # *         - Peak Prominence !Done
    # *         - Successive dip position !Done

    # *         - Distance to next prominent peak (ignoring tiny peaks)
    # !To Be Done (Classifying peaks as L0-L4:redundent)
    # *
    #? Split larger and smaller peak distances
    - Position of peaks
    #! Consider Non alignment of contributing elements


    Use a modified version of databaseFill.py
    ____________________________________________________________________________________________________________________

    ----------------------------------------------- Pre-processing Data ------------------------------------------------

    For all ENDF data, compile all Peak widths, all successive peak distances.
        - Peak Widths already in data folder for NR_ANALYSER

    - Restrict all graph data to be between the largest peak limit range about the selected peak of input data

    - If peak found:
        - Find peak width

    - Perform integral using largest peak limits
        - Order by Size

    - Consider peak interference, check positions of peaks reletive to 2nd Derivatives of input data, which may need
    smoothing to some degree if not ideal

    - Filtering down ENDF database to 'ideal' selection about a peak.

    ____________________________________________________________________________________________________________________
"""

# Load the experimental data
data = pd.read_csv('src/project/AI_TEST/extracted_peak_features.csv')

# Extract relevant features from the experimental data
# data = data[data['name'].str.contains('n-tot')]
data = data[["name", "ID", "Position", "Height", "Distance", "Integral", "Width",
             "Prominence", "Prev Dip", "Next Dip", "Tailedness", "Skewness", "FWHM",
             "FW1QM", "FW3QM", 'distanceOfEqualId', 'numPeaks',
             'numPeaksID0', 'numPeaksID1', 'numPeaksID2', 'numPeaksID3', 'numPeaksID4', 'numPeaksID5']]
data.sort_values('name', inplace=True)
# data = data.loc[data['name'].str.contains('Sn'), :]
# data = data.loc[data['ID'] < 4, :]
data = data[data['Integral'] != 0]
counts = data['name'].value_counts()
data = data[data['name'].isin(counts[counts > 1].index)]
# # Step 1: Prepare Your Data
# # data = data[data['Peak FWHM'] != 0]
# data = data[data['Peak Prominence'] >= 10]

y = data['name'].values  # Assuming 'name' is your target variable
# X = data[['Peak Position', 'Peak Height', 'Peak Distance', 'Peak Integral', 'Peak Width',
#           'Peak Prominence', 'Peak Prev Dip']
#          ].values  # Adjust based on your feature columns
X = data[["Position", "Height", "Distance", "Integral", "Width", "Prominence",
          "Prev Dip", "Next Dip", "Tailedness", "Skewness", "FWHM", "FW1QM", "FW3QM", "distanceOfEqualId"]]


#   'numPeaksID0', 'numPeaksID1', 'numPeaksID2', 'numPeaksID3', 'numPeaksID4', 'numPeaksID5']]
# for colName in X.columns:
#     if colName == 'Peak ID':
#         continue
#     X[colName] = X[colName] / X[colName].max()
# Split the dataset into training and testing sets
# creating a RF classifier
# TODO - Consider the parameters given to clf and see how they affect the accuracy.
typec = 'rf'
if typec == 'rf':
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
    clf = RandomForestClassifier(n_estimators=150,
                                 criterion='entropy',
                                 bootstrap=True,
                                 verbose=3,
                                 min_samples_leaf=1,
                                 min_samples_split=3,
                                 n_jobs=-1,
                                 max_features='sqrt'
                                 )
if typec == 'xgb':
    y_string = data['name'].values
    label_encoder = LabelEncoder()
    y_encoded = label_encoder.fit_transform(y_string)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y_encoded, test_size=0.3, random_state=42, stratify=y_encoded)
    clf = xgb.XGBClassifier(n_estimators=100, learning_rate=0.1, objective='multi:softmax')

# Training the model on the training dataset
# fit function is used to train the model using the training sets as parameters
clf.fit(X_train, y_train)
score = clf.score(X_test, y_test)
print(score)
print()
# performing predictions on the test dataset
y_pred = clf.predict(X_train)
print("ACCURACY OF THE MODEL - TRAIN SPLIT:", metrics.accuracy_score(y_train, y_pred))

y_pred = clf.predict(X_test)
# using metrics module for accuracy calculation
print("ACCURACY OF THE MODEL - TEST SPLIT:", metrics.accuracy_score(y_test, y_pred))

# Using ["Position", "Height", "Distance", "Integral", "Width", "Prominence",
#        "Prev Dip", "Next Dip", "Tailedness", "Skewness", "FWHM", "FW1QM", "FW3QM", 'distanceOfEqualId']

y_pred = clf.predict([[112.0, 9.784931, 39.6, 2.32297, 3.69186, 2.222619,
                     107.645, 149.556, 2.608728, 1.854333, 0.0, 0.0, 0.0, 330.0]])  # Se
print(y_pred)

y_pred = clf.predict([[914.261, 53.522844, 1.812, 6.99545, 0.462148, 41.203925, 913.478,
                     915.05, -0.231332, 1.023665, 0.293974, 0.851268, 0.1546, 3.449]])  # U
print(y_pred)

y_pred = clf.predict([[19853.1, 9.300742, 26496.9, 10423.0, 5579.93, 5.828014, 10000.0, 39174.6,
                     0.559245, 1.35864, 3716.405607, 0.0, 1545.196911, 824076.9]])  # Mg
print(y_pred)

y_pred = clf.predict([[745227.0, 5.451085, 953.0, 1309.04, 732.31, 4.814391, 744588.0,
                     745957.0, -0.900365, 0.629445, 506.277137, 0.0, 286.328852, 1110.0]])  # Ni
print(y_pred)
y_pred = clf.predict([[1363.95, 57.862398, 20.61, 90.3488, 4.1014, 53.965171, 1360.77,
                     1381.68, 1.739497, 1.751446, 2.044336, 3.052493, 1.288864, 71.9]])  # Sb
print(y_pred)

# using metrics module for accuracy calculation

# print(y_string[y_pred[0]])


importances = list(clf.feature_importances_)
print(sorted(list(zip(importances, list(X.columns)))))
st = SuperTree(clf,
               X_train,
               y_train,
               list(X.columns),
               y)

# st.save_html("file.html")
