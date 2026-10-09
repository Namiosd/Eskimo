import threading
from core.logger import logger

# Thread-local storage to keep track of the current active test tracker
_local = threading.local()

def get_current_tracker():
    return getattr(_local, "tracker", None)

def set_current_tracker(tracker):
    _local.tracker = tracker

class StepTracker:
    def __init__(self, test_name):
        self.test_name = test_name
        self.steps = []
        self._active_stack = []

    def start_step(self, desc):
        step_num = len(self.steps) + 1
        step_obj = {"num": step_num, "desc": desc, "status": "PENDING"}
        self.steps.append(step_obj)
        self._active_stack.append(step_obj)
        logger.info(f">>> Starting Step {step_num}: {desc}...")
        return step_obj

    def pass_step(self, step_obj=None):
        target = step_obj or (self._active_stack.pop() if self._active_stack else (self.steps[-1] if self.steps else None))
        if step_obj and step_obj in self._active_stack:
            self._active_stack.remove(step_obj)
        if target:
            target["status"] = "PASSED"
            logger.info(f"=== Step {target['num']} -> [PASSED]")

    def fail_step(self, step_obj=None):
        target = step_obj or (self._active_stack.pop() if self._active_stack else (self.steps[-1] if self.steps else None))
        if step_obj and step_obj in self._active_stack:
            self._active_stack.remove(step_obj)
        if target:
            target["status"] = "FAILED"
            logger.error(f"=== Step {target['num']} -> [FAILED]")

    def print_summary(self):
        logger.info("=" * 70)
        logger.info(f" TEST RUN SUMMARY: {self.test_name}")
        logger.info("=" * 70)
        for step in self.steps:
            symbol = "✅ PASSED" if step["status"] == "PASSED" else "❌ FAILED"
            logger.info(f"Step {step['num']}: {step['desc']:<50} | {symbol}")
        logger.info("=" * 70)

class Step:
    def __init__(self, desc):
        self.desc = desc
        self._step_obj = None

    def __enter__(self):
        tracker = get_current_tracker()
        if tracker:
            self._step_obj = tracker.start_step(self.desc)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        tracker = get_current_tracker()
        if not tracker:
            return False
        if exc_type is None:
            tracker.pass_step(self._step_obj)
        else:
            tracker.fail_step(self._step_obj)
        return False  # Propagate exception

