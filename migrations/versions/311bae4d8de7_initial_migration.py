"""Initial migration.

Revision ID: 311bae4d8de7
Revises: 
Create Date: 2020-02-06 03:53:38.828771

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '311bae4d8de7'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=20), nullable=True),
    sa.Column('password', sa.String(length=40), nullable=True),
    sa.Column('date_registered', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('username')
    )
    op.create_table('article',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.Text(), nullable=True),
    sa.Column('text', sa.Text(), nullable=True),
    sa.Column('date_posted', sa.DateTime(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_article_date_posted'), 'article', ['date_posted'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_article_date_posted'), table_name='article')
    op.drop_table('article')
    op.drop_table('user')
    # ### end Alembic commands ###
