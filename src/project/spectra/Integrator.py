from __future__ import annotations
from pyparsing import Literal

import concurrent.futures
from pandas import DataFrame, read_csv
from scipy.interpolate import interp1d
from numpy import arange

from project.helpers.integration import integrate_simps
from project.helpers.resourcePath import resource_path
from project.settings import params


class IsotopeIntegrator:
    def __init__(self, parent):
        self.parent = parent
        self.name = parent.name
        self.distributions = parent.distributions
        self.plotType = parent.plotType
        self.isToF = parent.isToF
        self.isoGraphData: dict = self._load_and_preprocess_data()

    def _load_and_preprocess_data(self) -> dict[str: DataFrame]:
        # Load and preprocess data for all isotopes here
        # Store the preprocessed data in a dictionary or class variable
        isoTempGraphData = {
            name: read_csv(
                resource_path(f"{params['dir_graphData']}{name}_{self.name.split('_')[-1]}.csv"),
                names=['x', 'y'],
                header=None)
            for name, dist in self.distributions.items() if dist != 0}
        if self.isToF:
            isoGraphData = {}
            for name, data in isoTempGraphData.items():
                data['x'] = self.parent.energyToTOF(data['x'], length=self.parent.length)
                data.sort_values('x', ignore_index=True, inplace=True)
                isoGraphData[name] = data
        else:
            isoGraphData = isoTempGraphData
        return isoGraphData

    def _integrate_isotope(self, name, left_limit, right_limit, which):
        graph_data = self.isoGraphData[name]
        if left_limit == right_limit:
            return '[]', 0

        graph_data_interp = interp1d(graph_data.iloc[:, 0], graph_data.iloc[:, 1])
        x_range = arange(left_limit, right_limit, (right_limit - left_limit) / 100)

        integral = integrate_simps(DataFrame(list(zip(x_range, graph_data_interp(x_range))),
                                             columns=['x', 'y']),
                                   left_limit,
                                   right_limit,
                                   which) * self.distributions[name]

        return f"['{name}_{self.plotType}']", integral

    def peak_integral(self, left_limit: float, right_limit: float,
                      which: Literal['max', 'min'] = 'max') -> tuple[float, str]:
        if not hasattr(self, 'isoGraphData'):
            self._load_and_preprocess_data()

        with concurrent.futures.ThreadPoolExecutor() as executor:
            integrals = executor.map(self._integrate_isotope, self.isoGraphData.keys(),
                                     [left_limit] * len(self.isoGraphData),
                                     [right_limit] * len(self.isoGraphData),
                                     [which] * len(self.isoGraphData))

        integrals_dict = dict(integrals)
        total_integral = sum(integrals_dict.values())
        relevant_isotope = f"{max(integrals_dict, key=integrals_dict.get)}"

        return (total_integral, relevant_isotope)
