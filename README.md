# Ant Colony Simulation

A Python 3 Pygame project simulating ant colony behavior.

## Installation

1. Clone the repository
2. Create virtual environment and install dependencies:
   ```bash
   make install
   ```
   
   Or for development with testing tools:
   ```bash
   make install-dev
   ```

## Usage

Run the simulation:
```bash
make run
```

Or run directly:
```bash
python src/colony.py [num_food]
```

## Project Structure

- `src/colony.py` - Main simulation file
- `requirements.txt` - Python dependencies
- `README.md` - Project documentation

## Available Commands

- `make help` - Show all available commands
- `make venv` - Create virtual environment
- `make install` - Install dependencies
- `make install-dev` - Install dependencies with development tools
- `make run` - Run the simulation
- `make test` - Run tests
- `make lint` - Run code linting
- `make format` - Format code
- `make clean` - Clean generated files
- `make venv-clean` - Remove virtual environment 