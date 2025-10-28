import logging
import time
import traceback

logger = logging.getLogger("django.request")

class RequestResponseLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = time.time()
        user = getattr(request, 'user', None)
        user_str = f"{user.username} (ID: {user.id})" if user and user.is_authenticated else "Anonymous"
        path = request.get_full_path()
        ip = self.get_client_ip(request)

        logger.info(
            f'[REQUEST] "method": "{request.method}" | "path": "{path}" | '
            f'"user": "{user_str}" | "ip": "{ip}"'
        )

        try:
            response = self.get_response(request)
        except Exception as e:
            duration = (time.time() - start_time) * 1000

            # Get the detailed traceback
            tb = traceback.format_exc()

            logger.error(
                f'[EXCEPTION] "path": "{path}" | "method": "{request.method}" | '
                f'"user": "{user_str}" | "ip": "{ip}" | "duration_ms": "{duration:.2f}" | '
                f'"error": "{str(e)}"'
            )

            # Log the full traceback separately for debug-level logging
            logger.debug(f'Traceback:\n{tb}')

            # You could optionally attach more request data for debugging
            logger.debug(f'Request data: {request.POST.dict() if request.method == "POST" else {}}')
            logger.debug(f'Query params: {request.GET.dict()}')

            raise  # Re-raise the exception so Django can handle it properly

        duration = (time.time() - start_time) * 1000
        log_message = (
            f'[RESPONSE] "status": "{response.status_code}" | "path": "{path}" | '
            f'"duration_ms": "{duration:.2f}" | "user": "{user_str}"'
        )

        if 500 <= response.status_code <= 599:
            logger.error(log_message)
        elif 400 <= response.status_code <= 499:
            logger.warning(log_message)
        else:
            logger.info(log_message)

        return response

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR')
