# Dialog-YML Example Project

[English](README.md) | [Русский](README.ru.md)

---

This is an example Telegram bot project built using the aiogram framework and the dialog-yml library, which allows defining dialog interfaces through YAML files.

## Description

The project demonstrates the capabilities of creating complex dialog interfaces for Telegram bots using a declarative approach through YAML configurations. Thanks to the dialog-yml library, all dialog logic is defined in YAML files, making the project more maintainable and flexible.

## Features

- Using YAML files to define dialog interfaces
- Support for various types of widgets:
  - Buttons and menus
  - Scrolling and lists
  - Selection elements
  - Calendars
  - Counters and progress bars
  - Combined widgets
  - Multi-step processes
  - Callback request handling
- Custom widgets (for example, custom calendar)
- Exception handling and recovery after bot restarts

## Architecture

- `main.py` - application entry point
- `src/bot.py` - main bot logic and dispatcher
- `src/data/*.yaml` - YAML files with dialog definitions
- `src/functions/*.py` - callback functions and handlers
- `src/functions/custom/*.py` - custom widgets and components

## Installation and Launch

1. Install dependencies:

```bash
uv sync
```

1. Create a `.env` file by copying from `.env.example` and add the bot token:

```bash
cp .env.example .env
```

1. Run the bot:

```bash
make run
```

## Available Commands

- `make run` - run the bot
- `make check` - code quality check
- `make format` - code formatting
- `make test` - run tests
- `make help` - display help information

## Dialog Structure

The project includes the following sections:

- Layout widgets - layout widgets
- Scrolling widgets - scrollable lists
- Selection widgets - selection elements
- Calendar widgets - calendars
- Counter and Progress - counters and progress
- Combining widgets - combined widgets
- Multiple steps - multi-step processes
- Callbacks - callback request handling

## Technologies

- [aiogram](https://github.com/aiogram/aiogram) - framework for creating Telegram bots
- [aiogram-dialog](https://github.com/Tishka17/aiogram_dialog) - library for creating dialog interfaces
- [dialog-yml](https://github.com/smkthat/dialog-yml) - library for defining dialogs through YAML
- [Ruff](https://github.com/astral-sh/ruff) - fast Python code linter and formatter
- [uv](https://github.com/astral-sh/uv) - fast package manager for Python

## Project Structure

```bash
├── .env.example          # Environment variables file example
├── .gitignore           # Git ignore rules
├── Makefile             # Build and run scripts
├── README.md            # Project documentation (in English)
├── README.ru.md         # Документация проекта (на русском)
├── main.py              # Entry point
├── pyproject.toml       # Project configuration and dependencies
├── src/
│   ├── bot.py           # Main bot logic
│   ├── data/            # YAML files with dialog definitions
│   └── functions/       # Event handling functions
└── tests/               # Tests (stub)
```
