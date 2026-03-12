# Quick Start Guide

## Installation (5 minutes)

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -e .
   ```

2. **Set up your Anthropic API key**
   ```bash
   export ANTHROPIC_API_KEY='your-api-key-here'
   ```

3. **Test the installation**
   ```bash
   python cli.py --help
   ```

## Your First Workout (2 minutes)

### Option 1: Parse Only (no Garmin account needed)

```bash
python cli.py parse "5 minute warm up, 6x800m at 5k pace with 400m recovery, 5 minute cool down" -o my_workout.json
```

This will create a JSON file you can inspect.

### Option 2: Full Workflow (requires Garmin account)

```bash
python cli.py create "10 minute easy run, then 4x1 mile at threshold with 2 minute recovery"
```

You'll be prompted for:
1. Garmin email and password (first time only)
2. Confirmation before uploading

That's it! Your workout will be in Garmin Connect.

## Common Use Cases

### Create a Simple Run
```bash
python cli.py create "30 minute easy run"
```

### Create Interval Workout
```bash
python cli.py create "5 min warmup, 8x400m at 5k pace with 90 second recovery, 5 min cooldown"
```

### Save JSON for Later
```bash
python cli.py parse "20 minute tempo run" -o tempo.json
python cli.py upload tempo.json  # Upload later
```

### Validate a JSON File
```bash
python cli.py validate examples/interval_workout.json
```

## Troubleshooting

**"Command not found: garmin-workout"**
- The package entry point is `cli.py`, use: `python cli.py` instead

**"ANTHROPIC_API_KEY not set"**
- Run: `export ANTHROPIC_API_KEY='your-key'`

**"Failed to parse workout"**
- Try simpler language or check examples in README.md

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Check [examples/interval_workout.json](examples/interval_workout.json) for JSON format
- Explore all CLI commands: `python cli.py --help`
