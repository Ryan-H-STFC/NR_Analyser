import numpy as np
import pandas as pd
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.preprocessing import LabelEncoder, MinMaxScaler
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
data = pd.read_csv('src/project/AI_TEST/peak_features_elements.csv')

# Extract relevant features from the experimental data
# data = data[data['name'].str.contains('n-tot')]
data = data[["name", 'ID', 'Position', 'Height', 'Distance', 'Integral', 'Width', 'Prominence', 'Prev Dip', 'Next Dip',
             'Tailedness', 'Skewness', 'FWHM', 'FW1QM', 'FW3QM', 'ratioToMaxHeight', 'ratioToNextHeight',
             'ratioToMaxWidth', 'ratioToNextWidth', 'ratioToTotalIntegral', 'ratioToMaxIntegral', 'ratioToNextIntegral',
             'Wavelet_mean', 'Wavelet_std']]
data.sort_values('name', inplace=True)
# data = data.loc[data['name'].str.contains('Sn'), :]
# data = data.loc[data['ID'] < 4, :]
data = data[data['Integral'] != 0]
counts = data['name'].value_counts()
data = data[data['name'].isin(counts[counts > 1].index)]
# # Step 1: Prepare Your Data
# # data = data[data['Peak FWHM'] != 0]
# data = data[data['Peak Prominence'] >= 10]
scaler = MinMaxScaler()


y = data['name'].values  # Assuming 'name' is your target variable

# X = data[['Peak Position', 'Peak Height', 'Peak Distance', 'Peak Integral', 'Peak Width',
#           'Peak Prominence', 'Peak Prev Dip']
#          ].values  # Adjust based on your feature columns
X = data[['ID', 'Position', 'Height', 'Distance', 'Integral', 'Width', 'Prominence', 'Prev Dip', 'Next Dip',
          'Tailedness', 'Skewness', 'FWHM', 'FW1QM', 'FW3QM', 'ratioToMaxHeight', 'ratioToNextHeight',
          'ratioToMaxWidth', 'ratioToNextWidth', 'ratioToTotalIntegral', 'ratioToMaxIntegral', 'ratioToNextIntegral',
          'Wavelet_mean', 'Wavelet_std']]


#   'numPeaksID0', 'numPeaksID1', 'numPeaksID2', 'numPeaksID3', 'numPeaksID4', 'numPeaksID5']]
# for colName in X.columns:
#     if colName == 'Peak ID':
#         continue
#     X[colName] = X[colName] / X[colName].max()
# Split the dataset into training and testing sets
# creating a RF classifier
# TODO - Consider the parameters given to clf and see how they affect the accuracy.
skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

for typec in ['rf', 'xgb']:
    if typec == 'rf':

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
        clf = RandomForestClassifier(n_estimators=200,
                                     criterion='entropy',
                                     bootstrap=True,
                                     verbose=3,
                                     min_samples_leaf=1,
                                     min_samples_split=24,
                                     n_jobs=-1,
                                     max_features=None
                                     )
        clf.fit(X, y)
        cv_scores = cross_val_score(clf, X, y, cv=skf, scoring='accuracy', n_jobs=-1)
    if typec == 'xgb':
        y_string = data['name'].values
        label_encoder = LabelEncoder()
        y_encoded = label_encoder.fit_transform(y_string)
        X_train, X_test, y_train, y_test = train_test_split(
            X, y_encoded, test_size=0.4, random_state=42, stratify=y_encoded)
        clf = xgb.XGBClassifier(n_estimators=50, learning_rate=0.1, objective='multi:softmax')

        clf.fit(X, y_encoded)
        cv_scores = cross_val_score(clf, X, y_encoded, cv=skf, scoring='accuracy', n_jobs=-1)

# todo _________________________________________________________________________________________________________________

# ¦ Add more classifer models for comparison

# @

# @

# ? Adjust hyper-parameters of models

# @

# @

# ! ADD MORE INDIVIUAL TESTS FOR COMPARSISON

