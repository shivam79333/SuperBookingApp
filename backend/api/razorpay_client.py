import logging

import razorpay
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

logger = logging.getLogger(__name__)


def initialize_razorpay_client():
    """
    Initializes the Razorpay client, verifies authentication, and returns the client.
    Raises ImproperlyConfigured if credentials are not set or are invalid.
    """
    key_id = settings.RAZORPAY_KEY_ID
    key_secret = settings.RAZORPAY_KEY_SECRET

    if not key_id or not key_secret:
        raise ImproperlyConfigured(
            "RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET must be set in your environment variables/settings."
        )

    try:
        client = razorpay.Client(auth=(key_id, key_secret))
        # Make a lightweight API call to verify credentials
        client.order.all({"count": 1})
        logger.info("Successfully authenticated with Razorpay.")
        return client
    except razorpay.errors.AuthenticationError as e:
        logger.error(
            "Razorpay authentication failed. Please check your RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET."
        )
        raise ImproperlyConfigured(
            "Razorpay authentication failed. Please check your credentials."
        ) from e


client = initialize_razorpay_client()
