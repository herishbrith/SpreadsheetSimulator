

from functools import reduce
import re

from UnsupportedOperationError import UnsupportedOperationError


ALLOWED_AGGREGATIONS = ["SUM", "MUL", "AVG", "MAX", "MIN"]


class SpreadsheetSimulator:

    def __init__(self) -> None:
        self.grid = {}

    def setCellValue(self, cellId: str, value: any) -> None:
        self.grid[cellId] = value

    def getCellValue(self, cellId: str) -> any:
        try:
            value = self.grid.get(cellId, None)
            display_value = self.getDisplayValue(value)
        except UnsupportedOperationError as err:
            display_value = err.message
        return display_value

    def getDisplayValue(self, storedValue: str) -> str:
        # if value in cell is found to be a number
        displayValue = None
        if storedValue:
            if storedValue.startswith("="):
                displayValue = self.evaluateValue(storedValue)
            else:
                displayValue = storedValue
        return displayValue

    def evaluateValue(self, storedValue: str):
        displayValue = self.checkIfAggregation(storedValue)
        return displayValue

    def checkIfAggregation(self, storedValue: str):
        operationMap = self.parseAggregatedCells(storedValue)
        displayValue = self.evaluateAggregatedValue(operationMap) \
            if operationMap else storedValue
        return displayValue

    def parseAggregatedCells(self, storedValue: str):
        allowedAggregatedString = "|".join(ALLOWED_AGGREGATIONS)
        regex = f"^=({allowedAggregatedString})" + "\(([A-Z]{1,2})(\d{1,2}):([A-Z]{1,2})(\d{1,2})\)$"
        match = re.search(regex, storedValue)
        operationMap = None
        if match and match.group(2) == match.group(4):
            operationMap = {
                "op": match.group(1),
                "start_cell_col": match.group(2),
                "start_cell_row": match.group(3),
                "end_cell_col": match.group(4),
                "end_cell_row": match.group(5),
            }
        return operationMap

    def evaluateAggregatedValue(self, operationMap: dict):
        cellValues = self.getCellValues(
            operationMap["start_cell_col"],
            operationMap["start_cell_row"],
            operationMap["end_cell_row"]
        )
        evaluatedValue = None
        if operationMap["op"] == "SUM":
            evaluatedValue = sum(cellValues)
        elif operationMap["op"] == "MUL":
            evaluatedValue = reduce((lambda m, n: m*n), cellValues)
        elif operationMap["op"] == "AVG":
            evaluatedValue = sum(cellValues) / len(cellValues)
        elif operationMap["op"] == "MAX":
            evaluatedValue = max(cellValues)
        elif operationMap["op"] == "MIN":
            evaluatedValue = min(cellValues)
        return evaluatedValue

    def getCellValues(self, cellCol, startCellRow, endCellRow) -> list:
        startCellRow = int(startCellRow)
        endCellRow = int(endCellRow)
        cellValues = []
        for row in range(startCellRow, endCellRow+1):
            cellId = f"{cellCol}{row}"
            cellValue = self.grid.get(cellId, "")
            if not cellValue.isnumeric():
                raise UnsupportedOperationError("invalid value found in cell")
            else:
                cellValues += [int(cellValue)]
        return cellValues
