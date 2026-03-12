#!/usr/bin/env python3
"""
Garmin Workout Creator CLI
Command-line interface for creating Garmin workouts from natural language
"""

import typer
import os
import json
from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax

from workout_parser import WorkoutParser
from garmin_uploader import GarminUploader

app = typer.Typer(
    name="garmin-workout-creator",
    help="Create Garmin workouts from natural language descriptions",
    add_completion=False
)
console = Console()


@app.command()
def parse(
    workout_text: str = typer.Argument(
        ...,
        help="Workout description in free text (quote if contains spaces)"
    ),
    output: Optional[Path] = typer.Option(
        None,
        "--output",
        "-o",
        help="Save JSON to file (defaults to output/workout.json)"
    ),
    method: str = typer.Option(
        "gemini",
        "--method",
        "-m",
        help="Parsing method: 'gemini' (free) or 'llm' (Claude)"
    ),
    api_key: Optional[str] = typer.Option(
        None,
        "--api-key",
        help="API key (Gemini: GOOGLE_API_KEY, Claude: ANTHROPIC_API_KEY)"
    ),
    name: Optional[str] = typer.Option(
        None,
        "--name",
        "-n",
        help="Override workout name"
    )
):
    """
    Parse a workout description into JSON format.

    Example:
        garmin-workout parse "5 minute warm up, 6x800m at 5k pace with 400m recovery, 5 minute cool down"
    """
    # Determine API key from environment if not provided
    if not api_key:
        if method == "gemini":
            api_key = os.getenv("GOOGLE_API_KEY")
            if not api_key:
                console.print("[red]Error: GOOGLE_API_KEY not set[/red]")
                console.print("Get a free key at: https://aistudio.google.com/apikey")
                console.print("Then set it with: export GOOGLE_API_KEY='your-key'")
                console.print("Or use: --api-key YOUR_KEY")
                raise typer.Exit(1)
        else:
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                console.print("[red]Error: ANTHROPIC_API_KEY not set[/red]")
                console.print("Set it with: export ANTHROPIC_API_KEY='your-key'")
                console.print("Or use: --api-key YOUR_KEY")
                raise typer.Exit(1)

    try:
        console.print(f"[cyan]Parsing workout with {method}...[/cyan]")
        parser = WorkoutParser(method=method, api_key=api_key)
        workout_json = parser.parse_to_json(workout_text)

        # Override workout name if provided
        if name:
            workout_data = json.loads(workout_json)
            workout_data["workout_name"] = name
            workout_json = json.dumps(workout_data, indent=2)
            console.print(f"[dim]Overriding workout name to: {name}[/dim]")

        # Save to file
        if not output:
            # Default to output directory with auto-generated name
            import datetime
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            output = Path(f"output/workout_{timestamp}.json")
            output.parent.mkdir(exist_ok=True)

        output.write_text(workout_json)
        console.print(f"[green]✓ Workout saved to {output}[/green]")

        # Also pretty print the JSON
        syntax = Syntax(workout_json, "json", theme="monokai", line_numbers=True)
        console.print(Panel(syntax, title="Parsed Workout", border_style="green"))

    except Exception as e:
        console.print(f"[red]✗ Parsing failed: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def upload(
    json_file: Path = typer.Argument(
        ...,
        help="Path to workout JSON file",
        exists=True
    ),
    email: Optional[str] = typer.Option(
        None,
        "--email",
        "-e",
        help="Garmin Connect email"
    ),
    password: Optional[str] = typer.Option(
        None,
        "--password",
        "-p",
        help="Garmin Connect password"
    )
):
    """
    Upload a workout JSON to Garmin Connect.

    Example:
        garmin-workout upload workout.json
    """
    try:
        console.print(f"[cyan]Reading workout from {json_file}...[/cyan]")

        uploader = GarminUploader()
        result = uploader.upload_from_file(str(json_file), email, password)

        if result["success"]:
            console.print(Panel(
                f"[green]✓ Workout uploaded successfully![/green]\n\n"
                f"Name: {result['workout_name']}\n"
                f"ID: {result['workout_id']}\n"
                f"URL: {result['url']}",
                title="Upload Success",
                border_style="green"
            ))
        else:
            console.print(f"[red]✗ Upload failed: {result['error']}[/red]")
            raise typer.Exit(1)

    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def create(
    workout_text: str = typer.Argument(
        ...,
        help="Workout description in free text"
    ),
    method: str = typer.Option(
        "gemini",
        "--method",
        "-m",
        help="Parsing method: 'gemini' (free) or 'llm' (Claude)"
    ),
    api_key: Optional[str] = typer.Option(
        None,
        "--api-key",
        help="API key (Gemini: GOOGLE_API_KEY, Claude: ANTHROPIC_API_KEY)"
    ),
    email: Optional[str] = typer.Option(
        None,
        "--email",
        "-e",
        help="Garmin Connect email"
    ),
    password: Optional[str] = typer.Option(
        None,
        "--password",
        "-p",
        help="Garmin Connect password"
    ),
    save_json: Optional[Path] = typer.Option(
        None,
        "--save-json",
        help="Save intermediate JSON to file"
    ),
    skip_confirm: bool = typer.Option(
        False,
        "--yes",
        "-y",
        help="Skip confirmation prompt"
    ),
    name: Optional[str] = typer.Option(
        None,
        "--name",
        "-n",
        help="Override workout name"
    )
):
    """
    Parse workout text and upload to Garmin (combined operation).

    Example:
        garmin-workout create "10 minute easy, then 4x1 mile at threshold with 2 minute recovery"
    """
    # Determine API key from environment if not provided
    if not api_key:
        if method == "gemini":
            api_key = os.getenv("GOOGLE_API_KEY")
            if not api_key:
                console.print("[red]Error: GOOGLE_API_KEY not set[/red]")
                console.print("Get a free key at: https://aistudio.google.com/apikey")
                console.print("Then set it with: export GOOGLE_API_KEY='your-key'")
                console.print("Or use: --api-key YOUR_KEY")
                raise typer.Exit(1)
        else:
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                console.print("[red]Error: ANTHROPIC_API_KEY not set[/red]")
                console.print("Set it with: export ANTHROPIC_API_KEY='your-key'")
                console.print("Or use: --api-key YOUR_KEY")
                raise typer.Exit(1)

    try:
        # Step 1: Parse
        console.print(f"[cyan]Step 1/2: Parsing workout with {method}...[/cyan]")
        parser = WorkoutParser(method=method, api_key=api_key)
        workout_json = parser.parse_to_json(workout_text)

        # Override workout name if provided
        if name:
            workout_data = json.loads(workout_json)
            workout_data["workout_name"] = name
            workout_json = json.dumps(workout_data, indent=2)
            console.print(f"[dim]Overriding workout name to: {name}[/dim]")

        # Display parsed workout
        syntax = Syntax(workout_json, "json", theme="monokai", line_numbers=False)
        console.print(Panel(syntax, title="Parsed Workout", border_style="cyan"))

        # Save JSON if requested
        if save_json:
            save_json.write_text(workout_json)
            console.print(f"[dim]Saved to {save_json}[/dim]")

        # Confirm upload
        if not skip_confirm:
            proceed = typer.confirm("\nUpload this workout to Garmin Connect?")
            if not proceed:
                console.print("[yellow]Upload cancelled[/yellow]")
                return

        # Step 2: Upload
        console.print("\n[cyan]Step 2/2: Uploading to Garmin Connect...[/cyan]")
        uploader = GarminUploader()
        result = uploader.upload_from_json(workout_json, email, password)

        if result["success"]:
            console.print(Panel(
                f"[green]✓ Workout created successfully![/green]\n\n"
                f"Name: {result['workout_name']}\n"
                f"ID: {result['workout_id']}\n"
                f"URL: {result['url']}",
                title="Success",
                border_style="green"
            ))
        else:
            console.print(f"[red]✗ Upload failed: {result['error']}[/red]")
            raise typer.Exit(1)

    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def validate(
    json_file: Path = typer.Argument(
        ...,
        help="Path to workout JSON file to validate",
        exists=True
    )
):
    """
    Validate a workout JSON file against the schema.

    Example:
        garmin-workout validate workout.json
    """
    try:
        workout_json = json_file.read_text()
        is_valid, error_msg = WorkoutParser.validate_json(workout_json)

        if is_valid:
            console.print(Panel(
                "[green]✓ Workout JSON is valid![/green]",
                title="Validation Success",
                border_style="green"
            ))
        else:
            console.print(Panel(
                f"[red]✗ Validation failed:[/red]\n\n{error_msg}",
                title="Validation Error",
                border_style="red"
            ))
            raise typer.Exit(1)

    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def logout():
    """
    Clear cached Garmin Connect session.

    Example:
        garmin-workout logout
    """
    try:
        uploader = GarminUploader()
        uploader.logout()
        console.print("[green]✓ Logged out successfully[/green]")
    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def list_workouts(
    limit: int = typer.Option(
        10,
        "--limit",
        "-n",
        help="Number of workouts to retrieve"
    ),
    email: Optional[str] = typer.Option(
        None,
        "--email",
        "-e",
        help="Garmin Connect email"
    ),
    password: Optional[str] = typer.Option(
        None,
        "--password",
        "-p",
        help="Garmin Connect password"
    )
):
    """
    List recent workouts from Garmin Connect.

    Example:
        garmin-workout list-workouts --limit 5
    """
    try:
        uploader = GarminUploader()
        uploader.client = uploader.auth.login(email, password)

        console.print(f"[cyan]Fetching {limit} most recent workouts...[/cyan]\n")
        workouts = uploader.get_workout_list(limit)

        for workout in workouts:
            workout_id = workout.get("workoutId")
            name = workout.get("workoutName", "Untitled")
            sport = workout.get("sportType", {}).get("sportTypeKey", "unknown")

            console.print(f"[green]{name}[/green]")
            console.print(f"  ID: {workout_id}")
            console.print(f"  Sport: {sport}")
            console.print(f"  URL: https://connect.garmin.com/modern/workout/{workout_id}\n")

    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")
        raise typer.Exit(1)


def main():
    """Entry point for the CLI"""
    app()


if __name__ == "__main__":
    main()
