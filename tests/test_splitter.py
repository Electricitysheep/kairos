from kairos.backtesting.splitter import WalkForwardSplitter, WindowIndices
import pytest


class TestRollingSplitBasic:
    def test_rolling_split_basic(self):
        splitter = WalkForwardSplitter(
            n_samples=500,
            train_size=100,
            test_size=50,
            step_size=50,
            embargo=5,
            mode="rolling",
        )
        windows = splitter.split()
        # step=50, train=100
        # Window 1: train_end=100, test_end=155
        # ...
        # Window 8: train_end=450, test_end=505 > 500 - breaks
        assert len(windows) == 7


class TestTemporalOrdering:
    def test_temporal_ordering(self):
        splitter = WalkForwardSplitter(
            n_samples=500,
            train_size=100,
            test_size=30,
            step_size=30,
            embargo=5,
            mode="rolling",
        )
        windows = splitter.split()
        for w in windows:
            assert w.train_end < w.test_start, (
                f"Window {w.name}: train_end ({w.train_end}) must be < test_start ({w.test_start})"
            )

    def test_temporal_ordering_expanding(self):
        splitter = WalkForwardSplitter(
            n_samples=500,
            train_size=100,
            test_size=30,
            step_size=30,
            embargo=5,
            mode="expanding",
        )
        windows = splitter.split()
        for w in windows:
            assert w.train_end < w.test_start, (
                f"Window {w.name}: train_end ({w.train_end}) must be < test_start ({w.test_start})"
            )


class TestEmbargoGap:
    def test_embargo_gap(self):
        embargo = 5
        splitter = WalkForwardSplitter(
            n_samples=500,
            train_size=100,
            test_size=30,
            step_size=30,
            embargo=embargo,
            mode="rolling",
        )
        windows = splitter.split()
        for w in windows:
            actual_gap = w.test_start - w.train_end
            assert actual_gap >= embargo, (
                f"Window {w.name}: gap ({actual_gap}) must be >= embargo ({embargo})"
            )

    def test_embargo_gap_larger(self):
        embargo = 10
        splitter = WalkForwardSplitter(
            n_samples=500,
            train_size=100,
            test_size=30,
            step_size=30,
            embargo=embargo,
            mode="rolling",
        )
        windows = splitter.split()
        for w in windows:
            actual_gap = w.test_start - w.train_end
            assert actual_gap >= embargo


class TestInvalidParams:
    def test_train_size_too_small(self):
        with pytest.raises(ValueError, match="train_size must be >= 10"):
            WalkForwardSplitter(n_samples=200, train_size=5)

    def test_train_size_exactly_10(self):
        splitter = WalkForwardSplitter(
            n_samples=200, train_size=10, test_size=10, embargo=1, step_size=10
        )
        assert splitter.train_size == 10

    def test_test_size_zero(self):
        with pytest.raises(ValueError, match="test_size must be >= 1"):
            WalkForwardSplitter(n_samples=200, train_size=50, test_size=0)

    def test_step_size_zero(self):
        with pytest.raises(ValueError, match="step_size must be >= 1"):
            WalkForwardSplitter(n_samples=200, train_size=50, test_size=10, step_size=0)

    def test_invalid_mode(self):
        with pytest.raises(ValueError, match="mode must be one of"):
            WalkForwardSplitter(n_samples=200, train_size=50, test_size=10, mode="invalid")


class TestInsufficientData:
    def test_insufficient_data(self):
        # 50+30+5=85 > 50
        with pytest.raises(ValueError, match="n_samples .* < train_size"):
            WalkForwardSplitter(n_samples=50, train_size=50, test_size=30, embargo=5)

    def test_exactly_sufficient_data(self):
        # train=50, embargo=5, test=30 -> 85 total
        splitter = WalkForwardSplitter(
            n_samples=135,
            train_size=50,
            test_size=30,
            step_size=50,
            embargo=5,
            mode="rolling",
        )
        windows = splitter.split()
        assert len(windows) == 1


class TestExpandingMode:
    def test_expanding_mode_train_grows(self):
        splitter = WalkForwardSplitter(
            n_samples=500,
            train_size=100,
            test_size=30,
            step_size=50,
            embargo=5,
            mode="expanding",
        )
        windows = splitter.split()
        # Expanding: train_start always 0
        assert windows[0].train_start == 0
        for w in windows:
            assert w.train_start == 0
        # Later trains grow
        assert windows[0].train_end < windows[-1].train_end

    def test_rolling_vs_expanding_first_window(self):
        rolling = WalkForwardSplitter(
            n_samples=500, train_size=100, test_size=30, step_size=50, embargo=5, mode="rolling"
        )
        expanding = WalkForwardSplitter(
            n_samples=500, train_size=100, test_size=30, step_size=50, embargo=5, mode="expanding"
        )
        r_windows = rolling.split()
        e_windows = expanding.split()
        assert r_windows[0].train_start == e_windows[0].train_start
        assert r_windows[0].train_end == e_windows[0].train_end
        assert r_windows[0].test_start == e_windows[0].test_start
        assert r_windows[0].test_end == e_windows[0].test_end


class TestExactFit:
    def test_exact_fit(self):
        # train=50, embargo=5, test=30, step=100
        splitter = WalkForwardSplitter(
            n_samples=135, train_size=50, test_size=30, step_size=100, embargo=5, mode="rolling"
        )
        windows = splitter.split()
        assert len(windows) == 1
        w = windows[0]
        assert w.train_start == 0
        assert w.train_end == 50
        assert w.test_start == 55
        assert w.test_end == 85


class TestStepSize:
    def test_step_size(self):
        step = 30
        splitter = WalkForwardSplitter(
            n_samples=500, train_size=50, test_size=20, step_size=step, embargo=5, mode="rolling"
        )
        windows = splitter.split()
        for i in range(1, len(windows)):
            expected_train_start = windows[i - 1].train_start + step
            assert windows[i].train_start == expected_train_start


class TestRepr:
    def test_repr(self):
        splitter = WalkForwardSplitter(
            n_samples=500, train_size=100, test_size=30, step_size=30, embargo=5, mode="rolling"
        )
        r = repr(splitter)
        assert "WalkForwardSplitter" in r
        assert "windows=" in r
        assert "mode=rolling" in r
        assert "train=100+5+30" in r


class TestNoOverlap:
    def test_no_test_overlap(self):
        splitter = WalkForwardSplitter(
            n_samples=500, train_size=100, test_size=30, step_size=50, embargo=5, mode="rolling"
        )
        windows = splitter.split()
        all_test_indices = set()
        for w in windows:
            test_range = set(range(w.test_start, w.test_end))
            assert len(all_test_indices & test_range) == 0, f"Overlap in test at window {w.name}"
            all_test_indices.update(test_range)

    def test_train_before_test_in_window(self):
        splitter = WalkForwardSplitter(
            n_samples=500, train_size=100, test_size=30, step_size=50, embargo=5, mode="rolling"
        )
        windows = splitter.split()
        for w in windows:
            assert w.train_end <= w.test_start, f"Train after test in {w.name}"


class TestWindowIndices:
    """Test WindowIndices dataclass."""

    def test_window_indices_creation(self):
        """WindowIndices stores correct values."""
        w = WindowIndices(
            name="window_1", train_start=0, train_end=99, test_start=105, test_end=134
        )
        assert w.name == "window_1"
        assert w.train_start == 0
        assert w.train_end == 99
        assert w.test_start == 105
        assert w.test_end == 134