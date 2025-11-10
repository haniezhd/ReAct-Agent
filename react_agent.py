# ------------------- Imports -------------------
import json
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass
from abc import ABC, abstractmethod
import re
from colorama import Fore, Style, init
init(autoreset=True)
from ollama import chat
import tiktoken

# ------------------- Agent Prompt -------------------
AGENT_PROMPT = """You are an AI assistant who follows a step-by-step reasoning process to determine the best answer.
You think, take actions when needed, and refine your response based on observations.

You run in a loop of Thought → Action → PAUSE → Observation until you reach a Final Answer.
At the end of the loop, you must output a Final Answer.

Use Thought to reason about the current question.
Use Action to execute one of the available tools. Then return PAUSE.
Observation will be provided by the system after the Action is executed.

Your available tools are:
{tools}

### Rules:
1. For greetings or farewells, respond directly without using the Thought-Action loop.
2. For all other inputs, follow the Thought-Action loop to determine the best answer.
3. If the answer is already known internally, respond directly without using external tools.
4. Execute each action separately; do not combine multiple actions in one step.
5. Always provide a clear and complete Final Answer at the end.
6. After each Action, wait for the system to provide an Observation.
7. Use the calculator tool for all mathematical operations. Do not attempt to answer math questions directly.

### Always use this output format:
Thought: <your reasoning>
Action: <tool_name>: <input>
Final Answer: <answer>

### Action Format:
- General queries:  
  Action: <tool_name>: <query>
- Mathematical queries:  
  Action: calculator: {{"operation": "<operation_name>", "params": {{"a": <num>, "b": <num>}}}}
- Always use exact numbers from the question.
- Each operation (add, subtract, multiply, divide, power, modulus) must be called separately.
- Never include "Observation" yourself; the system will provide it.

### Examples:

1. Single-step calculation
Question: What is 5 + 7?
Thought: I need to add 5 and 7.
Action: calculator: {{"operation": "add", "params": {{"a": 5, "b": 7}}}}
PAUSE
Observation: calculator tool output -> 12
Final Answer: 5 + 7 = 12

2. Multi-step calculation
Question: Calculate (5 + 7) * 3
Thought: First, I need to add 5 and 7.
Action: calculator: {{"operation": "add", "params": {{"a": 5, "b": 7}}}}
PAUSE
Observation: calculator tool output -> 12
Thought: Now, I multiply the result by 3.
Action: calculator: {{"operation": "multiply", "params": {{"a": 12, "b": 3}}}}
PAUSE
Observation: calculator tool output -> 36
Final Answer: (5 + 7) * 3 = 36

3. Division example
Question: Divide 36 by 6
Thought: I need to divide 36 by 6.
Action: calculator: {{"operation": "divide", "params": {{"a": 36, "b": 6}}}}
PAUSE
Observation: calculator tool output -> 6
Final Answer: 36 / 6 = 6


4. Current time in Iran  
Question: What is the current time in Iran?  
Thought: I need the current date and time in Iran.  
Action: get_current_datetime_iran: ""  
PAUSE  
Observation: get_current_datetime_iran tool output -> <current Iranian date/time>  
Final Answer: The current time in Iran is <current Iranian date/time>.

---

5. Mock weather example  
Question: What’s the weather like in Paris today?  
Thought: I should call the mock_weather tool with the city parameter "Paris".  
Action: mock_weather: {"city": "Paris"}  
PAUSE  
Observation: mock_weather tool output -> "Cloudy, 18°C"  
Final Answer: The weather in Paris today is sunny with a temperature of 18°C.

---

6. Multi-step mixed example  
Question: What is the temperature in Paris, and what is (5 + 3)?  
Thought: First, I should get the weather for Paris.  
Action: mock_weather: {"city": "Paris"}  
PAUSE  
Observation: mock_weather tool output -> "Cloudy, 18°C"  
Thought: Now, I calculate 5 + 3.  
Action: calculator: {"operation": "add", "params": {"a": 5, "b": 3}}  
PAUSE  
Observation: calculator tool output -> 8  
Final Answer: The weather in Paris is cloudy and 18°C, and (5 + 3) = 8.
"""

# ------------------- Base Classes -------------------
@dataclass
class Message:
    role: str
    content: str

class BaseTool(ABC):
    """Abstract base class for tools."""
    def __init__(self, name: str, description: str):
        self._name = name.lower()
        self._description = description

    @property
    def name(self):
        return self._name

    @property
    def description(self):
        return self._description

    @abstractmethod
    def run(self, query: str) -> str:
        pass

# ------------------- Tools -------------------
class CalculatorTool(BaseTool):
    def __init__(self):
        super().__init__("calculator", "Performs basic math operations via JSON input")

    def add(self, a, b): return a + b
    def subtract(self, a, b): return a - b
    def multiply(self, a, b): return a * b
    def divide(self, a, b): return "Error: Division by zero" if b == 0 else a / b
    def power(self, a, b): return a ** b
    def modulus(self, a, b): return int(a) % int(b)

    def run(self, query):
        try:
            data = json.loads(query)
            op = data.get("operation")
            params = data.get("params", {})
            if not op or "a" not in params or "b" not in params:
                return json.dumps({"success": False, "result": None, "error": "Invalid JSON params"})
            if hasattr(self, op):
                result = getattr(self, op)(**params)
                if isinstance(result, str) and result.startswith("Error"):
                    return json.dumps({"success": False, "result": None, "error": result})
                return json.dumps({"success": True, "result": round(result,4) if isinstance(result,float) else result, "error": None})
            return json.dumps({"success": False, "result": None, "error": f"Unknown operation '{op}'"})
        except Exception as e:
            return json.dumps({"success": False, "result": None, "error": str(e)})

