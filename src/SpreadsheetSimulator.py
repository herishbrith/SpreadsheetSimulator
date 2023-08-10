

class SpreadsheetSimulator:

    def __init__(self) -> None:
        self.grid = {}

    def setCellValue(self, cellId: str, value: any) -> None:
        self.grid[cellId] = value

    def getCellValue(self, cellId: str) -> any:
        storedValue = self.grid.get(cellId, None)
        displayValue = self.getDisplayValue(storedValue)
        return displayValue

    def getDisplayValue(self, storedValue) -> str:
        # if value in cell is found to be a number
        displayValue = None
        if storedValue:
            if storedValue.isnumeric():
                displayValue = storedValue
            elif storedValue.startswith("="):
                displayValue = self.evaluateValue(storedValue)
            else:
                displayValue = storedValue
        return displayValue

    def evaluateValue(self, storedValue):
        # TODO: evaluate value
        pass
