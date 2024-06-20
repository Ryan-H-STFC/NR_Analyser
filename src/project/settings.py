from os import path


params = {
    # ? ------------------------------------------------------------------------------------------------------------
    # ?                                               Filepaths
    # ? ------------------------------------------------------------------------------------------------------------
    # Filepath for the src directory
    'dir_src': f"{path.dirname(path.dirname(__file__))}\\",
    # Filpath for the img directory
    'dir_img': f"{path.dirname(path.dirname(__file__))}\\img\\",
    # Filpath for the fonts directory
    'dir_fonts': f"{path.dirname(path.dirname(__file__))}\\fonts\\",
    # Filepath for the project directory
    'dir_project': f"{path.dirname(__file__)}\\",
    # Filepath for the data directory
    'dir_data': f"{path.dirname(__file__)}\\data\\",
    # Filepath for the Graph Data directory
    'dir_graphData': f"{path.dirname(__file__)}\\data\\Graph Data\\",
    # Filepath for the Compound Graph Data
    'dir_compoundGraphData': f"{path.dirname(__file__)}\\data\\Graph Data\\Compound Data\\",
    # Filepath for the distribution directory
    'dir_distribution': f"{path.dirname(__file__)}\\data\\Distribution Information\\",
    # Filepath for the Peak Information directory
    'dir_peakInfo': f"{path.dirname(__file__)}\\data\\Peak Information\\",
    # Filepath for the Peak Limit Information directory
    'dir_peakLimitInfo': f"{path.dirname(__file__)}\\data\\Peak Limit Information\\",

    # ? ------------------------------------------------------------------------------------------------------------
    # ?                                                Length
    # ? ------------------------------------------------------------------------------------------------------------

    'length': {"n-g": 22.804, "n-tot": 23.404},

    # ? ------------------------------------------------------------------------------------------------------------
    # ?                                          Threshold Exceptions
    # ? ------------------------------------------------------------------------------------------------------------
    'threshold_exceptions': {
        'Cu': (20, 4.3),
        'Fe': (50, 10.2),
        'Sn': (100, 21),
        'Ag': (100, 88),
        'Au': (100, 970),
        'Sb': (100, 124),
        'Zn': (100, 7.7),
        'As': (100, 268),
        'Mn': (100, 268),
        'Co': (100, 15),
        'In': (100, 18.5),
        'Hg': (100, 130),
        'Pb': (100, 7.4)
    },  # 'X' : (n-tot, n-g)

    # ? ------------------------------------------------------------------------------------------------------------
    # ?                                        Peak Detector Parameters
    # ? ------------------------------------------------------------------------------------------------------------
    'max_prominence': 5.0,
    # Prominence Factor, threshold for identifying
    'min_prominence': 0.1,
    # Height Threshold,
    'min_required_height': -99999999.0,

    # ? ------------------------------------------------------------------------------------------------------------
    # ?                                             Graph Settings
    # ? ------------------------------------------------------------------------------------------------------------
    # Maximum number of peak annotations per spectra.
    'max_annotations': 50,
    # Settings Related to the Grid
    'grid_settings': {
        "which": "major",
        "axis": "both",
        "color": "#444"
    },
    # ! ------------------------------------------------------------------------------------------------------------
    # !                                        Debug Settings (Developers)
    # ! ------------------------------------------------------------------------------------------------------------
    # Forces SpectraData init to recalculate limits and peak table data
    'updating_database': False,
    # Plots the smoothed graph data which the derivatives are calculated from, useful for debugging zero integrals.
    'show_smoothed': False,
    # Draws vertical lines where the graph has a zero derivative, green for peaks, red for dips
    'show_first_der': False,
    # Draws vertical lines where the graph has a point of inflection, zero second derivative, in blue
    'show_second_der': False,
}
