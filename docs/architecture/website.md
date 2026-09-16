# Website App Architecture

## Overview

The `website` app contains models that represent general website-level
features and are not directly associated with a specific business-domain app.

These models provide functionality that is shared across different parts
of the system and therefore are kept separately from domain-specific apps.

The app currently contains the following models:

- `Ticket`
- `TicketMessage`
- `Wishlist`

---

## Ticket System

The ticket system is designed to provide a structured way for users to
communicate with the support team.

A `Ticket` represents a support request created by a user. Each ticket
contains information such as its category, priority, status, and optionally
the order related to the request.

The ticket can therefore provide context for the support team and make it
easier to identify the reason and importance of a user's request.

### Ticket Categories

Tickets can be categorized based on the subject of the request, such as:

- Order
- Payment
- Product
- Account
- Technical
- Other

### Ticket Priority

Each ticket has a priority level to indicate the importance of the request:

- Low
- Medium
- High
- Urgent

### Ticket Status Lifecycle

A ticket can be in one of four states:

- `OPEN` — default state when a ticket is created.
- `IN_PROGRESS` — support is actively working on the request.
- `ANSWERED` — support has replied and is awaiting the user's response.
- `CLOSED` — the request has been resolved.

**Status changes are manual, not automatic.** There is no signal or
model-level logic that transitions a ticket between states based on
message activity (e.g. adding a staff reply does not automatically move
the ticket to `ANSWERED`).

The `status` field is writable only by admins. The serializer marks
`status` as **read-only for non-admin users** — a regular user cannot
change a ticket's status through the API, regardless of what value they
submit. Only staff can move a ticket through `OPEN → IN_PROGRESS →
ANSWERED → CLOSED`.

Confirmed: `closed_at` is set automatically when a ticket's `status`
becomes `CLOSED`.

Confirmed: closed tickets **cannot be reopened** — there is no path
in the API to move a `CLOSED` ticket back to an earlier status.

### Related Order

A ticket can optionally be associated with an order belonging to the user.

This allows support requests related to a specific order to retain a direct
reference to that order.

**Technical decision — `SET_NULL` instead of `CASCADE`:** if the
referenced order is deleted, the ticket is not deleted with it; only its
link to the order is cleared. This preserves the support conversation
history even if the underlying order record no longer exists.

---

## Ticket Messages

`TicketMessage` is used to store the messages exchanged within a ticket.

The reason for separating messages from the `Ticket` model is to allow a
ticket to contain an ongoing conversation between the user and the support
team.

Instead of requiring the user to create a new ticket for every additional
message, the user can continue the conversation within the existing ticket
until the ticket is closed.

This provides a conversation-based support flow:

```
User creates a ticket
→ Support responds
→ User continues the conversation
→ Support responds
→ Ticket is eventually closed
```

Each message stores its `sender` and an `is_staff_reply` flag indicating
whether the message was sent by support rather than the user. This flag
is what allows the conversation to be rendered with the sender's role
distinguished (e.g. styled differently in the UI for staff vs. user
messages).

> ⚠️ **TBD — needs verification:** whether the API enforces that no new
> `TicketMessage` can be added once a ticket's `status` is `CLOSED`.
> No such constraint currently exists at the model level; if this is an
> intended rule, it must be enforced in the view/serializer layer.

---

## Wishlist

The `Wishlist` model represents the products a user wants to save for later.

Each user has a single wishlist, and the wishlist can contain multiple
products.

**Technical decision — automatic creation via `post_save` signal:** the
wishlist is created automatically whenever a new `User` is saved, via a
signal listening on `User`'s `post_save`. This ensures every user has a
wishlist without requiring every user-creation code path (registration,
admin panel, test fixtures, seed scripts) to remember to create one
manually.

**Known limitation:** the `post_save` signal is not triggered by
`User.objects.bulk_create()`. Users created this way will not
automatically receive a wishlist and would need one created manually.

---

## Architectural Responsibility

The `website` app is intentionally kept separate from domain-specific apps.

Its responsibility is to contain general website functionality that does not
belong exclusively to applications such as `products`, `order`, or
`accounts`.

Currently, the main responsibilities of this app are:

- Customer support and ticket management
- Ticket conversations and messages
- User wishlists

---

## Data Retention

Closed tickets are periodically deleted via a Celery Beat task,
`delete_old_closed_tickets` (in `website/tasks.py`), once a configurable
retention period (`settings.CLOSED_TICKET_RETENTION_DAYS`, default 30
days) has passed since `closed_at`. Since `closed_at` is reliably set
when a ticket closes (see Ticket Status Lifecycle above), the task can
filter directly on it.

## Known Issues / Open Questions

- Whether adding a `TicketMessage` to a `CLOSED` ticket is blocked is
  not yet confirmed — no model-level constraint currently exists.
- `status`, `category`, and `priority` fields on `Ticket` do not
  currently specify `max_length`, which can behave inconsistently
  across database backends (works on SQLite, may error on
  PostgreSQL/MySQL at migration time).