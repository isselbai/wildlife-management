from django.db import DatabaseError
from django.http import HttpResponseServerError
import logging

logger = logging.getLogger(__name__)

class DatabaseErrorMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            response = self.get_response(request)
            return response
        except DatabaseError as e:
            logger.error(f"Database error: {str(e)}")
            return HttpResponseServerError("A database error occurred. Please try again later.") 