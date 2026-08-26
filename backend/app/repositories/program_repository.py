from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.program import Program


class ProgramRepository:
    """
    Handles lookup and creation of programs.
    """

    def get_by_name(
        self,
        session: Session,
        *,
        name: str,
    ) -> Program | None:
        """
        Retrieve a program using its unique name.
        """

        statement = select(Program).where(
            Program.name == name
        )

        return session.scalar(statement)

    def get_or_create(
        self,
        session: Session,
        *,
        name: str,
    ) -> Program:
        """
        Return an existing program or create it if it does not
        already exist.
        """

        program = self.get_by_name(
            session,
            name=name,
        )

        if program is not None:
            return program

        program = Program(
            name=name,
            is_active=True,
        )

        session.add(program)

        session.flush()

        return program