from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def auth_check(request):
    """
    Verify that the supplied API token belongs to an
    authenticated Django user.
    """

    return Response(
        {
            "authenticated": True,
            "user_id": request.user.pk,
            "username": request.user.get_username(),
            "is_staff": request.user.is_staff,
            "is_superuser": request.user.is_superuser,
        }
    )

