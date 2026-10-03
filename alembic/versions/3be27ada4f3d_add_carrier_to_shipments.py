"""add carrier to shipments

Revision ID: 3be27ada4f3d
Revises: 9dbf455f653a
Create Date: 2026-10-02 15:34:34.334983

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "3be27ada4f3d"
down_revision: Union[str, Sequence[str], None] = "9dbf455f653a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.add_column(
        "shipments",
        sa.Column(
            "carrier_id",
            sa.Integer(),
            nullable=True,
        ),
    )

    op.create_index(
        "ix_shipments_carrier_id",
        "shipments",
        ["carrier_id"],
        unique=False,
    )

    op.create_foreign_key(
        "fk_shipments_carrier",
        "shipments",
        "carriers",
        ["carrier_id"],
        ["id"],
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_constraint(
        "fk_shipments_carrier",
        "shipments",
        type_="foreignkey",
    )

    op.drop_index(
        "ix_shipments_carrier_id",
        table_name="shipments",
    )

    op.drop_column(
        "shipments",
        "carrier_id",
    )