import random


def word_puzzle_game():
    words = ["python", "programming", "puzzle", "computer", "algorithm", "function", "variable", "database"]
    word = random.choice(words)
    guessed = ["_"] * len(word)
    wrong_guesses = []
    attempts = 6

    print("Welcome to Word Puzzle Game!")
    print("Guess one letter or try the full word.")
    print("If a full-word guess has letters in the correct position, they stay revealed.")
    print(f"Word: {' '.join(guessed)}")

    while attempts > 0 and "_" in guessed:
        guess = input("Enter a letter or full-word guess: ").strip().lower()

        if not guess:
            print("Please enter something.")
            continue

        if len(guess) == 1:
            if guess in wrong_guesses or guess in guessed:
                print("Already guessed that letter!")
                continue

            if guess in word:
                found_positions = []
                for i, letter in enumerate(word):
                    if letter == guess:
                        guessed[i] = guess
                        found_positions.append(i + 1)

                print(f"Correct! The letter '{guess}' is right at position(s): {', '.join(map(str, found_positions))}.")
                print(f"Word: {' '.join(guessed)}")
            else:
                wrong_guesses.append(guess)
                attempts -= 1
                print(f"Wrong letter! Attempts left: {attempts}. Wrong guesses: {', '.join(wrong_guesses)}")
            continue

        if len(guess) != len(word):
            print(f"Your full-word guess must be {len(word)} letters long.")
            continue

        if guess == word:
            guessed = list(word)
            print(f"Perfect! You guessed the whole word: {word}")
            break

        newly_revealed = []
        for i, letter in enumerate(guess):
            if letter == word[i] and guessed[i] == "_":
                guessed[i] = letter
                newly_revealed.append(f"{letter} at position {i + 1}")

        attempts -= 1

        if newly_revealed:
            print("Nice try! You got some letters in the correct place:")
            print(", ".join(newly_revealed))
            print("These letters will stay visible in the next attempts.")
        else:
            print("No letters matched in the correct position this time.")

        print(f"Word: {' '.join(guessed)}")
        print(f"Attempts left: {attempts}")

    if "_" not in guessed:
        print(f"You won! The word was: {word}")
    else:
        print(f"Game Over! The word was: {word}")

if __name__ == "__main__":
    word_puzzle_game()