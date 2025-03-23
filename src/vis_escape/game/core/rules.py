from abc import ABC, abstractmethod

from .context import GameContext


class TransitionRule(ABC):
    @abstractmethod
    def evaluate(self, context: GameContext) -> bool:
        pass


class HasItemRule(TransitionRule):
    def __init__(self, required_item: str):
        self._required_item = required_item

    def evaluate(self, context: GameContext) -> bool:
        print("REQUIRED ITEM: ", self._required_item)
        print("Inventory: ", context.player_inventory)
        return self._required_item in context.player_inventory

    def __str__(self) -> str:
        return f"HasItem({self._required_item})"


class TriggerActiveRule(TransitionRule):
    def __init__(self, trigger_name: str):
        self._trigger_name = trigger_name

    def evaluate(self, context: GameContext) -> bool:
        return context.triggers.get(self._trigger_name, False)

    def __str__(self) -> str:
        return f"TriggerActive({self._trigger_name})"


class AndRule(TransitionRule):
    def __init__(self, *rules: TransitionRule):
        self._rules = rules

    def evaluate(self, context: GameContext) -> bool:
        return all(rule.evaluate(context) for rule in self._rules)

    def __str__(self) -> str:
        rules_str = ", ".join(str(rule) for rule in self._rules)
        return f"And({rules_str})"


class AlwaysAllowRule(TransitionRule):
    def evaluate(self, context: GameContext) -> bool:
        return True

    def __str__(self) -> str:
        return "AlwaysAllow"


class NotRule(TransitionRule):
    def __init__(self, rule: TransitionRule):
        self._rule = rule

    def evaluate(self, context: GameContext) -> bool:
        return not self._rule.evaluate(context)

    def __str__(self) -> str:
        return f"Not({self._rule})"
