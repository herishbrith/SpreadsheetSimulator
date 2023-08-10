

from functools import reduce
import re

from UnsupportedOperationError import UnsupportedOperationError


ALLOWED_AGGREGATIONS = ["SUM", "MUL", "AVG", "MAX", "MIN"]


class SpreadsheetSimulator:

    def __init__(self) -> None:
        self.grid = {}

    def setCellValue(self, cellId: str, value: any) -> None:
        """
        Method to set value of a cell.
        :params:
            cellId:                         cellId
            value:                          value to be stored in cell
        :return:
            None
        """
        self.grid[cellId] = self.generateMetadata(value)
        self.checkForCircularDependency(cellId, set())

    def getCellValue(self, cellId: str) -> any:
        """
        Method to get value of a cell.
        :params:
            cellId:                         cellId
        :return:
            value
        """
        self.checkForCircularDependency(cellId, set())
        return self.getDisplayValue(cellId)

    def generateMetadata(self, string: str) -> dict:
        """
        Method to generate metadata for a cell.
        :params:
            string:                         value of the cell
        :return:
            metadata as dict
        """
        metadata = {}
        if string.isnumeric():
            metadata = {"type": "number"}
        elif not string.startswith("="):
            metadata = {"type": "string"}
        else:
            metadata = self.getEvaluationMetadata(string)
            if metadata is None:
                metadata = {"type": "string"}
        metadata["stored_value"] = string
        return metadata

    def getEvaluationMetadata(self, string: str):
        """
        Method to generate metadata for a cell with evaluation formula in its value.
        :params:
            string:                         value of the cell
        :return:
            metadata as dict
        """
        dependentCells = []
        operators = []
        traverser = 1 # skip "=" sign in provided string
        while traverser < len(string):
            # match for cellId
            match = re.search("^([A-Z]{1,2}\d{1,2}).*$", string[traverser:])
            if match:
                # append to dependentCells
                dependentCell = match.group(1)
                dependentCells += [dependentCell]
                # increase traverser by length of dependentCell
                # if traverser is found to be at end of string, break
                traverser += len(dependentCell)
                if traverser >= len(string)-1: break
                # collect operator value and append to operators list
                # increase traverser by 1
                operator = string[traverser:traverser+1]
                operators += [operator]
                traverser += 1
            else:
                # if match is not found, raise error
                raise UnsupportedOperationError("format couldn't be parsed")
        return {
            "type": "evaluation",
            "dependent_cells": dependentCells,
            "operators": operators
        }

    def checkForCircularDependency(self, cellId: str, dependentCells: set):
        """
        Method to recursively check if circular dependency is detected
        in evaluation formula stored in a given cell.
        :params:
            cellId:                         cellId
            dependentCells:                 dependentCells set
        :return:
            None
        :raises:
            UnsupportedOperationError if circular dependency is detected.
        """
        typeOfCell = self.grid.get(cellId, {}).get("type", "number")
        # process metadata if only evaluation on cellId is required
        if typeOfCell == "evaluation":
            # raise circular dependency error
            if cellId in dependentCells:
                raise UnsupportedOperationError(f"circular dependency found for cellId: {cellId}")
            dependentCells.add(cellId)
            # collect new dependent cells and recursively check if circular
            # dependency is detected
            newDependentCells = set(self.grid.get(cellId).get("dependent_cells"))
            for dependentCell in newDependentCells:
                self.checkForCircularDependency(dependentCell, dependentCells)

    def getDisplayValue(self, cellId: str) -> str:
        """
        Method to get display value of a given cellId.
        :params:
            cellId:                         cellId
        :return:
            displayValue as string
        """
        metadata = self.grid.get(cellId, {})
        typeOfCell = metadata.get("type", "blank")
        if typeOfCell == "evaluation":
            displayValue = self.evaluateValue(cellId)
        elif typeOfCell == "number" or typeOfCell == "string":
            displayValue = metadata["stored_value"]
        else:
            displayValue = ""
        return displayValue

    def evaluateValue(self, cellId: str) -> float:
        """
        Method to recursively find value of a given cellId.
        :params:
            cellId:                         cellId
        :return:
            evaluatedValue as float
        """
        metadata = self.grid[cellId]
        dependentCells = metadata["dependent_cells"]
        operators = ["+"] + metadata["operators"]
        operationIndex = 0
        evaluatedValue = 0
        for dependentCell in dependentCells:
            newMetadata = self.grid.get(dependentCell, {})
            typeOfCell = newMetadata.get("type", "blank")
            if typeOfCell == "evaluation":
                value = self.evaluateValue(dependentCell)
            elif typeOfCell == "number":
                value = int(newMetadata.get("stored_value", "0"))
            elif typeOfCell == "string":
                raise UnsupportedOperationError(f"cell {dependentCell} can't be evaluated")
            else:
                value = 0
            evaluatedValue = SpreadsheetSimulator.performOperation(evaluatedValue, value, operators[operationIndex])
            operationIndex += 1
        return evaluatedValue

    @staticmethod
    def performOperation(operand1, operand2, oper: str) -> any:
        """
        Method to perform a given operation on provided two operands.
        :params:
            operand1:                       operand1
            operand2:                       operand2
            oper:                           operation
        :return:
            result
        """
        if oper == "+": result = operand1 + operand2
        elif oper == "-": result = operand1 - operand2
        elif oper == "*": result = operand1 * operand2
        elif oper == "/": result = operand1 / operand2
        else:
            raise UnsupportedOperationError(f"unsupported operation: {oper} found")
        return result

    def getAggregationMetadata(self, cellId: str, string: str):
        # check if string provided has supported aggregations defined
        allowedAggregatedString = "|".join(ALLOWED_AGGREGATIONS)
        regex = f"^=({allowedAggregatedString})" + "\(([A-Z]{1,2})(\d{1,2}):([A-Z]{1,2})(\d{1,2})\)$"
        match = re.search(regex, string)
        # construct metadata for aggregation
        metadata = None
        if match and match.group(2) == match.group(4):
            metadata = {
                "type": "aggregation",
                "op": match.group(1),
                "start_cell_col": match.group(2),
                "start_cell_row": match.group(3),
                "end_cell_col": match.group(4),
                "end_cell_row": match.group(5),
            }
        return metadata

    def evaluateValue2(self, string: str):
        # check if aggregation formula is provided
        displayValue = self.checkIfAggregation(string)
        # check if evaluation formula is provided
        if displayValue is None:
            displayValue = self.checkIfFunction(string)
        return displayValue if displayValue else string

    def checkIfAggregation(self, string: str):
        displayValue = None
        # parse stored value to collect aggregation metadata
        metadata = self.getAggregationMetadata(string)
        displayValue = self.evaluateAggregatedValue(metadata) if metadata else None
        return displayValue

    def evaluateAggregatedValue(self, metadata: dict):
        # get values in a list stored in cells
        cellValues = self.getCellValues(metadata)
        # evaluate value based on operation collected in metadata
        evaluatedValue = None
        if cellValues:
            if metadata["op"] == "SUM":
                evaluatedValue = sum(cellValues)
            elif metadata["op"] == "MUL":
                evaluatedValue = reduce((lambda m, n: m*n), cellValues)
            elif metadata["op"] == "AVG":
                evaluatedValue = sum(cellValues) / len(cellValues)
            elif metadata["op"] == "MAX":
                evaluatedValue = max(cellValues)
            elif metadata["op"] == "MIN":
                evaluatedValue = min(cellValues)
        return evaluatedValue

    def getCellValues(self, metadata) -> list:
        startCellCol = metadata["start_cell_col"]
        startCellRow = int(metadata["start_cell_row"])
        endCellRow = int(metadata["end_cell_row"])
        cellValues = []
        # traverse through all the cells defined in metadata
        # by incrementing row number in each iteration
        for row in range(startCellRow, endCellRow+1):
            cellValue = self.grid.get(f"{startCellCol}{row}", "")
            # if cell value is found to be not a number, return with empty list
            if not cellValue.isnumeric():
                cellValues = []
                break
            else:
                cellValues += [int(cellValue)]
        return cellValues
