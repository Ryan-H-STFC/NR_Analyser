from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.backend_bases import NavigationToolbar2


class NavigationBar(NavigationToolbar):
    def __init__(self, canvas_, parent_):
        toolitems = [*NavigationToolbar2.toolitems]
        toolitems.insert(
            # Add 'customize' action after 'subplots'
            [name for name, *_ in toolitems].index("Subplots") + 1,
            ("Customize", "Edit axis, curve and image parameters",
             "qt4_editor_options", "edit_parameters"))

    def configure_subplots(self):
        return super().configure_subplots()
