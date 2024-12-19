from django.http import HttpResponse


def trigger_error(request: HttpResponse) -> float:
    division_by_zero = 1 / 0
    return division_by_zero
