"""Walk-forward data splitter for time series backtesting."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class WindowIndices:
    """Indices for a single walk-forward window."""

    name: str
    train_start: int
    train_end: int
    test_start: int
    test_end: int


class WalkForwardSplitter:
    """Generates rolling/expanding train/test windows with embargo."""

    VALID_MODES = ("rolling", "expanding")

    def __init__(
        self,
        n_samples: int,
        train_size: int = 90,
        test_size: int = 30,
        step_size: int = 30,
        embargo: int = 5,
        mode: str = "rolling",
    ):
        self.n_samples = n_samples
        self.train_size = train_size
        self.test_size = test_size
        self.step_size = step_size
        self.embargo = embargo
        self.mode = mode
        self.validate()

    def validate(self) -> None:
        if self.train_size < 10:
            raise ValueError(f"train_size must be >= 10, got {self.train_size}")
        if self.test_size < 1:
            raise ValueError(f"test_size must be >= 1, got {self.test_size}")
        if self.step_size < 1:
            raise ValueError(f"step_size must be >= 1, got {self.step_size}")
        if self.mode not in self.VALID_MODES:
            raise ValueError(f"mode must be one of {self.VALID_MODES}, got {self.mode}")
        min_required = self.train_size + self.embargo + self.test_size
        if self.n_samples < min_required:
            raise ValueError(f"n_samples ({self.n_samples}) < train_size + embargo + test_size ({min_required})")

    def split(self) -> list[WindowIndices]:
        windows: list[WindowIndices] = []
        start = 0
        i = 1

        while True:
            train_end = start + self.train_size
            test_start = train_end + self.embargo
            test_end = test_start + self.test_size

            if test_end >= self.n_samples:
                break

            windows.append(
                WindowIndices(
                    name=f"window_{i}",
                    train_start=start if self.mode == "rolling" else 0,
                    train_end=train_end,
                    test_start=test_start,
                    test_end=test_end,
                )
            )

            start += self.step_size
            i += 1

        return windows

    def get_window_count(self) -> int:
        return len(self.split())

    def __repr__(self) -> str:
        return (
            f"WalkForwardSplitter(windows={self.get_window_count()}, "
            f"mode={self.mode}, train={self.train_size}+{self.embargo}+{self.test_size})"
        )
