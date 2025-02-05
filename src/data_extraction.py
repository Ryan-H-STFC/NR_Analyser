import os
import pandas as pd
import numpy as np
from scipy.stats import kurtosis, skew
from scipy.interpolate import UnivariateSpline
from findpeaks import findpeaks
from multiprocessing import Pool

from project.spectra.SpectraDataStructure import SpectraData
from project.helpers.interpName import interpName

# Directories containing the ENDF data files
data_dir = r'src\project\data\Peak information\Energy'
graph_dir = r'src\project\data\Graph Data'
distributionDir = r'src\project\data\Distribution Information'
dist_filePaths: list[str] = [
    f for f in os.listdir(distributionDir) if f.endswith(".csv")
]
distributions = {}
for filepath in dist_filePaths:
    name = filepath[:-4]
    dist = pd.read_csv((f"{distributionDir}/{filepath}"), header=None)
    distributions[name] = dict({d[0]: d[1] for d in dist.values})
# Initialize a list to store all extracted features
all_features = []

ISOTOPES = [name for name in os.listdir(graph_dir)
            if name.split('_')[0][-1].isnumeric() and 'n-tot' in name]
ELEMENTS = [name for name in os.listdir(graph_dir)
            if name.split('_')[0][-1].isalpha() and 'n-tot' in name]
COMPOUNDS = [name for name in os.listdir(f"{graph_dir}/Compound Data/")
             if name.split('_')[0][-1].isalpha() and 'n-tot' in name]

isotope_data = pd.read_csv("src\\isotope_data.csv", names=['spin', 'mass'])
# Loop over each file in the directory


