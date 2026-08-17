from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op


revision: str = "20260817_01"
down_revision: str | None = None
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "deployments",
        sa.Column(
            "id",
            sa.BigInteger(),
            sa.Identity(always=True),
            primary_key=True,
        ),
        sa.Column("version", sa.Text(), nullable=False),
        sa.Column("environment", sa.Text(), nullable=False),
        sa.Column("status", sa.Text(), nullable=False),
        sa.Column(
            "deployed_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.CheckConstraint(
            "status IN ('successful', 'failed', 'running')",
            name="deployments_status_check",
        ),
    )
    op.create_index(
        "ix_deployments_deployed_at",
        "deployments",
        ["deployed_at"],
    )


def downgrade() -> None:
    op.drop_index("ix_deployments_deployed_at", table_name="deployments")
    op.drop_table("deployments")
