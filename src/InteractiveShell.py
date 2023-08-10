
import re

from src.SpreadsheetSimulator import SpreadsheetSimulator


INTRO_MESSAGE = """
            Welcome to Spreadsheet Simulator!

Use following commands to interact with the shell:
SET <cellId> <value>
GET <cellId>
QUIT
---\n
"""
ERROR_MESSAGE = "wrong command passed"
EXIT_MESSAGE = "exiting"


class InteractiveShell:

    def __init__(self) -> None:
        # initiate SpreadsheetSimulator
        self.spreadsheet = SpreadsheetSimulator()
        self.parsedInputGet = None
        self.parsedInputSet = None

    def validateInput(self, input_str):
        # process QUIT command
        if input_str == "QUIT":
            print(EXIT_MESSAGE)
            exit(0)
        # validate if GET command was invoked
        isMatchGet = re.search("^GET ([A-Z]{1,2}\d{1,2})$", input_str)
        if isMatchGet:
            self.parsedInputGet = isMatchGet
            return
        # validate if SET command was invoked
        isMatchSet = re.search("^SET ([A-Z]{1,2}\d{1,2}) (.*)$", input_str)
        if isMatchSet:
            self.parsedInputSet = isMatchSet
            return
        # return error message
        return ERROR_MESSAGE

    def handleInput(self):
        message = None
        # process GET command
        if self.parsedInputGet:
            cellId = self.parsedInputGet.group(1)
            message = self.spreadsheet.getCellValue(cellId)
        # process SET command
        elif self.parsedInputSet:
            cellId = self.parsedInputSet.group(1)
            value = self.parsedInputSet.group(2)
            self.spreadsheet.setCellValue(cellId, value)
            message = f"value: {value} set in cell: {cellId}"
        else:
            return
        return message

    def displayMessage(self, message):
        print(f"{message}\n>")

    def clearVars(self):
        self.parsedInputGet = None
        self.parsedInputSet = None

    def startShell(self):
        # print intro
        print(INTRO_MESSAGE)
        # run interactive shell
        while True:
            message = self.validateInput(input().strip())
            if message == None:
                message = self.handleInput()
            self.displayMessage(message)
            self.clearVars()
