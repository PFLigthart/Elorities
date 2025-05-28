# Elorities

A terminal-based priority ranking app using ELO ratings. Rank items within themed groups by comparing pairs.

## Features

- Create themed lists (goals, books, etc.)
- Rank items using head-to-head comparisons
- ELO rating system for fair rankings
- Visual rankings with loading bars
- Track statistics (wins, losses, plays)

## Installation

```bash
git clone https://github.com/PFLigthart/Elorities.git
cd Elorities
python ranker.py
```

## Usage

1. **Create a theme** - Start with a new category like "books" or "goals"
2. **Add items** - Add things you want to rank (max 100 characters each)
3. **Start ranking** - Compare pairs using `<` (left) or `>` (right) keys
4. **View rankings** - See your preferences visualized with dash bars

## Example

Ships with some example themes with entries, "books to buy" and "spending items"

```
Which is more important/better?
  <  Deep work
  >  Tools for thought

Your choice (</>): <

--- Rankings: goals ---
1. Deep work
   -------------------- (1032)
2. Tools for thought
   ------------ (968)
```

## Requirements

- Python 3.6+
- No external dependencies

## License

MIT
