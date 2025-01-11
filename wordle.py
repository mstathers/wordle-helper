import re
import sys
from typing import Counter
from blessed import Terminal

term = Terminal()

def main():
    """
    Help provide wordle guesses.
    """
    word_bank = generate_word_bank('word-bank.csv')

    # keep track of guesses
    guess_ledger = []


    # Provide instructions
    print("""Input each letter of your five-letter guess one at a time, pressing Enter after each letter. Repeating a letter cycles through the feedback colors:

    Press the letter once for gray (not in the word).
    Press the letter twice for yellow (in the word but wrong position).
    Press the letter three times for green (correct letter and position).
    Pressing the letter four times returns it to gray and restarts the cycle.

A complete guess must always contain five letters. Press Enter after all five letters to submit your guess.""")

    guesses = 0
    while guesses < 6:
        suggest_some_words(word_bank)

        guess_list = get_user_input(word_bank)


        guess_ledger = modify_guess_ledger(guess_ledger, guess_list)

        # Generate Regex patterns based on the guess ledger.
        re_pat = '^'
        yellow_pat = ''
        for guess_idx, guess in enumerate(guess_ledger):
            if guess_idx == 5:
                if guess:
                    yellow_pat = '[' + ''.join(guess) + ']'
            else:
                re_pat += '[' + ''.join(guess) + ']'
        re_pat += '$'

        # Apply the regex patterns to the word bank to trim it down.
        new_word_bank = {}
        for word, score in word_bank.items():
            if re.match(re_pat, word) and re.search(yellow_pat, word):
                new_word_bank[word] = score

        word_bank = new_word_bank

        guesses += 1


def generate_word_bank(input_file: str) -> dict[str, int]:
    """
    Take input file in, create a counter to see how often all letters are used,
    create a score for each word in the input file based on the frequency of
    letters used.
    Duplicate letters in a word are assinged half score for that letter. This
    is arbitrary, but I needed to lessen the score of words with duplicate
    letters. This is more of a wordle strategy decision.
    """
    with open(input_file, 'r', encoding='utf8') as fh:
        file = fh.read()
        cnt = Counter(file)
        words = file.splitlines()

    w_bank = {}
    for word in words:
        word_score = 0
        duplicate_detection = ""
        for letter in list(word):
            if letter in duplicate_detection:
                word_score += cnt[letter] / 2
            else:
                word_score += cnt[letter]

            duplicate_detection += letter

        #print(f"{word}: {word_score}")
        w_bank[word] = word_score


    return w_bank


def suggest_some_words(w_bank):
    """
    Find the three highest scoring words in the word bank and print them.
    """
    sorted_w_bank = sorted(w_bank.keys(), key=w_bank.get, reverse=True)

    print("\nWord suggestions:")

    if len(sorted_w_bank) > 3:
        print(f"{sorted_w_bank[0]}")
        print(f"{sorted_w_bank[1]}")
        print(f"{sorted_w_bank[2]}")
    elif len(sorted_w_bank) == 1:
        print(f"Congrats! Final guess: {sorted_w_bank[0]}")
        sys.exit()
    else:
        for word in sorted_w_bank:
            print(word)


def get_user_input(word_bank):
    """
    Ask user for input, make sure it's 5 characters long
    """
    colors = [term.normal, term.yellow, term.green]

    print("Please enter a word:")

    target = ''
    result_list = []
    with term.cbreak(), term.hidden_cursor():
        val = ''
        last_letter = ''
        color = 0
        while len(target) < 5:
            val = term.inkey()
            if val == '\n':
                if last_letter != '':
                    print(f"{term.move_right}", end='', flush=True)

                    target += last_letter

                    # make colors sane
                    if color == 2:
                        color_eng = 'green'
                    elif color == 1:
                        color_eng = 'yellow'
                    else:
                        color_eng = 'grey'


                    result_list.append([last_letter, color_eng])

                    last_letter = ''

            elif val == last_letter:
                # If the same letter typed out, rotate its color.
                if color < len(colors)-1:
                    color += 1
                else:
                    color = 0
                print(f"{term.move_left}{colors[color]}{val}{term.normal}", end='', flush=True)

            elif re.match('[a-z]', val):
                color = 0
                last_letter = val
                print(f"{term.move_left}{term.normal}{val}", end='', flush=True)
        print()

    while True:
        if target in word_bank:
            #valid_guess = True
            return result_list
        print("Sorry, that isn't a possible word.")
        return get_user_input(word_bank)

def modify_guess_ledger(ledger, guess):
    # init ledger
    if not ledger:
        ledger = [
            ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z'],
            ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z'],
            ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z'],
            ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z'],
            ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z'],
            set() #this one is for yellow guesses
            ]


    for idx_i, i in enumerate(guess):
        letter = i[0]
        color = i[1]

        # start with green
        if color == 'green':
            ledger[idx_i] = [letter]
        elif color == 'yellow':
            # Add letter to set of "yellow" letters
            ledger[5].add(letter)
            # Remove yellow letter from slot we found it in because we know
            # it's not there.
            try:
                ledger[idx_i].remove(letter)
            # Likely already removed it with an old guess
            except ValueError:
                pass
        else: # grey
            for j in range(0, 5):
                try:
                    ledger[j].remove(letter)
                # Likely already removed it with an old guess
                except ValueError:
                    pass

    return ledger


if __name__ == '__main__':
    main()
