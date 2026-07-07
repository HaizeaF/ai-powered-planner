from enum import Enum

class TaskType(str, Enum):
    """Task type: determines whether it makes sense to mark it as completed."""
    TASK = "task"
    EVENT = "event"

class ColorType(str, Enum):
    "Color type: determines tasks color"
    PURPLE = "#7c3aed"

class RecurrenceType(str, Enum):
    """Recurrence type: determines tasks recurrence."""
    NONE = "none"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"