board = ['1', '2', '3', '4', '5', '6', '7', '8', '9']
currentToken = 'X'
winningToken = ''
slotsFilled = 0


def printBoard():
    print("\n")
    print("%s|%s|%s" % (board[0], board[1], board[2]))
    print("-+-+-")
    print("%s|%s|%s" % (board[3], board[4], board[5]))
    print("-+-+-")
    print("%s|%s|%s" % (board[6], board[7], board[8]))


print('Tic-Tac-Toe Example')
print('Match three lines vertically, horizontally, or diagonally')
print('X goes first, then O')

while winningToken == '' and slotsFilled < 9:
    printBoard()

    pos = -1
    while (pos == -1):
        pos = int(input("\n%s's turn.  Where to? " % currentToken))
        if pos < 1 or pos > 9:
            pos = -1
            print("Invalid choice!  1-9 only.")
        else:
            pos = pos - 1
            if board[pos] == 'X' or board[pos] == 'O':
                pos = -1
                print("That spot has already been taken by %s!  Try again" % board[pos])

    board[pos] = currentToken
    slotsFilled += 1

    row1 = board[0] == currentToken and board[1] == currentToken and board[2] == currentToken
    row2 = board[3] == currentToken and board[4] == currentToken and board[5] == currentToken
    row3 = board[7] == currentToken and board[7] == currentToken and board[8] == currentToken

    col1 = board[0] == currentToken and board[3] == currentToken and board[6] == currentToken
    col2 = board[1] == currentToken and board[4] == currentToken and board[7] == currentToken
    col3 = board[2] == currentToken and board[5] == currentToken and board[8] == currentToken

    diag1 = board[0] == currentToken and board[4] == currentToken and board[8] == currentToken
    diag2 = board[2] == currentToken and board[4] == currentToken and board[6] == currentToken

    row = row1 or row2 or row3
    col = col1 or col2 or col3
    diag = diag1 or diag2

    if (row or col or diag):
        printBoard()
        print("Congratulations %s! You won!" % currentToken)

    if currentToken == 'X':
        currentToken = 'O'
    else:
        currentToken = 'X'

if slotsFilled == 9 and winningToken == '':
    print("As in life there is no winner.  All is for nought as these bytes drift into the void from which they came.")
