from .models import Notification

def notify_booking_created(booking):
    content = f'New booking created by {booking.user.username} for property {booking.property.title}.'
    Notification.objects.create(
        recipient=booking.property.owner,
        event_type='booking_created',
        content=content,
        related_object_id=booking.id
    )

def notify_booking_status_changed(booking):
    content = f'Booking status changed to {booking.status} for property {booking.property.title}.'
    Notification.objects.create(
        recipient=booking.user,
        event_type='booking_status_changed',
        content=content,
        related_object_id=booking.id
    )

def notify_new_review(review):
    content = f'New review from {review.user.username} on property {review.property.title}.'
    Notification.objects.create(
        recipient=review.property.owner,
        event_type='new_review',
        content=content,
        related_object_id=review.id
    )
