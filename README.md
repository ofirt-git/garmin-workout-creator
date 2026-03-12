# Garmin Workout Creator

Create Garmin Connect workouts from natural language descriptions using AI.

## Overview

This tool allows you to describe a workout in plain English and automatically generate a structured workout in your Garmin Connect account. It uses AI (Google Gemini by default, or Claude AI) to parse natural language and the unofficial Garmin Connect API to upload workouts.

## Features

- **Natural Language Parsing**: Describe workouts in free text (e.g., "5 minute warm up, 6x800m at 5k pace with 400m recovery")
- **Multiple AI Backends**: Use Google Gemini (free, default) or Claude AI for parsing
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
- Use different parsing methods (Google Gemini, Claude AI, etc.)
- Manually edit JSON before uploading
- Integrate with other workout generation tools

## Installation

### Prerequisites

- Python 3.8 or higher
- Google API key for Gemini ([get one free here](https://aistudio.google.com/apikey)) OR
- Anthropic API key for Claude ([get one here](https://console.anthropic.com/))
- Garmin Connect account

### Install from source

```bash
# Clone the repository
git clone https://github.com/yourusername/garmin-workout-creator.git
cd garmin-workout-creator

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install the package (this installs all dependencies and creates the garmin-workout command)
pip install -e .
```

**Important**: The `pip install -e .` command is required to create the `garmin-workout` CLI command. Without this step, the command won't be available in your terminal.

**Verify Installation**

After installing, verify the command is available:
```bash
garmin-workout --help
```

You should see the list of available commands. If you get "command not found", the Python bin directory may not be in your PATH. Try one of these solutions:

**Option A: Add Python bin to PATH** (recommended)
```bash
# Find where it was installed
pip show garmin-workout-creator | grep Location

# Add to PATH (adjust path based on above output)
export PATH="/Library/Frameworks/Python.framework/Versions/3.14/bin:$PATH"

# Or add to your shell profile (.bashrc, .zshrc, etc.)
echo 'export PATH="/Library/Frameworks/Python.framework/Versions/3.14/bin:$PATH"' >> ~/.zshrc
```

**Option B: Use with python -m**
```bash
python -m cli parse "your workout description"
```

**Option C: Use the full path**
```bash
# Find the command location
find /Library/Frameworks/Python.framework -name "garmin-workout" 2>/dev/null
# Then use the full path
/Library/Frameworks/Python.framework/Versions/3.14/bin/garmin-workout --help
```

**Alternative: Run without installation**

If you prefer not to install the package, you can run it directly with Python:
```bash
# Install dependencies only
pip install -r requirements.txt

# Run commands using python cli.py instead of garmin-workout
python cli.py parse "your workout description"
python cli.py create "your workout description"
```

### Set up API key

**Option 1: Google Gemini (Free, Default)**

```bash
# Copy example env file
cp .env.example .env

# Edit .env and add your Google API key
# Open .env in your editor and set: GOOGLE_API_KEY=your_api_key_here

# Or add it via command line
echo "GOOGLE_API_KEY=your_api_key_here" >> .env
```

The `.env` file will be automatically loaded when you run commands. Alternatively, you can export it directly in your shell:
```bash
export GOOGLE_API_KEY='your_api_key_here'
```

**Option 2: Claude AI**

```bash
# Add Anthropic API key to .env
# Open .env and add: ANTHROPIC_API_KEY=your_api_key_here

# Or add it via command line
echo "ANTHROPIC_API_KEY=your_api_key_here" >> .env
```

The `.env` file will be automatically loaded. Alternatively, export it directly:
```bash
export ANTHROPIC_API_KEY='your_api_key_here'
```

## Usage

### Quick Start

Create and upload a workout in one command (uses Google Gemini by default):

```bash
garmin-workout create "5 minute warm up, 6x800m at 5k pace with 400m recovery, 5 minute cool down"
```

To use Claude AI instead:

```bash
garmin-workout create "5 minute warm up, 6x800m at 5k pace with 400m recovery, 5 minute cool down" --method llm
```

### Command Reference

#### 1. Parse only (generate JSON)

```bash
# Uses Gemini by default, saves to output/workout_TIMESTAMP.json
garmin-workout parse "10 minute easy run, then 4x1 mile at threshold with 2 min recovery"

# Specify output file
garmin-workout parse "10 minute easy run, then 4x1 mile at threshold with 2 min recovery" -o workout.json

# Use Claude AI instead
garmin-workout parse "10 minute easy run, then 4x1 mile at threshold with 2 min recovery" --method llm
```

#### 2. Upload existing JSON

```bash
garmin-workout upload workout.json
```

#### 3. Create and upload (combined)

```bash
# With confirmation prompt (uses Gemini by default)
garmin-workout create "20 minute tempo run at 10k pace"

# Skip confirmation
garmin-workout create "3x5k at marathon pace with 3 minute recovery" --yes

# Use Claude AI
garmin-workout create "20 minute tempo run at 10k pace" --method llm

# Override workout name
garmin-workout create "20 minute tempo run" --name "Tuesday Tempo"
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

# Parse a workout with Gemini (default)
parser = WorkoutParser(method="gemini", api_key="your-google-api-key")
workout_json = parser.parse_to_json("5 min warmup, 10x400m at 5k pace with 200m jog recovery")

# Or use Claude AI
parser = WorkoutParser(method="llm", api_key="your-anthropic-api-key")
workout_json = parser.parse_to_json("5 min warmup, 10x400m at 5k pace with 200m jog recovery")

# Upload to Garmin
uploader = GarminUploader()
result = uploader.upload_from_json(workout_json)
print(f"Workout URL: {result['url']}")
```

## Configuration

### Environment Variables

- `GOOGLE_API_KEY`: Required for Gemini parsing (default method)
- `ANTHROPIC_API_KEY`: Required for Claude AI parsing (when using `--method llm`)
- `GARMIN_EMAIL`: Optional, Garmin Connect email
- `GARMIN_PASSWORD`: Optional, Garmin Connect password (not recommended)

### Credential Storage

Garmin credentials are cached in `~/.garmin/session.pkl` after first login. To clear:

```bash
garmin-workout logout
```

## How It Works

1. **Natural Language Input**: You describe your workout in plain English
2. **AI Parsing**: Google Gemini (or Claude AI) converts the description to structured JSON
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

### "GOOGLE_API_KEY not set"

```bash
export GOOGLE_API_KEY='your-key-here'
# Get a free key at: https://aistudio.google.com/apikey
```

### "ANTHROPIC_API_KEY not set" (when using --method llm)

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

### Import errors

```bash
# Install all required dependencies
pip install -r requirements.txt

# If google-genai is missing:
pip install google-genai

# If garth is missing:
pip install garth
```

## Development

### Project Structure

```
garmin-workout-creator/
├── workout_parser/          # Module 1: Natural language → JSON
│   ├── models.py           # Pydantic models
│   ├── gemini_parser.py    # Google Gemini integration
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
    def __init__(self, method="gemini", **kwargs):
        if method == "gemini":
            self.parser = GeminiWorkoutParser(...)
        elif method == "llm":
            self.parser = LLMWorkoutParser(...)
        elif method == "rule_based":  # Add new method
            self.parser = RuleBasedParser(...)
```

## Contributing

Contributions are welcome! Areas for improvement:

- Additional parsing methods (rule-based, other LLMs like OpenAI)
- Support for more workout types and features
- Better pace personalization
- Unit tests
- Documentation improvements

## License

MIT License - see LICENSE file for details

## Acknowledgments

- [Google](https://ai.google.dev/) for Gemini API
- [Anthropic](https://www.anthropic.com/) for Claude AI
- [garth](https://github.com/matin/garth) for Garmin Connect API access
- Garmin Connect community for API documentation

## Disclaimer

This tool uses the unofficial Garmin Connect API and is not affiliated with or endorsed by Garmin. Use at your own risk. The API may change without notice.
