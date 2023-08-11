# SpreadsheetSimulator

## How to run?
- Clone the public repo locally
- Navigate to root folder in the repo
- Execute command `python main.py` and the program will open an interactive shell with details mentioned on how to interact with it

## Supported commands

### QUIT
- This command can be issued at any time and the program will exit

### GET <cellId>
- This command can be used to fetch value stored in a given cellId

### SET <cellId> <value>
- This command can be used to store value in provided cellId

## Grid dimensions
- Currently the grid supports:
    - max col number of ZZ (i.e. A to ZZ as in Excel sheet)
    - max row number of 2 digits (i.e. 99)

- These parameters are configurable and can be changed before starting script.

## Type of values that can be stored
- Currently the grid supports following 4 types of values:
    - `evaluation`: Cells are stored with an operator in between. This `evaluation` doesn't pertain to BODMAS rule. It processes data from left to right. Supported operations are: "+", "-", "*" and "/".
    e.g.
    ```
    > SET A8 =A1+A2+A3-A6*A4
    ```
    - `aggregation`: Cells are stored with aggregation formula associated with them. Supported aggregation functions are: SUM, AVG, MUL, MAX and MIN.
    e.g.
    ```
    > SET A8 =SUM(A1:A5)
    ```
    Note: To perform `aggregation` function on a range of cells, dependent cells must all be numbers and should be in one column.
    - `number`: number
    - `string`: anything other than above 3 is considered as string

    Note: During `evaluation`, `aggregated` dependent cells are allowed.
    e.g.
    ```
    > SET A1 123
    > SET A2 123
    > SET A3 123
    > SET A4 =SUM(A1:A3)
    > SET A8 =A1+A2+A3+A4
    > GET A8
    738
    ```
