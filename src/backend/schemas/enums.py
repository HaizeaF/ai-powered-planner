from enum import Enum

class TaskType(str, Enum):
    """Task type: determines whether it makes sense to mark it as completed."""
    TASK = "task"
    EVENT = "event"

class ColorType(str, Enum):
    "Color type: determines tasks color"
    PURPLE = "#7c3aed",
    AMBAR = "#f59e0b",
    RED = "#ef4444",
    GREEN = "#10b981",
    BLUE = "#3b82f6",
    PINK = "#ec4899"