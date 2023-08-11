

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
        self.performValidations(cellId)

    def getCellValue(self, cellId: str) -> any:
        """
        Method to get value of a cell.
        :params:
            cellId:                         cellId
        :return:
            value
        """
        self.performValidations(cellId)
        return self.getDisplayValue(cellId)

    def performValidations(self, cellId: str):
        try:
            self.checkForCircularDependency(cellId, set())
            self.checkForAggregationValidation(cellId)
        except UnsupportedOperationError as err:
            del self.grid[cellId]
            raise err

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
            # check if string format matches evaluation formula
            metadata = self.getEvaluationMetadata(string)
            if metadata is None:
                # check if string format matches aggregation formula
                metadata = self.getAggregationMetadata(string)
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
                # if match is not found, return
                return
        return {
            "type": "evaluation",
            "dependent_cells": dependentCells,
            "operators": operators
        }

    def getAggregationMetadata(self, string: str):
        """
        Method to generate metadata for a cell with aggregation formula in its value.
        :params:
            string:                         value of the cell
        :return:
            metadata as dict
        """
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
                "dependent_cells": SpreadsheetSimulator.getCellsToAggregate(
                    match.group(2), int(match.group(3)), int(match.group(5))
                )
            }
        return metadata

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
        # raise circular dependency error
        if typeOfCell == "evaluation" and cellId in dependentCells:
            raise UnsupportedOperationError(f"circular dependency found for cellId: {cellId}")
        dependentCells.add(cellId)
        # collect new dependent cells and recursively check if circular
        # dependency is detected
        newDependentCells = set(self.grid.get(cellId, {}).get("dependent_cells", []))
        for dependentCell in newDependentCells:
            self.checkForCircularDependency(dependentCell, dependentCells)

    def checkForAggregationValidation(self, cellId: str):
        """
        Method to check if dependent cells to be aggregated are all numbers.
        :params:
            cellId:                         cellId
        :return:
            None
        :raises:
            UnsupportedOperationError if value in a cell is found to be not a number.
        """
        typeOfCell = self.grid.get(cellId, {}).get("type", "number")
        if typeOfCell == "aggregation":
            dependentCells = self.grid[cellId]["dependent_cells"]
            for dependentCell in dependentCells:
                if self.grid.get(dependentCell, {}).get("type", "number") != "number":
                    raise UnsupportedOperationError(f"unsupported data found in: {dependentCell}")

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
        elif typeOfCell == "aggregation":
            displayValue = self.evaluateAggregatedValue(cellId)
        elif typeOfCell == "number" or typeOfCell == "string":
            displayValue = metadata["stored_value"]
        else:
            displayValue = ""
        return displayValue

    def evaluateValue(self, cellId: str) -> float:
        """
        Method to recursively find value of a given cellId for evaluation type.
        :params:
            cellId:                         cellId
        :return:
            evaluatedValue as float
        """
        metadata = self.grid[cellId]
        dependentCells = metadata["dependent_cells"]
        operators = ["+"] + metadata["operators"] # need to add "+" as first operation for addition to 0
        operationIndex = 0
        evaluatedValue = 0
        # for each of the dependent cells, get evaluated value recursively if required,
        # i.e. type is evaluation or aggregation
        # or else if type is number, use it for evaluation
        # or else if type is string, raise error
        # else the cell is blank and can be used as 0
        for dependentCell in dependentCells:
            newMetadata = self.grid.get(dependentCell, {})
            typeOfCell = newMetadata.get("type", "blank")
            if typeOfCell == "evaluation":
                value = self.evaluateValue(dependentCell)
            elif typeOfCell == "aggregation":
                value = self.evaluateAggregatedValue(dependentCell)
            elif typeOfCell == "number":
                value = int(newMetadata.get("stored_value", "0"))
            elif typeOfCell == "string":
                raise UnsupportedOperationError(f"cell {dependentCell} can't be evaluated")
            else:
                value = 0
            evaluatedValue = SpreadsheetSimulator.performEvaluation(evaluatedValue, value, operators[operationIndex])
            operationIndex += 1
        return evaluatedValue

    def evaluateAggregatedValue(self, cellId: str):
        """
        Method to recursively find value of a given cellId for aggregation type.
        :params:
            cellId:                         cellId
        :return:
            evaluatedValue as float
        """
        metadata = self.grid[cellId]
        dependentCells = metadata["dependent_cells"]
        cellValues = self.getCellValues(dependentCells)
        evaluatedValue = 0
        if metadata["op"] == "SUM":
            evaluatedValue = sum(cellValues)
        elif metadata["op"] == "AVG":
            evaluatedValue = sum(cellValues) / len(cellValues)
        elif metadata["op"] == "MUL":
            evaluatedValue = reduce((lambda m, n: m*n), cellValues)
        elif metadata["op"] == "MAX":
            evaluatedValue = max(cellValues)
        elif metadata["op"] == "MIN":
            evaluatedValue = min(cellValues)
        return evaluatedValue

    @staticmethod
    def performEvaluation(operand1, operand2, oper: str) -> any:
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

    @staticmethod
    def getCellsToAggregate(startCellCol, startCellRow, endCellRow) -> list:
        # traverse through all the cells defined in metadata
        # by incrementing row number in each iteration
        return [
            f"{startCellCol}{row}"
            for row in range(startCellRow, endCellRow+1)
        ]

    def getCellValues(self, cells):
        return [
            int(self.grid.get(cell, {}).get("stored_value", "0"))
            for cell in cells
        ]