class GetCurrentTimeIran(BaseTool):
    def __init__(self):
        super().__init__("get_current_datetime_iran", "Returns current Iran time")
    def run(self, query=None):
        iran_time = datetime.now(timezone.utc) + timedelta(hours=3, minutes=30)
        return json.dumps({"success": True, "result": iran_time.strftime("%Y-%m-%d %H:%M:%S"), "error": None})

class GetWeatherTool(BaseTool):
    def __init__(self):
        super().__init__("get_weather", "Returns weather for a city")
    def run(self, city):
        fake_weather = {"tehran": "Sunny, 22°C", "paris": "Cloudy, 18°C", "london": "Rainy, 15°C"}
        city_lower = city.strip().lower()
        if city_lower in fake_weather:
            return json.dumps({"success": True, "result": f"{city_lower}: {fake_weather[city_lower]}", "error": None})
        return json.dumps({"success": False, "result": None, "error": "Weather data not available"})

# ------------------- ReActAgent -------------------
class ReActAgent:
    def __init__(self):
        self.messages = []
        self.tools = {}
        self.max_iterations = 10
        self.current_iteration = 0
        self.model = "llama3.2:1b"
        self.register_tools()
        self.system_prompt = AGENT_PROMPT.replace("{tools}", ", ".join(self.get_tools()))
        self.tokenizer = tiktoken.get_encoding("cl100k_base")

    def register_tools(self):
        self.tools["calculator"] = CalculatorTool()
        self.tools["get_current_datetime_iran"] = GetCurrentTimeIran()
        self.tools["get_weather"] = GetWeatherTool()

    def get_tools(self):
        return list(self.tools.keys())

    def add_message(self, role, content):
        self.messages.append(Message(role, content))

    def get_llm_response(self, prompt):
        chat_history = [{"role": m.role, "content": m.content} for m in self.messages]
        messages = [{"role": "system", "content": prompt}] + chat_history
        try:
            response = chat(model=self.model, messages=messages)
            return response["message"]["content"].strip()
        except Exception as e:
            return f"Error calling LLM: {str(e)}"

    def think(self):
        self.current_iteration += 1
        if self.current_iteration > self.max_iterations:
            print(f"{Fore.YELLOW}Reached max iterations. Stopping.{Style.RESET_ALL}")
            self.add_message("assistant", "Couldn't find a satisfactory answer.")
            return

        prompt = self.system_prompt + f"\nCurrent date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        response = self.get_llm_response(prompt)
        self.add_message("assistant", response)
        self.format_output(response)
        obs = self.determine_action(response)
        if obs is not None:
            self.system_prompt += f"\nObservation: {obs}"
            self.add_message("system", f"Observation: {obs}")
            print(f"{Fore.CYAN}[OBSERVATION]:{Style.RESET_ALL} {obs}\n")
            self.think()  # continue loop

    def determine_action(self, response):
        if "Final Answer:" in response: return None
        action_start = response.find("Action:")
        if action_start == -1:
            print(f"{Fore.YELLOW}No action found.{Style.RESET_ALL}")
            return None
        line = response[action_start:].split("\n")[0].strip()
        parts = line.replace("Action:", "").strip().split(":", 1)
        if len(parts) < 2: return None
        tool_name = parts[0].strip().lower()
        query = parts[1].strip()
        if tool_name == "calculator":
            try:
                data = json.loads(query)
                query = json.dumps(data)
            except:
                return None
        return self.execute_action(tool_name, query)

    def execute_action(self, tool_name, query):
        tool = self.tools.get(tool_name)
        if not tool:
            err = f"Tool '{tool_name}' not found"
            self.add_message("system", err)
            print(f"{Fore.RED}{err}{Style.RESET_ALL}")
            return None
        result = tool.run(query)
        try:
            data = json.loads(result)
            output = data.get("result", result)
        except:
            output = result
        obs = f"{tool_name} tool output -> {output}"
        return output

    def format_output(self, response):

        formatted = re.sub(r"Thought:", f"{Fore.MAGENTA}[THOUGHT]:{Style.RESET_ALL}", response)
        formatted = re.sub(r"Action:", f"{Fore.BLUE}[ACTION]:{Style.RESET_ALL}", formatted)
        formatted = re.sub(r"PAUSE", f"{Fore.YELLOW}[PAUSE]{Style.RESET_ALL}", formatted)
        formatted = re.sub(r"Observation:", f"{Fore.CYAN}[OBSERVATION]:{Style.RESET_ALL}", formatted)
        formatted = re.sub(r"Final Answer:", f"{Fore.RED}[FINAL ANSWER]:{Style.RESET_ALL}", formatted)

        print(f"{Fore.GREEN}[ASSISTANT]:{Style.RESET_ALL}\n{formatted}\n")


    def execute(self, query):
        self.current_iteration = 0
        self.add_message("user", query)
        self.think()
        # Return all messages since user input
        result = []
        for m in reversed(self.messages):
            if m.role == "user": break
            result.append(m)
        return result[::-1]

# ------------------- Main -------------------
if __name__ == "__main__":
    react_agent = ReActAgent()
    while True:
        query = input(f"{Fore.CYAN}USER:{Style.RESET_ALL} ").strip()
        if query.lower() in ["exit", "quit"]:
            print(f"{Fore.YELLOW}Exiting the ReAct agent.{Style.RESET_ALL}")
            break
        result = react_agent.execute(query)

        print("\n" + "="*60 + "\n")


