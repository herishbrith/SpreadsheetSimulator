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

## Demo

```

            Welcome to Spreadsheet Simulator!

Use following commands to interact with the shell:
SET <cellId> <value>
GET <cellId>
QUIT
---

> SET A1 123
value: 123 set in cell: A1
> SET A2 123
value: 123 set in cell: A2
> SET A3 123
value: 123 set in cell: A3
> SET A4 =A1+A2+A3
value: =A1+A2+A3 set in cell: A4
> SET A5 =SUM(A1:A3)
value: =SUM(A1:A3) set in cell: A5
> GET A4
369
> GET A5
369
> SET A8 =A1+A2+A3+A4+A5
value: =A1+A2+A3+A4+A5 set in cell: A8
> GET A8
1107
> SET A3 =A1+A8
circular dependency found for cellId: A3
> GET A3

> GET A1
123
> GET A8
738
> SET A4 =A1&A2
value: =A1&A2 set in cell: A4
> GET A4
unsupported operation: & found
> GET A4
unsupported operation: & found
> GET A*
wrong command passed
> GET A8
unsupported operation: & found
> GET A1
123
> GET A2
123
> GET A3

> SET A3 123
value: 123 set in cell: A3
> SET A4 =SUM(A1:A3)
value: =SUM(A1:A3) set in cell: A4
> GET A4
369
> SET A8 =A1+A2+A3+A4
value: =A1+A2+A3+A4 set in cell: A8
> GET A8
738
>
```
