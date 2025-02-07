import pandas as pd
import numpy as np

features_data = pd.read_csv('src/project/AI_TEST/peak_features_elements.csv').sort_values(['name', 'ID'])
id0 = features_data[features_data['ID'] == 0]
id1 = features_data[features_data['ID'] == 1]
id2 = features_data[features_data['ID'] == 2]
id3 = features_data[features_data['ID'] == 3]
id4 = features_data[features_data['ID'] == 4]
id5 = features_data[features_data['ID'] == 5]
names = list(features_data['name'].unique())
sameIdDistance = []
numPeaks = {}
numPeaksID0 = {}
numPeaksID1 = {}
numPeaksID2 = {}
numPeaksID3 = {}
numPeaksID4 = {}
numPeaksID5 = {}

for name in names:
    numPeaks[name] = 0
    numPeaksID0[name] = 0
    numPeaksID1[name] = 0
    numPeaksID2[name] = 0
    numPeaksID3[name] = 0
    numPeaksID4[name] = 0
    numPeaksID5[name] = 0
    isoData = id0[id0['name'] == name]['Position']
    for j in range(isoData.shape[0]):
        if j == len(isoData) - 1:
            sameIdDistance.append(0)
        else:
            first = isoData.iloc[j]
            second = isoData.iloc[j + 1]
            sameIdDistance.append(second - first)
        numPeaks[name] += 1
        numPeaksID0[name] += 1
    isoData = id1[id1['name'] == name]['Position']
    for j in range(isoData.shape[0]):
        if j == len(isoData) - 1:
            sameIdDistance.append(0)
        else:
            first = isoData.iloc[j]
            second = isoData.iloc[j + 1]
            sameIdDistance.append(second - first)
        numPeaks[name] += 1
        numPeaksID1[name] += 1
    isoData = id2[id2['name'] == name]['Position']
    for j in range(isoData.shape[0]):
        if j == len(isoData) - 1:
            sameIdDistance.append(0)
        else:
            first = isoData.iloc[j]
            second = isoData.iloc[j + 1]
            sameIdDistance.append(second - first)
        numPeaks[name] += 1
        numPeaksID2[name] += 1
    isoData = id3[id3['name'] == name]['Position']
    for j in range(isoData.shape[0]):
        if j == len(isoData) - 1:
            sameIdDistance.append(0)
        else:
            first = isoData.iloc[j]
            second = isoData.iloc[j + 1]
            sameIdDistance.append(second - first)
        numPeaks[name] += 1
        numPeaksID3[name] += 1
    isoData = id4[id4['name'] == name]['Position']
    for j in range(isoData.shape[0]):
        if j == len(isoData) - 1:
            sameIdDistance.append(0)
        else:
            first = isoData.iloc[j]
            second = isoData.iloc[j + 1]
            sameIdDistance.append(second - first)
        numPeaks[name] += 1
        numPeaksID4[name] += 1
    isoData = id5[id5['name'] == name]['Position']
    for j in range(isoData.shape[0]):
        if j == len(isoData) - 1:
            sameIdDistance.append(0)
        else:
            first = isoData.iloc[j]
            second = isoData.iloc[j + 1]
            sameIdDistance.append(second - first)
        numPeaks[name] += 1
        numPeaksID5[name] += 1


features_data['distanceOfEqualId'] = np.round(sameIdDistance, 6).tolist()
features_data['numPeaks'] = features_data['name'].map(numPeaks)
features_data['numPeaksID0'] = features_data['name'].map(numPeaksID0)
features_data['numPeaksID1'] = features_data['name'].map(numPeaksID1)
features_data['numPeaksID2'] = features_data['name'].map(numPeaksID2)
features_data['numPeaksID3'] = features_data['name'].map(numPeaksID3)
features_data['numPeaksID4'] = features_data['name'].map(numPeaksID4)
features_data['numPeaksID5'] = features_data['name'].map(numPeaksID5)


features_data.sort_values(['name', 'Position'], inplace=True)
features_data.to_csv('src/project/AI_TEST/extracted_peak_features.csv', index=None)
