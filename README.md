# Garmin Workout Creator

Create Garmin Connect workouts from natural language descriptions using AI.

## Overview

This tool allows you to describe a workout in plain English and automatically generate a structured workout in your Garmin Connect account. It uses Claude AI to parse natural language and the unofficial Garmin Connect API to upload workouts.

## Features

- **Natural Language Parsing**: Describe workouts in free text (e.g., "5 minute warm up, 6x800m at 5k pace with 400m recovery")
- **Modular Architecture**: Separate parsing and upload modules for flexibility
- **Multiple Sports**: Support for running, cycling, swimming, and more
- **Complex Workouts**: Handles intervals, repeats, zones, and various targets
- **CLI Interface**: Easy-to-use command-line tool
- **Session Caching**: Saves Garmin authentication between sessions

## Architecture

The tool consists of two independent modules:

1. **workout_parser**: Converts natural language → JSON workout definition
2. **garmin_uploader**: Converts JSON workout definition → Garmin Connect workout

This separation allows you to:
- Use different parsing methods (LLM-based, rule-based, etc.)
- Manually edit JSON before uploading
- Integrate with other workout generation tools

## Installation

### Prerequisites

- Python 3.8 or higher
- Anthropic API key ([get one here](https://console.anthropic.com/))
- Garmin Connect account

### Install from source

```bash
# Clone the repository
git clone https://github.com/yourusername/garmin-workout-creator.git
cd garmin-workout-creator

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install the package
pip install -e .
```

### Set up API key

```bash
# Copy example env file
cp .env.example .env

# Edit .env and add your Anthropic API key
echo "ANTHROPIC_API_KEY=your_api_key_here" >> .env

# Or export directly
export ANTHROPIC_API_KEY='your_api_key_here'
```

## Usage

### Quick Start

Create and upload a workout in one command:

```bash
garmin-workout create "5 minute warm up, 6x800m at 5k pace with 400m recovery, 5 minute cool down"
```

### Command Reference

#### 1. Parse only (generate JSON)

```bash
garmin-workout parse "10 minute easy run, then 4x1 mile at threshold with 2 min recovery" -o workout.json
```

#### 2. Upload existing JSON

```bash
garmin-workout upload workout.json
```

#### 3. Create and upload (combined)

```bash
# With confirmation prompt
garmin-workout create "20 minute tempo run at 10k pace"

# Skip confirmation
garmin-workout create "3x5k at marathon pace with 3 minute recovery" --yes
```

#### 4. Validate JSON

```bash
garmin-workout validate workout.json
```

#### 5. List recent workouts

```bash
garmin-workout list-workouts --limit 5
```

#### 6. Logout

```bash
garmin-workout logout
```

## Workout Description Examples

### Simple Workouts

```bash
# Basic endurance run
garmin-workout create "30 minute easy run"

# Tempo run
garmin-workout create "10 minute warm up, 20 minutes at tempo pace, 5 minute cool down"
```

### Interval Workouts

```bash
# Classic intervals
garmin-workout create "5 min warmup, 6x800m at 5k pace with 400m recovery, 5 min cooldown"

# Mile repeats
garmin-workout create "10 minute easy, then 4x1 mile at threshold with 2 minute recovery"

# Pyramid workout
garmin-workout create "2 min warmup, 400m, 800m, 1200m, 800m, 400m all at 5k pace with 90 second recovery, 2 min cooldown"
```

### Cycling Workouts

```bash
# Power-based intervals
garmin-workout create "cycling: 15 min warmup, 5x5 minutes at FTP with 3 min recovery, 10 min cooldown"
```

### Swimming Workouts

```bash
# Pool swimming
garmin-workout create "swimming: 200m warmup, 10x100m at hard effort with 20 second rest, 200m cooldown"
```

## JSON Workout Schema

The tool uses a standardized JSON format for workouts:

```json
{
  "workout_name": "Morning Intervals",
  "sport_type": "running",
  "description": "Optional description",
  "steps": [
    {
      "step_id": 1,
      "step_type": "warmup",
      "duration_type": "time",
      "duration_value": 300,
      "duration_unit": "seconds",
      "target_type": "open",
      "target_value": null
    },
    {
      "step_id": 2,
      "step_type": "repeat",
      "repeat_count": 6,
      "steps": [
        {
          "step_id": 3,
          "step_type": "interval",
          "duration_type": "distance",
          "duration_value": 800,
          "duration_unit": "meters",
          "target_type": "pace",
          "target_value": {
            "min_pace": 240,
            "max_pace": 260,
            "unit": "seconds_per_km"
          }
        }
      ]
    }
  ]
}
```

### Field Specifications

**Sport Types**: `running`, `cycling`, `swimming`, `other`

**Step Types**: `warmup`, `cooldown`, `interval`, `recovery`, `rest`, `repeat`

**Duration Types**: `time`, `distance`, `lap_button`, `open`

**Target Types**: `open`, `pace`, `speed`, `heart_rate`, `cadence`, `power`

See `workout_parser/models.py` for complete schema definitions.

## Programmatic Usage

You can also use the modules directly in Python:

```python
from workout_parser import WorkoutParser
from garmin_uploader import GarminUploader

# Parse a workout
parser = WorkoutParser(method="llm", api_key="your-api-key")
workout_json = parser.parse_to_json("5 min warmup, 10x400m at 5k pace with 200m jog recovery")

# Upload to Garmin
uploader = GarminUploader()
result = uploader.upload_from_json(workout_json)
print(f"Workout URL: {result['url']}")
```

## Configuration

### Environment Variables

- `ANTHROPIC_API_KEY`: Required for parsing workouts
- `GARMIN_EMAIL`: Optional, Garmin Connect email
- `GARMIN_PASSWORD`: Optional, Garmin Connect password (not recommended)

### Credential Storage

Garmin credentials are cached in `~/.garmin/session.pkl` after first login. To clear:

```bash
garmin-workout logout
```

## How It Works

1. **Natural Language Input**: You describe your workout in plain English
2. **AI Parsing**: Claude AI converts the description to structured JSON
3. **Validation**: Pydantic validates the workout structure
4. **Transformation**: JSON is converted to Garmin Connect API format
5. **Upload**: Workout is uploaded via the unofficial Garmin API
6. **Confirmation**: You receive a link to view your workout

## Limitations

- Uses unofficial Garmin Connect API (subject to change)
- Pace estimates for terms like "5k pace" are generic (not personalized)
- Some advanced Garmin workout features may not be supported
- Requires internet connection for both parsing and uploading

## Troubleshooting

### "ANTHROPIC_API_KEY not set"

```bash
export ANTHROPIC_API_KEY='your-key-here'
```

### "Garmin login failed"

- Check your email and password
- Try logging out: `garmin-workout logout`
- Garmin may require 2FA - check your email for verification

### "Failed to parse workout"

- Make sure your workout description is clear
- Try simpler language
- Check the examples above for guidance

### "Import Error: No module named 'garth'"

```bash
pip install -r requirements.txt
```

## Development

### Project Structure

```
garmin-workout-creator/
├── workout_parser/          # Module 1: Natural language → JSON
│   ├── models.py           # Pydantic models
│   ├── llm_parser.py       # Claude AI integration
│   └── parser.py           # Main parser interface
├── garmin_uploader/         # Module 2: JSON → Garmin
│   ├── auth.py             # Garmin authentication
│   ├── transformer.py      # JSON → Garmin format
│   └── uploader.py         # Main uploader interface
├── cli.py                   # Command-line interface
├── requirements.txt         # Dependencies
└── setup.py                # Package configuration
```

### Running Tests

```bash
# Parse a workout without uploading
garmin-workout parse "test workout: 5 min easy" -o test.json

# Validate the JSON
garmin-workout validate test.json
```

### Adding New Parsing Methods

The architecture supports pluggable parsing methods:

```python
# In workout_parser/parser.py
class WorkoutParser:
    def __init__(self, method="llm", **kwargs):
        if method == "llm":
            self.parser = LLMWorkoutParser(...)
        elif method == "rule_based":  # Add new method
            self.parser = RuleBasedParser(...)
```

## Contributing

Contributions are welcome! Areas for improvement:

- Additional parsing methods (rule-based, other LLMs)
- Support for more workout types and features
- Better pace personalization
- Unit tests
- Documentation improvements

## License

MIT License - see LICENSE file for details

## Acknowledgments

- [Anthropic](https://www.anthropic.com/) for Claude AI
- [garth](https://github.com/matin/garth) for Garmin Connect API access
- Garmin Connect community for API documentation

## Disclaimer

This tool uses the unofficial Garmin Connect API and is not affiliated with or endorsed by Garmin. Use at your own risk. The API may change without notice.
