from .models import Review, Post
from .services import newest_first
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.permissions import IsAdminUser, AllowAny
from rest_framework.response import Response
from decimal import Decimal, InvalidOperation

def serialize_thought(thought):
    """
    Convert a Review or Post model object into data that can be encoded as JSON.
    """

    data = {
        "id": thought.id,
        "type": thought.kind,
        "title": thought.title,
        "created_at": thought.created_at.isoformat(),
    }

    if thought.kind == "review":
        data["rating"] = float(thought.rating)

    return data

