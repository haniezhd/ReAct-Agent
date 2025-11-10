# ReAct-Agent
Intelligent reasoning agent using ReAct

A Python-based ReAct agent that follows step-by-step reasoning to answer questions using tools like a calculator, current time in Iran, and mock weather data.

## Features

- Step-by-step reasoning using **Thought → Action → PAUSE → Observation → Final Answer** loop.
- Supports **multi-step calculations** with automatic tool handling.
- Includes tools:
  - `calculator`: addition, subtraction, multiplication, division, power, modulus.
  - `get_current_datetime_iran`: returns current date and time in Iran.
  - `get_weather`: returns mock weather data for predefined cities.
- Handles errors gracefully, including invalid tool calls or JSON input.

## Getting Started

1. Clone or download the repository.
2. Install dependencies (if any, e.g., `colorama`, `tiktoken`, `ollama` client).
3. Run the agent:

```bash
python react_agent.py
