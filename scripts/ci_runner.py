"""Keep each test class together when splitting Django tests between jobs."""
import hashlib
import os

from django.test.runner import DiscoverRunner
from django.test.utils import iter_test_cases


class ShardedDiscoverRunner(DiscoverRunner):
    def load_tests_for_label(self, label, discover_kwargs):
        suite = super().load_tests_for_label(label, discover_kwargs)
        shard = os.environ.get('CRM_TEST_SHARD', '')
        if not shard:
            return suite
        if shard not in ('1/2', '2/2'):
            raise ValueError('CRM_TEST_SHARD must be 1/2 or 2/2.')
        index = int(shard[0]) - 1
        selected = []
        for test in iter_test_cases(suite):
            cls = type(test)
            identity = f'{cls.__module__}.{cls.__qualname__}'
            bucket = int.from_bytes(hashlib.sha256(identity.encode()).digest()[:8]) % 2
            if bucket == index:
                selected.append(test)
        return self.test_suite(selected)
