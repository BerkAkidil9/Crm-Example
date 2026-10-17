"""Run isolated checks with the active Python environment, without Docker."""
import argparse
import os
from pathlib import Path
import secrets
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent.parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('job', choices=('quality', 'test', 'all'), default='all', nargs='?')
    parser.add_argument('--workers', type=int, choices=(1, 2), default=2,
                        help='Parallel test processes (default: 2).')
    parser.add_argument('--shard', choices=('1/2', '2/2'),
                        help='Run one of two disjoint groups of test classes.')
    args = parser.parse_args()
    job = args.job
    if args.shard and job == 'quality':
        parser.error('--shard is only valid for test or all.')
    # Project settings load .env with override=True. Refuse it instead of risking
    # a local database, storage account or mail configuration during checks.
    if (ROOT / '.env').exists():
        parser.error('Run checks in a checkout without .env; the file is preserved.')

    with tempfile.TemporaryDirectory(prefix='crm-check-') as work:
        env = {key: value for key, value in os.environ.items()
               if not key.startswith(('DB_', 'DATABASE_', 'R2_', 'GMAIL_', 'EMAIL_',
                                      'DJANGO_', 'RENDER_', 'AWS_'))}
        env.update({
            'SECRET_KEY': secrets.token_urlsafe(64),
            'DEBUG': 'True',
            'DB_ENGINE': 'django.db.backends.sqlite3',
            'USE_R2': 'false',
            'USE_GMAIL_API': 'false',
            'DEFAULT_FROM_EMAIL': 'checks@example.invalid',
            'ALLOWED_HOSTS': 'localhost,127.0.0.1,testserver',
            'CSRF_TRUSTED_ORIGINS': 'https://localhost',
            'SITE_URL': 'http://localhost',
            'CRM_CHECK_DIR': work,
            'PYTHONPATH': str(ROOT),
            'PYTHONDONTWRITEBYTECODE': '1',
            'CRM_TEST_SHARD': args.shard or '',
        })

        def run(*args, production=False, cwd=ROOT):
            print('+', ' '.join(args), flush=True)
            child_env = dict(env, DEBUG='False') if production else env
            subprocess.run([sys.executable, *args], cwd=cwd, env=child_env, check=True)

        settings = '--settings=scripts.ci_settings'
        if job in ('quality', 'all'):
            run('-m', 'pip', 'check')
            run('-m', 'pip_audit', '--progress-spinner', 'off', '--strict',
                '--cache-dir', str(Path(work) / 'audit-cache'))
            run('manage.py', 'check', settings, '--fail-level', 'WARNING')
            run('manage.py', 'check', settings, '--deploy', '--fail-level', 'WARNING', production=True)
            run('manage.py', 'makemigrations', settings, '--check', '--dry-run')
            run('manage.py', 'collectstatic', settings, '--noinput', '--verbosity', '0')
        if job in ('test', 'all'):
            if job == 'test':
                run('manage.py', 'collectstatic', settings, '--noinput', '--verbosity', '0')
            # macOS spawn creates SQLite clones in the working directory.
            # Discover from ROOT, but keep those files inside this job's temp dir.
            run(str(ROOT / 'manage.py'), 'test', str(ROOT), settings,
                '--noinput', '--verbosity', '1', '--parallel', str(args.workers),
                cwd=work)


if __name__ == '__main__':
    try:
        main()
    except subprocess.CalledProcessError as error:
        sys.exit(error.returncode)
