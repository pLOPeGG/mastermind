import itertools
import random

from collections import Counter
from typing import Iterable

import colorama
import tqdm

from mastermind import make_a_guess

BLUE = colorama.Fore.BLUE
RED = colorama.Fore.RED
GREEN = colorama.Fore.GREEN
YELLOW = colorama.Fore.YELLOW
MAGENTA = colorama.Fore.MAGENTA
CYAN = colorama.Fore.CYAN

WHITE = colorama.Fore.WHITE

colors = {0: BLUE, 1: RED, 2: GREEN, 3: YELLOW, 4: MAGENTA, 5: CYAN}

clues = [WHITE, RED]


def draw_secret(seed=None):
    if seed is not None:
        random.seed(seed)
    return random.choices(list(colors.keys()), k=4)


def show_comb(proposition: Iterable):
    print(
        # " ".join(colors[c] + "\u25C9" for c in proposition),
        " ".join(colors[c] + "o" for c in proposition),
        end=colorama.Style.RESET_ALL + "\n",
    )


def show_answer(n_correct, n_almost):
    print(
        " ".join(
            # itertools.chain([RED + "\u25C9"] * n_correct, [WHITE + "\u25C9"] * n_almost)
            itertools.chain([RED + "o"] * n_correct, [WHITE + "o"] * n_almost)
        ),
        end=colorama.Style.RESET_ALL + "\n",
    )


def fit(prop, secret, n_correct, n_almost):
    return get_clues(prop, secret) == (n_correct, n_almost)


def step(remain, secret, guess=None, *, solver="python"):
    if guess is None:
        if solver == "python":
            best_reduce = 0
            best_comb = None
            to_remove = []

            for g in tqdm.tqdm(itertools.product(colors, repeat=4)):
                worst_reduce = len(remain)
                worst_comb_secret = None

                for s in remain:
                    clues = get_clues(g, s)

                    curr_reduce = sum(1 for p in remain if not fit(p, g, *clues))

                    if curr_reduce < worst_reduce:
                        worst_reduce = curr_reduce
                        worst_comb_secret = (g, s)

                if worst_reduce > best_reduce:
                    best_reduce = worst_reduce
                    best_comb = worst_comb_secret[0]

            guess = best_comb

        elif solver == "rust":
            guess = make_a_guess(remain)

    remain = [p for p in remain if fit(p, guess, *get_clues(guess, secret))]

    return guess, remain


def get_clues(guess, secret):
    n_correct = sum(g == s for g, s in zip(guess, secret))
    n_almost = (
        sum(
            min(sum(1 for g in guess if g == c), sum(1 for s in secret if s == c))
            for c in colors
        )
        - n_correct
    )

    return n_correct, n_almost


def conclude(remain, secret, i):
    if len(remain) == 1:
        print(f"Solved ! in {i} steps. The secret was : ")
        show_comb(secret)
        print("Our final guess is : ")
        show_comb(next(iter(remain)))
    elif len(remain) > 1:
        print(f"We couldn't decide in {i} steps. {len(remain)} options remaining")

    else:
        print("Error :/")


def solve(secret, solver):

    remain = list(itertools.product(colors, repeat=4))
    print("The secret is : ")
    show_comb(secret)

    i = 1
    while True:
        if i == 1:
            guess, remain = step(remain, secret, [0, 0, 1, 1], solver=solver)
        else:
            guess, remain = step(remain, secret, solver=solver)

        n_correct, n_almost = get_clues(guess, secret)

        print(f"[{i}] New guess : ", end="")
        show_comb(guess)
        show_answer(n_correct, n_almost)

        if n_correct == len(secret):
            assert len(remain) == 1
            break

        i += 1

    conclude(remain, secret, i)
    return i


def main():
    secret = draw_secret()
    # secret = [1, 3, 2, 3]
    secret = random.choices(range(6), k=4)
    solve(secret, "rust")

    # print(max(solve(draw_secret(), "rust") for _ in range(100)))


if __name__ == "__main__":
    main()