# todo _________________________________________________________________________________________________________________

    y_pred = clf.predict(X_test)
    print(f"ACCURACY OF THE MODEL - TEST SPLIT: {metrics.accuracy_score(y_test, y_pred)}")
    print(f"Cross-validation scores: {cv_scores}")
    print("\n\n\n")
    print(f"Mean accuracy: {np.mean(cv_scores):.4f} ± {np.std(cv_scores):.4f}")
    print("\n\n\n")

    # using metrics module for accuracy calculation

    # performing predictions on the test dataset
    y_pred = clf.predict(X_train)
    print("ACCURACY OF THE MODEL - TRAIN SPLIT:", metrics.accuracy_score(y_train, y_pred,))
    print("\n\nNe")
    y_pred = clf.predict([[5, 22474.8, 2.635015, 144.7, 2.99889, 448.574, 0.112949, 21433.9, 22600.9, -1.666703, -0.326988,
                           0.0, 0.0, 0.0, 0.134719, 0.134422, 0.001394, 0.004551, 3e-06, 8e-06, 0.017418,
                           -0.0009902003620386453, 0.0021002222501741463]],)  # Ne
    y_pred = y_pred if typec == 'rf' else np.unique(y_string)[y_pred]
    print(f"{y_pred}")
    print(f"[{'Ne' == y_pred}\n\n")

    print("\n\nCl")
    y_pred = clf.predict([[4, 136466.0, 4.275637, 3625.0, 361.714, 1580.31, 1.849697, 135619.0, 139982.0, -1.130961,
                           0.473312, 0.0, 0.0, 1163.693152, 0.048343, 0.041461, 0.00021, 9e-06, 0.000307, 0.000384, 6.4e-05,
                           0.26763379821825145, 0.5248189141486688]])  # Cl
    y_pred = y_pred if typec == 'rf' else np.unique(y_string)[y_pred]
    print(f"{y_pred}")
    print(f"[{'Cl' == y_pred}\n\n")

    print("\n\nZr")
    y_pred = clf.predict([[0, 12510.0, 67.574152, 35.3, 590.917, 25.4703, 63.158608, 12450.9, 12534.6, -0.56929, 0.939872,
                           14.645825, 25.738309, 8.659296, 0.195987, 0.039847, 2e-06, 1e-06, 0.000318, 0.000363, 2.3e-05,
                           -0.49303543963236235, 0.9475009431527907]]
                         )  # Zr
    y_pred = y_pred if typec == 'rf' else np.unique(y_string)[y_pred]
    print(f"{y_pred}")
    print(f"[{'Zr' == y_pred}\n\n")

    print("\n\nTe")
    y_pred = clf.predict([[5, 11180.0, 8.421905, 34.2, 21.5564, 10.7273, 4.554717, 11169.8, 11214.1, 0.294459, 1.354787,
                           10.070813, 0.0, 4.951085, 0.008518, 0.003789, 4e-06, 5e-06, 3.3e-05, 3.4e-05, 5.4e-05,
                           0.6066846017473959, 1.2635637221892084]]
                         )  # Te
    y_pred = y_pred if typec == 'rf' else np.unique(y_string)[y_pred]
    print(f"{y_pred}")
    print(f"[{'Te' == y_pred}\n\n")

    print("\n\nOs")
    y_pred = clf.predict([[0, 3055.22, 88.937044, 45.98, 121.514, 7.5804, 51.179082, 3050.85, 3097.94, 1.094891, 1.53059,
                           6.26377, 0.0, 2.431517, 0.025094, 0.011675, 6.3e-05, 3.6e-05, 0.003543, 0.016685, 0.000892,
                           -0.8740990396802523, 1.7134332664220597]]
                         )  # Os
    y_pred = y_pred if typec == 'rf' else np.unique(y_string)[y_pred]
    print(f"{y_pred}")
    print(f"[{'Os' == y_pred}\n\n")

    print("\n\nEr")
    y_pred = clf.predict([[0, 3895.29, 52.802253, 24.21, 82.7596, 5.93241, 34.856209, 3891.24, 3916.18, 0.303839, 1.257523,
                           4.530082, 0.0, 2.451885, 0.014412, 0.006145, 0.422061, 0.445951, 0.003304, 0.082124, 0.007158,
                           6.079452120591168, 8.983919648955714]]
                         )  # Er
    y_pred = y_pred if typec == 'rf' else np.unique(y_string)[y_pred]
    print(f"{y_pred}")
    print(f"[{'Er' == y_pred}\n\n")

    print("\n\nPb")
    y_pred = clf.predict([[5, 4623700.0, 7.791252, 72200.0, 5312.29, 42290.9, 0.450869, 4598800.0, 4651700.0, -1.451538,
                           -0.566693, 0.0, 0.0, 0.0, 0.122578, 0.122177, 0.000336, 9.4e-05, 0.000557, 0.001171, 0.000397,
                           0.05575590905891568, 0.24593624034238495]]
                         )  # Pb
    y_pred = y_pred if typec == 'rf' else np.unique(y_string)[y_pred]
    print(f"{y_pred}")
    print(f"[{'Pb' == y_pred}\n\n")

    print("\n\nPb")
    y_pred = clf.predict([[0, 3357.0, 63.561687, 447.01, 130.441, 8.80311, 52.809374, 3295.55, 3790.07, 4.354982, 2.340623, 2.715864, 4.493633, 1.682187, 1.0, 0.175049, 0.0, 0.0, 1.4e-05, 2.9e-05, 0.0, 33.21119388362486, 28.105373958983773
                           ]]
                         )  # Pb
    y_pred = y_pred if typec == 'rf' else np.unique(y_string)[y_pred]
    print(f"{y_pred}")
    print(f"[{'Pb' == y_pred}\n\n")

    print("\n\nPb")
    y_pred = clf.predict([[2, 1686.13, 27.671278, 794.05, 81.6539, 28.3424, 16.85454, 1656.34, 2446.77, 6.390324, 2.661091, 9.518453, 0.0, 3.880764, 0.435345, 0.374256, 0.0, 0.0, 9e-06, 1.8e-05, 1.9e-05, 9.545539444341205, 7.717178247819772
                           ]]
                         )  # Pb
    y_pred = y_pred if typec == 'rf' else np.unique(y_string)[y_pred]
    print(f"{y_pred}")
    print(f"[{'Pb' == y_pred}\n\n")

    print("\n\nCd")
    y_pred = clf.predict([[1, 27.57, 201.273178, 1.3983, 60.7772, 0.841295, 196.554587, 22.8353, 28.7018, 4.310851, 2.282586, 0.354736, 0.532098, 0.222926, 0.022588, 0.000869, 0.035359, 0.045728, 0.00312, 0.070645, 0.00112, 19.703068147201723, 29.46025096817547
                           ]]
                         )  # Cd
    y_pred = y_pred if typec == 'rf' else np.unique(y_string)[y_pred]
    print(f"{y_pred}")
    print(f"[{'Cd' == y_pred}\n\n")

    importances = list(clf.feature_importances_)
    print(sorted(list(zip(importances, list(X.columns)))))
# st = SuperTree(clf,
#                X_train,
#                y_train,
#                list(X.columns),
#                y)

# st.save_html("file.html")
