"""Account creation and delivery failures shared by signup and invitations."""
from contextlib import contextmanager
import logging

from django.core.mail import send_mail as django_send_mail
from django.db import transaction

logger = logging.getLogger(__name__)


class AccountEmailError(Exception):
    pass


def send_account_mail(*args, **kwargs):
    kwargs['fail_silently'] = False
    try:
        sent = django_send_mail(*args, **kwargs)
        if sent != 1:
            raise AccountEmailError('The email backend did not accept the message.')
        return sent
    except Exception as error:
        logger.exception('Account email delivery failed')
        raise AccountEmailError('Email delivery is temporarily unavailable. Please try again later.') from error


@contextmanager
def creating_account(user):
    """Roll back a failed new account and remove only its newly saved upload."""
    if not user._state.adding:
        raise ValueError('creating_account only accepts new users.')
    try:
        with transaction.atomic():
            yield
    except Exception:
        image = user.profile_image
        if image and image._committed:
            try:
                image.delete(save=False)
            except Exception:
                logger.exception('Could not remove the upload for a failed account creation')
        raise
