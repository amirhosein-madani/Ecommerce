import logging

from celery import shared_task

from reviews.models import Review, ReviewStatus

logger = logging.getLogger(__name__)


@shared_task
def delete_rejected_reviews() -> None:
    """
    Delete reviews that have been rejected by moderation..
    """

    deleted_count, _ = Review.objects.filter(status=ReviewStatus.REJECTED).delete()
    logger.info("Deleted %d rejected reviews", deleted_count)
