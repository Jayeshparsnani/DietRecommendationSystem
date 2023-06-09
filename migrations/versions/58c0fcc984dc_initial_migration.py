"""Initial migration.

Revision ID: 58c0fcc984dc
Revises: 
Create Date: 2021-02-05 15:30:38.505120

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '58c0fcc984dc'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('User',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=80), nullable=False),
    sa.Column('email', sa.String(length=120), nullable=False),
    sa.Column('password', sa.String(length=100), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    op.create_table('Diet_model',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('breakfast', sa.String(), nullable=True),
    sa.Column('lunch', sa.String(), nullable=True),
    sa.Column('dinner', sa.String(), nullable=True),
    sa.Column('cal', sa.Float(), nullable=True),
    sa.Column('date_table', sa.Date(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['User.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('Exercise_model',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('exercises', sa.String(), nullable=True),
    sa.Column('date_table', sa.Date(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['User.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('Information',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('height', sa.Float(), nullable=True),
    sa.Column('weight', sa.Integer(), nullable=True),
    sa.Column('activity', sa.String(length=50), nullable=True),
    sa.Column('Diabetic', sa.String(length=50), nullable=True),
    sa.Column('date_table', sa.Date(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['User.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('Profile',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('Phone', sa.Integer(), nullable=True),
    sa.Column('age', sa.Integer(), nullable=True),
    sa.Column('gender', sa.String(length=50), nullable=True),
    sa.Column('img_filename', sa.String(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['User.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('Profile')
    op.drop_table('Information')
    op.drop_table('Exercise_model')
    op.drop_table('Diet_model')
    op.drop_table('User')
    # ### end Alembic commands ###
