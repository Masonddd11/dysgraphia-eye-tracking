"""Head-pitch monitor<->paper switch detector with hysteresis + dwell.

A look-down at the paper produces a large positive head-pitch excursion; the
detector turns that into clean binary attention-state events:

- Hysteresis: readings between ``exit_deg`` and ``enter_deg`` hold the
  current raw state (no chatter at the boundary).
- Dwell: a new state is only committed (and an event emitted) after it has
  persisted continuously for ``dwell_ms``.
"""

from __future__ import annotations

from dataclasses import dataclass, field

MONITOR = 0
PAPER = 1


@dataclass
class SwitchConfig:
    enter_deg: float = 18.0  # pitch at/above which raw state becomes PAPER
    exit_deg: float = 12.0  # pitch at/below which raw state becomes MONITOR
    dwell_ms: float = 200.0  # continuous persistence required to commit


@dataclass
class SwitchDetector:
    config: SwitchConfig = field(default_factory=SwitchConfig)
    state: int = MONITOR
    events: list[tuple[float, int]] = field(default_factory=list)  # (t_ms, new_state)
    _raw: int = MONITOR
    _pending: int | None = None
    _since_ms: float = 0.0

    def update(self, down_deg: float, t_ms: float) -> int:
        cfg = self.config
        if down_deg >= cfg.enter_deg:
            self._raw = PAPER
        elif down_deg <= cfg.exit_deg:
            self._raw = MONITOR
        # else: inside the hysteresis band, hold the previous raw state.

        if self._raw != self.state:
            if self._pending != self._raw:
                self._pending = self._raw
                self._since_ms = t_ms
            elif t_ms - self._since_ms >= cfg.dwell_ms:
                self.state = self._raw
                self.events.append((t_ms, self.state))
                self._pending = None
        else:
            self._pending = None
        return self.state
