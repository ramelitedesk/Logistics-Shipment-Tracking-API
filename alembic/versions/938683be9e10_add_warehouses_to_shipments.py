"""add warehouses to shipments

Revision ID: 938683be9e10
Revises: bcb58d114903
Create Date: 2026-10-02 13:08:00.672865

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "938683be9e10"
down_revision: Union[str, Sequence[str], None] = "bcb58d114903"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.add_column(
        "shipments",
        sa.Column(
            "origin_warehouse_id",
            sa.Integer(),
            nullable=True,
        ),
    )

    op.add_column(
        "shipments",
        sa.Column(
            "destination_warehouse_id",
            sa.Integer(),
            nullable=True,
        ),
    )

    op.create_index(
        "ix_shipments_origin_warehouse_id",
        "shipments",
        ["origin_warehouse_id"],
        unique=False,
    )

    op.create_index(
        "ix_shipments_destination_warehouse_id",
        "shipments",
        ["destination_warehouse_id"],
        unique=False,
    )

    op.create_foreign_key(
        "fk_shipments_origin_warehouse",
        "shipments",
        "warehouses",
        ["origin_warehouse_id"],
        ["id"],
    )

    op.create_foreign_key(
        "fk_shipments_destination_warehouse",
        "shipments",
        "warehouses",
        ["destination_warehouse_id"],
        ["id"],
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_constraint(
        "fk_shipments_destination_warehouse",
        "shipments",
        type_="foreignkey",
    )

    op.drop_constraint(
        "fk_shipments_origin_warehouse",
        "shipments",
        type_="foreignkey",
    )

    op.drop_index(
        "ix_shipments_destination_warehouse_id",
        table_name="shipments",
    )

    op.drop_index(
        "ix_shipments_origin_warehouse_id",
        table_name="shipments",
    )

    op.drop_column(
        "shipments",
        "destination_warehouse_id",
    )

    op.drop_column(
        "shipments",
        "origin_warehouse_id",
    )