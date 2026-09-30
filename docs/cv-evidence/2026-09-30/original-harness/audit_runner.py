import json, time, unittest
from pathlib import Path
from django.test.runner import DiscoverRunner
ROOT = Path('/private/tmp/crm-cv-audit')
class Result(unittest.TextTestResult):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.outcomes = []
    def addSuccess(self, test):
        super().addSuccess(test)
        self.outcomes.append({'id': test.id(), 'outcome': 'passed'})
    def addFailure(self, test, err):
        super().addFailure(test, err)
        self.outcomes.append({'id': test.id(), 'outcome': 'failed'})
    def addError(self, test, err):
        super().addError(test, err)
        self.outcomes.append({'id': test.id(), 'outcome': 'error'})
    def addSkip(self, test, reason):
        super().addSkip(test, reason)
        self.outcomes.append({'id': test.id(), 'outcome': 'skipped', 'reason':reason})
class Runner(DiscoverRunner):
    def build_suite(self, *args, **kwargs):
        suite = super().build_suite(*args, **kwargs)
        def flatten(s):
            for t in s:
                if isinstance(t, unittest.TestSuite): yield from flatten(t)
                else: yield t.id()
        (ROOT / 'discovery.json').write_text(json.dumps(list(flatten(suite)), indent=2))
        return suite
    def get_resultclass(self):
        return Result
    def run_suite(self, suite, **kwargs):
        start = time.perf_counter()
        result = super().run_suite(suite, **kwargs)
        (ROOT / 'results.json').write_text(json.dumps({'tests_run':result.testsRun, 'passed':sum(x['outcome']=='passed' for x in result.outcomes), 'failures':len(result.failures), 'errors':len(result.errors), 'skipped':len(result.skipped), 'expected_failures':len(result.expectedFailures), 'unexpected_successes':len(result.unexpectedSuccesses), 'seconds':time.perf_counter()-start, 'outcomes':result.outcomes}, indent=2))
        return result
