# Minesweeper AI

An AI that plays Minesweeper by **logical reasoning**: it works out which cells are safe and which hide mines, and only guesses when logic can't decide.

## How it thinks

Every time a cell is revealed, the AI adds a fact to its knowledge base, for example:

> "Of these 3 neighboring cells, exactly 1 is a mine."

It then reasons over everything it knows:

- **Simple deductions.** If the count is 0, all those cells are safe. If the count equals the number of cells, they are all mines.
- **Subset inference.** If one fact's cells are a subset of another's, the AI subtracts them to get a new fact. For example, `{A, B, C} = 1` and `{A, B} = 1` together mean `C` is safe.
- **Propagation.** Each newly found safe cell or mine is applied to every other fact, and the loop repeats until nothing new can be learned.

When it runs out of safe moves, it picks a random cell that isn't known to be a mine.

## Run it

```bash
pip install -r requirements.txt
python runner.py
```

Play yourself, or press **AI Move** to let the AI play.

> The game window expects `assets/fonts/OpenSans-Regular.ttf` and the images `assets/images/flag.png` and `assets/images/mine.png`. Add these files before launching.

## Built with

Python · Pygame
