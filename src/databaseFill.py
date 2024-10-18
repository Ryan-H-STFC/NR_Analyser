import os
import pandas as pd
from project.spectra.SpectraDataStructure import SpectraData
from project.helpers.resourcePath import resource_path
from project.settings import params
from time import perf_counter

from multiprocessing import Pool

dist_filePaths: list[str] = [f for f in os.listdir(params['dir_distribution']) if f.endswith(".csv")]
defaultDistributions: dict = {}
for filepath in dist_filePaths:
    name = filepath[:-4]
    dist = pd.read_csv(resource_path(f"{params['dir_distribution']}{filepath}"), header=None)
    defaultDistributions[name] = dict({d[0]: d[1] for d in dist.values})


spectraNames: list = []
for file in os.listdir(f"{params['dir_graphData']}"):
    filename = os.fsdecode(file)
    if ".csv" not in filename[-4:]:
        continue
    filename = filename[:-4]
    spectraNames.append(filename)

thresholds = params['threshold_exceptions']
exportDir = r'C:\Users\Ryanh\Desktop\Test DataBase'


def exportDatabaseValues(name):
    print(f"Starting - {name}")
    filepath = f"{params['dir_graphData']}{name}.csv"
    try:
        graphData = pd.read_csv(resource_path(filepath), header=None)
    except pd.errors.EmptyDataError:
        return
    split = name.split("-")
    if name.startswith("e"):
        dataSymbolSort = split[1]
        dataSymbol = dataSymbolSort[:-2]
    else:
        dataSymbol = split[1]

    threshold = thresholds.get(dataSymbol, {'n-tot': 100, 'n-g': 100})

    for tof in [False, True]:
        tableData = pd.DataFrame(
            columns=[
                "Rank by Integral",
                "TOF (us)" if tof else "Energy (eV)",
                "Rank by " + ("TOF" if tof else "Energy"),
                "Integral",
                "Peak Width",
                "Rank by Peak Width",
                "Peak Height",
                "Rank by Peak Height",
                "Relevant Isotope"
            ])
        spectra = SpectraData(name=name,
                              numPeaks=None,
                              tableDataMax=tableData,
                              tableDataMin=tableData,
                              graphData=graphData,
                              graphColour=(0, 0, 0),
                              isToF=tof,
                              defaultDist=defaultDistributions.get(name, None),
                              distributions=defaultDistributions.get(name, None),
                              isCompound=False,
                              isAnnotationsHidden=True,
                              thresholds=threshold,
                              updatingDatabase=True
                              )
        name = name.replace("element_", "").replace("-Energy", "").replace("-ToF", "")
        spectra.maxTableData[1:].to_csv(
            f'{exportDir}/Peak Information/{'TOF' if tof else 'Energy'}/{name}_tableData_max.csv', index=False)
        spectra.minTableData[1:].to_csv(
            f'{exportDir}/Peak Information/{'TOF' if tof else 'Energy'}/{name}_tableData_min.csv', index=False)

        pd.DataFrame(spectra.maxPeakLimitsX.values()
                     ).to_csv(f'{exportDir}/Peak Limit Information/{name}_max.csv',
                              header=False,
                              index=False)
        pd.DataFrame(spectra.minPeakLimitsX.values()
                     ).to_csv(f'{exportDir}/Peak Limit Information/{name}_min.csv',
                              header=False,
                              index=False)
    print(f"Finished - {name}\n")


if __name__ == "__main__":
    # for name in [name for name in spectraNames if 'Te' in name]:
    #     exportDatabaseValues(name)
    t1 = perf_counter()
    with Pool() as p:
        map = p.map(exportDatabaseValues, spectraNames)
        for item in map:
            pass
    t2 = perf_counter()
    print(f'\n\nFinished All - Elapsed Time: {t2 - t1}')
