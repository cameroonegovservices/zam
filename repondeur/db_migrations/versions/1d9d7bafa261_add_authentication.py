"""Add authentication

Revision ID: 1d9d7bafa261
Revises: 72b5668e320f
Create Date: 2019-03-26 11:00:30.180008

"""
from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils


# revision identifiers, used by Alembic.
revision = "1d9d7bafa261"
down_revision = "72b5668e320f"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "teams",
        sa.Column(
            "password", sqlalchemy_utils.types.password.PasswordType(), nullable=True
        ),
    )
    op.add_column(
        "users",
        sa.Column(
            "password", sqlalchemy_utils.types.password.PasswordType(), nullable=True
        ),
    )


def downgrade():
    op.drop_column("users", "password")
    op.drop_column("teams", "password")
