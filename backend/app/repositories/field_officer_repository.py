from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.field_officer import FieldOfficer


class FieldOfficerRepository:
    """
    Handles lookup and creation of field officers based on
    identifiers provided by the source platform.
    """

    def get_by_external_id(
        self,
        session: Session,
        *,
        external_id: str,
    ) -> FieldOfficer | None:
        """
        Retrieve a field officer using the source-system identifier.
        """

        statement = select(FieldOfficer).where(
            FieldOfficer.external_id == external_id
        )

        return session.scalar(statement)

    def get_or_create(
        self,
        session: Session,
        *,
        external_id: str,
        full_name: str,
    ) -> FieldOfficer:
        """
        Return an existing field officer or create one when
        the external identifier is new.
        """

        field_officer = self.get_by_external_id(
            session,
            external_id=external_id,
        )

        if field_officer is not None:
            return field_officer

        field_officer = FieldOfficer(
            external_id=external_id,
            full_name=full_name,
            is_active=True,
        )

        session.add(field_officer)

        session.flush()

        return field_officer