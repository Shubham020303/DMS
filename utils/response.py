# utils/responses.py
from django.http import JsonResponse


def success_response(data=None, message="Success", status=200):
    """
    Returns a standardized success response.
    """
    return JsonResponse({
        "status": "success",
        "message": message,
        "data": data
    }, status=status)


def error_response(message="An error occurred", status=500, error_code="INTERNAL_ERROR"):
    """
    Returns a standardized error response.
    """
    return JsonResponse({
        "status": "error",
        "message": message,
        "error_code": error_code
    }, status=status)

def validation_error_response(errors, message="Validation Error", status=400):
    """
    Returns a standardized validation error response.
    """
    return JsonResponse({
        "status": "error",
        "message": message,
        "errors": errors
    }, status=status)
