from project.myPyQt.PeriodicCell import ElementCell


class IsoCell(ElementCell):

    def __init__(self, isoList: list[dict[str]]):
        super(IsoCell, self).__init__()
        for iso in isoList:
            iso = ElementCell(iso['symbol'])
