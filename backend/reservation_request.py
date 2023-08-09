from datetime import date


class InvalidReservationException(Exception):
    pass


class ReservationRequest:
    date: date = None
    num_guests: int = None
    message: str = ""
    name: str = ""
    address: str = ""
    phone: str = ""
    email: str = ""

    @staticmethod
    def from_formdata(data: dict) -> "ReservationRequest":
        rr = ReservationRequest()
        rr.date = date.fromisoformat(data['date'])
        if rr.date < date.today():
            raise InvalidReservationException("Requested date is in the past")
        rr.num_guests = int(data['numGuests'])
        if not (0 < rr.num_guests < 100):
            raise InvalidReservationException("Invalid number of guests")
        rr.message = data['message']
        if not rr.message:
            raise InvalidReservationException("Missing event description")
        rr.name = data['name']
        rr.address = data['kohde']
        rr.phone = data['phone']
        rr.email = data['email']
        if not (rr.name and rr.address and rr.phone and rr.email):
            raise InvalidReservationException("Missing contact details")
        return rr
