# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.


class BookingDetails:
    def __init__(
        self,
        destination: str = None,
        origin: str = None,
        travel_date = None,
        return_date = None,
        max_cost: str = None,
        result: bool = False
    ):
        self.destination = destination
        self.origin = origin
        self.travel_date = travel_date
        self.return_date = return_date
        self.max_cost = max_cost
        self.result = result
