# website/tasks.py

import logging


from celery import shared_task

from website.models import Ticket, TicketStatus

logger = logging.getLogger(__name__)


@shared_task
def delete_old_closed_tickets():

    deleted_count, _ = Ticket.objects.filter(
        status=TicketStatus.CLOSED,
    ).delete()

    logger.info("Deleted %d closed tickets past retention period", deleted_count)
