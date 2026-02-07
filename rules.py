from dataclasses import dataclass
from typing import Callable, List, Optional
import random


@dataclass
class Rule:
    name: str
    apply: Callable[[], None]


class RuleManager:
    def __init__(
        self,
        rules: List[Rule],
        interval: float,
        combo_rules: Optional[List[Rule]] = None,
        combo_chance: float = 0.0,
    ):
        self.rules = rules
        self.interval = interval
        self.combo_rules = combo_rules or []
        self.combo_chance = combo_chance

        self.timer = 0.0
        self.index = 0
        self.current_rule: Optional[Rule] = None

        self.frozen = False

    def update(self, delta_time: float) -> bool:
        if self.frozen:
            return False

        self.timer += delta_time
        if self.timer >= self.interval:
            self.timer = 0.0
            return self._apply_next_rule()

        return False

    def force_next_rule(self) -> bool:
        """F2: force rule switch immediately."""
        self.timer = 0.0
        return self._apply_next_rule()

    def toggle_freeze(self) -> None:
        """F1: pause/resume automatic rule switching."""
        self.frozen = not self.frozen

    def _apply_next_rule(self) -> bool:
        use_combo = (
            self.combo_rules
            and self.combo_chance > 0
            and random.random() < self.combo_chance
        )

        if use_combo:
            self.current_rule = random.choice(self.combo_rules)
            self.current_rule.apply()
            return True

        self.current_rule = self.rules[self.index]
        self.current_rule.apply()
        self.index = (self.index + 1) % len(self.rules)
        return True
