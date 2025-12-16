# Texas Hold'em Best Hand Quiz

A multiple choice quiz CLI program that tests knowledge of Texas Hold'em hand rankings.

## Features

- Interactive quiz with randomly generated hands
- Tests knowledge of poker hand rankings
- Color-coded card display
- Score tracking

## Requirements

- Python 3.8+

## Installation

Using Poetry (recommended):

```bash
poetry install
```

Or using pip:

```bash
pip install -r requirements.txt
```

## Usage

Run the quiz:

```bash
poetry run python poker_quiz.py
```

Or if using pip:

```bash
python poker_quiz.py
```

## Development

### Running Tests

```bash
poetry run pytest
```

### Linting

```bash
poetry run ruff check .
poetry run ruff format .
```

### Type Checking

```bash
poetry run mypy poker_quiz.py
```

## License

MIT

