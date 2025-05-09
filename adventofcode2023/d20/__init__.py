import dataclasses
from dataclasses import dataclass
import math

from adventofcode2023.problem import Problem
from adventofcode2023.solution import Solution


@dataclass
class Pulse(object):
    source: str
    level: bool
    destination: str = ""
    
    def __str__(self) -> str:
        return f"{self.source} -{"high" if self.level else "low"}-> {self.destination}"
    
    def across(self, destinations: list[str]) -> list["Pulse"]:
        return [Pulse(self.source, self.level, dest) for dest in destinations]


@dataclass
class Module(object):
    name: str
    destinations: list[str] = dataclasses.field(default_factory=list)
    
    def add_source(self, source: str):
        pass
    
    def receive_and_send(self, pulse: Pulse) -> Pulse | None:
        return Pulse(self.name, pulse.level)
    
    def receive_and_send_across(self, pulse: Pulse) -> list["Pulse"]:
        pulse = self.receive_and_send(pulse)
        return [] if pulse is None else pulse.across(self.destinations)
    
    def reset(self):
        pass


@dataclass
class Button(Module):
    name: str = "button"
    destinations: list[str] = dataclasses.field(default_factory=lambda: ["broadcaster"])
    
    def receive_and_send(self, pulse: Pulse) -> Pulse | None:
        return Pulse(self.name, False)


@dataclass
class Broadcaster(Module):
    name: str = "broadcaster"
    
    def receive_and_send(self, pulse: Pulse) -> Pulse | None:
        return Pulse(self.name, pulse.level)


@dataclass
class FlipFlop(Module):
    state: bool = False
    
    def receive_and_send(self, pulse: Pulse) -> Pulse | None:
        if pulse is not None and pulse.level:
            return None
        self.state = not self.state
        return Pulse(self.name, self.state)
    
    def reset(self):
        self.state = False


@dataclass
class Conjunction(Module):
    memory: dict[str, bool] = dataclasses.field(default_factory=dict)
    
    def add_source(self, source: str):
        self.memory[source] = False
    
    def receive_and_send(self, pulse: Pulse) -> Pulse | None:
        self.memory[pulse.source] = pulse.level
        return Pulse(self.name, any(not level for level in self.memory.values()))
    
    def reset(self):
        for k in self.memory.keys():
            self.memory[k] = False


@dataclass
class Configuration(object):
    modules: dict[str, Module]
    
    @classmethod
    def from_str(cls, input: str) -> "Configuration":
        module_types: dict[str, str] = {"button": "button"}
        connections: dict[str, list[str]] = {"button": ["broadcaster"]}
        for line in input.splitlines():
            line = line.strip().split(" -> ")
            input = line[0]
            input_type = (
                input if input == "button" or input == "broadcaster" else (
                    "flipflop" if input[0] == "%" else (
                        "conjunction" if input[0] == "&" else "sink"
                    )
                )
            )
            if input_type == "flipflop" or input_type == "conjunction":
                input = input[1:]
            module_types[input] = input_type
            outputs = line[1].split(", ")
            for output in outputs:
                if output not in module_types:
                    module_types[output] = "sink"
            connections[input] = outputs
        modules: dict[str, Module] = {}
        for module_name, type in module_types.items():
            destinations = connections.get(module_name, [])
            match type:
                case "button": module = Button()
                case "broadcaster": module = Broadcaster(destinations=destinations)
                case "flipflop": module = FlipFlop(module_name, destinations)
                case "conjunction": module = Conjunction(module_name, destinations)
                case "sink": module = Module(module_name, destinations)
            modules[module_name] = module
        for module_name in module_types.keys():
            for destination in connections.get(module_name, []):
                modules[destination].add_source(module_name)
        return Configuration(modules)
    
    def reset(self):
        for module in self.modules.values():
            module.reset()
    
    def sources_of(self, dest: str) -> list[str]:
        return [src for src, mod in self.modules.items() if dest in mod.destinations]


@dataclass
class Manager(object):
    configuration: Configuration
    pulses: list[Pulse] = dataclasses.field(default_factory=list)
    frontier_index: int = 0
    
    def press_button(self):
        self.pulses.append(Pulse("button", False, "broadcaster"))
    
    def run_once(self) -> bool:
        if self.frontier_index >= len(self.pulses):
            return False
        pulse = self.pulses[self.frontier_index]
        pulses = self.configuration.modules[pulse.destination].receive_and_send_across(pulse)
        self.pulses.extend(pulses)
        self.frontier_index += 1
        return True
    
    def get_pulse_report(self) -> tuple[int, int]:
        """
        low, high
        """
        low, high = 0, 0
        for pulse in self.pulses:
            if pulse.level:
                high += 1
            else:
                low += 1
        return low, high


class Problem20(Problem):
    def __init__(self, configuration: Configuration):
        self.configuration = configuration
    
    @classmethod
    def from_str(cls, input: str) -> "Problem20":
        return Problem20(Configuration.from_str(input))


class Solution20(Solution):
    def p1(self, problem: Problem20, button_presses: int = 1000) -> int:
        problem.configuration.reset()
        manager = Manager(problem.configuration)
        for p in range(button_presses):
            manager.press_button()
            while manager.run_once():
                pass
        # print("\n".join(str(p) for p in manager.pulses))
        low, high = manager.get_pulse_report()
        return low * high
    
    def p2(self, problem: Problem20) -> int:
        problem.configuration.reset()
        final_conjunction = problem.configuration.sources_of("rx")[0]
        fc_inputs = set(problem.configuration.sources_of(final_conjunction))
        fc_inputs_first_seen: dict[str, int] = {a: 0 for a in fc_inputs}
        manager = Manager(problem.configuration)
        p = 0
        while len(fc_inputs) >= 1:
            p += 1
            manager.press_button()
            while manager.run_once():
                pass
            # get first instance of when each of the four inputs to the final
            # conjunction is high
            for pulse in manager.pulses:
                if pulse.source in fc_inputs and pulse.level:
                    fc_inputs_first_seen[pulse.source] = p
                    fc_inputs.remove(pulse.source)
            manager.pulses = []
            manager.frontier_index = 0
        return math.lcm(*fc_inputs_first_seen.values())