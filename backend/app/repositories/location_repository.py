from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.location import Location


class LocationRepository:
    """
    Handles lookup and creation of activity locations.
    """

    def get_by_address(
        self,
        session: Session,
        *,
        state: str,
        lga: str,
        community: str,
    ) -> Location | None:
        """
        Retrieve a location using its administrative and community
        identifiers.
        """

        statement = select(Location).where(
            Location.state == state,
            Location.lga == lga,
            Location.community == community,
        )

        return session.scalar(statement)

    def get_or_create(
        self,
        session: Session,
        *,
        state: str,
        lga: str,
        community: str,
        latitude: float | None,
        longitude: float | None,
    ) -> Location:
        """
        Return an existing location or create a new one.

        GPS coordinates are stored when a new location is created.
        """

        location = self.get_by_address(
            session,
            state=state,
            lga=lga,
            community=community,
        )

        if location is not None:
            return location

        location = Location(
            state=state,
            lga=lga,
            community=community,
            latitude=latitude,
            longitude=longitude,
        )

        session.add(location)

        session.flush()

        return location