def get_data(filename):
    if filename.endswith('.csv'):  # Assuming the files are in CSV format
        # Load the graph data from the current file
        filepath = os.path.join(data_dir, filename)
        graphData = pd.read_csv(f"{graph_dir}\\{'Compound Data\\' if 'compound' in filename else ''}{filename}",
                                header=None,)
        name = f'{filename.replace('_tableData_max', '')}'[:-4]
        # isoName = interpName(name)
        # isoName = f"{isoName['zNum']}{isoName['symbol']}"
        spectra = SpectraData(name, None,
                              None, None,
                              graphData,
                              (0, 0, 0),
                              False,
                              distributions.get(name, None),
                              distributions.get(name, None),
                              isCompound='compound' in name,
                              thresholds={'n-g': 0, 'n-tot': 0},
                              updatingDatabase=True,
                              )

        x, y = graphData.iloc[:, 0].to_numpy(), graphData.iloc[:, 1].to_numpy()
        # Find peaks in the data

        peaks = spectra.maxima
        dips = spectra.minima
        # Initialize lists to store extracted features for the current file
        peak_ids = []
        positions = []
        heights = []
        widths = []
        distances = []
        integrals = []
        prominence = []
        prev_dips = []
        next_dips = []
        tailedness = []
        skewness = []
        fwhm = []
        fw3qm = []
        fw1qm = []
        mass = []
        spin = []
        tableData = spectra.maxTableData
        # isoData = isotope_data.loc[isoName]
        # Loop over each detected peak
        for i in range(tableData.shape[0]):
            prom = spectra.peakDetector.prominences[i]
            if prom > 70:
                peak_ids.append(0)
            elif prom > 30:
                peak_ids.append(1)
            elif prom > 10:
                peak_ids.append(2)
            elif prom > 5:
                peak_ids.append(3)
            elif prom > 3:
                peak_ids.append(4)
            elif prom > 1:
                peak_ids.append(5)
            else:
                # This intentionally removes tiny peaks / noisy peaks that are found
                continue

            row = tableData[tableData['Energy (eV)'] == peaks[i][0]]
            if row.empty:
                continue
            positions.append(peaks[i, 0])
            heights.append(peaks[i, 1])

            integrals.append(float(row['Integral']))
            widths.append(float(row['Peak Width']))
            prominence.append(prom)
            prev_dip = np.max(dips[dips[:, 0] < peaks[i, 0]], axis=0)[0]
            next_dip = np.min(dips[dips[:, 0] > peaks[i, 0]], axis=0)[0]
            prev_dips.append(prev_dip)
            next_dips.append(next_dip)
            peak_graph = graphData.loc[np.where((x >= prev_dip) & (x <= next_dip))]
            tailedness.append(kurtosis(peak_graph[1]))
            skewness.append(skew(peak_graph[1]))

            if np.array(peak_graph[1] - np.max(peak_graph[1]) / 2).shape[0] > 3:
                spline = UnivariateSpline(peak_graph[0], peak_graph[1] - np.max(peak_graph[1]) / 2, s=0)
                if spline.roots().shape[0] == 2:
                    fwhm.append(np.diff(spline.roots())[0])
                else:
                    fwhm.append(0)
            else:
                fwhm.append(0)
            if np.array(peak_graph[1] - np.max(peak_graph[1]) / 4).shape[0] > 3:
                spline = UnivariateSpline(peak_graph[0], peak_graph[1] - np.max(peak_graph[1]) / 4, s=0)
                if spline.roots().shape[0] == 2:
                    fw1qm.append(np.diff(spline.roots())[0])
                else:
                    fw1qm.append(0)
            else:
                fw1qm.append(0)
            if np.array(peak_graph[1] - np.max(peak_graph[1]) / 2).shape[0] > 3:
                spline = UnivariateSpline(peak_graph[0], peak_graph[1] - 3 * np.max(peak_graph[1]) / 4, s=0)
                if spline.roots().shape[0] == 2:
                    fw3qm.append(np.diff(spline.roots())[0])
                else:
                    fw3qm.append(0)
            else:
                fw3qm.append(0)
            # Calculate distance to the next peak if it exists
            if i < len(peaks) - 1:
                distances.append(peaks[i + 1, 0] - peaks[i, 0])
            else:
                distances.append(0)

            # mass.append(float(isoData['mass']))
            # spin.append(float(isoData['spin']))
        # sameIDdistances = []
        # for i in range(len(positions)):
        #     distancesIDs = np.array(positions)[np.where(np.array(peak_ids) == peak_ids[i])]
        #     if i == len(distancesIDs) - 1:
        #         sameIDdistances.append(0)
        #     else:
        #         sameIDdistances.append(distancesIDs[i + 1] - distancesIDs[i])
        # Store extracted features in a dictionary
        feature_list = []
        for j in range(len(positions)):

            features = {
                # Use the filename without the extension as the element name
                # 'name': name if tableData['Relevant Isotope'
                #                           ].iloc[j] == 'none' else tableData['Relevant Isotope'].iloc[j][2:-2],
                'name': interpName(name)['symbol'],
                'ID': peak_ids[j],
                'Position': round(positions[j], 6),
                'Height': round(heights[j], 6),
                'Distance': round(distances[j], 6),
                'Integral': round(integrals[j], 6),
                'Width': round(widths[j], 6),
                'Prominence': round(prominence[j], 6),
                'Prev Dip': round(prev_dips[j], 6),
                'Next Dip': round(next_dips[j], 6),
                'Tailedness': round(tailedness[j], 6),
                'Skewness': round(skewness[j], 6),
                'FWHM': round(fwhm[j], 6),
                'FW1QM': round(fw1qm[j], 6),
                'FW3QM': round(fw3qm[j], 6),
                # 'Mass': round(mass[j], 6),
                # 'Spin': spin[j]
                # 'Peak Distance Same ID': sameIDdistances[j]


            }
            feature_list.append(features)
        return feature_list


if __name__ == '__main__':

    with Pool() as p:
        for item in p.map(get_data, ELEMENTS):
            all_features += item
    # get_data(ELEMENTS[16])
    # # Create a DataFrame to store all extracted features
    # for data in ELEMENTS:
    #     get_data(data)
    features_df = pd.DataFrame(all_features)
    # Save the features to a CSV file
    features_df.to_csv('src/project/AI_TEST/peak_features_elements.csv', index=False)
