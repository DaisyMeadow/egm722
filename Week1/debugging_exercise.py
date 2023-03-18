import random

# pick a random number for the user to guess
rand = random.randint(1, 20)

print('Guess a number between 1 and 20.')  # tell user to guess number between 1 and 20
guess = int(input())  # number needs to be an integer

numberGuess = int(1)  # create integer variable that stores number of guesses

while guess != rand:  # if the guess is not equal to the random number, you have to guess again
    if guess > rand:  # if the guess is too high, tell the user.
        print('Too high. Guess again.')
    else:  # if the guess is too low, tell the user.
        print('Too low. Guess again.')

    print('Enter a new guess: ')
    guess = int(input())
    numberGuess = numberGuess + 1  # number of guesses incremented by 1

if numberGuess == 1:  # If user guesses number straight away print below
    print('You got it in 1 guess, WOW! The number was {}'.format(rand))

else:  # Else print below
    print('You got it in {} guesses! The number was {}'.format(numberGuess, rand))