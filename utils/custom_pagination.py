from math import ceil
from rest_framework import status, pagination
from rest_framework.response import Response

from utils.response_data import response_data


class CustomPagination(pagination.PageNumberPagination):
    page_size = 30
    page_size_query_param = "page_size"
    # max_page_size = 50
    page_query_param = "page"

    def get_paginated_response(self, data):
        data = response_data(200, "All data", data)
        data["count"] = self.page.paginator.count
        data["next"] = self.get_next_link()
        data["previous"] = self.get_previous_link()
        data["page_count"] = ceil(data["count"] / self.page_size)
        return Response(data, status=status.HTTP_200_OK)
