"""Initial schema

Revision ID: 001
Revises:
Create Date: 2026-03-29

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('full_name', sa.String(), nullable=True),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('is_verified', sa.Boolean(), default=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('garmin_email', sa.String(), nullable=True),
        sa.Column('garmin_oauth1_token', sa.String(), nullable=True),
        sa.Column('garmin_oauth2_token', sa.String(), nullable=True),
        sa.Column('garmin_connected_at', sa.DateTime(), nullable=True),
    )
    op.create_index('ix_users_email', 'users', ['email'], unique=True)

    # Create workout_templates table
    op.create_table(
        'workout_templates',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('workout_type', sa.Enum('running', 'cycling', 'swimming', 'strength', 'other', name='workouttype'), nullable=False),
        sa.Column('original_prompt', sa.Text(), nullable=False),
        sa.Column('parsed_data', postgresql.JSONB(), nullable=True),
        sa.Column('garmin_workout_id', sa.String(), nullable=True),
        sa.Column('uploaded_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_workout_templates_user_id', 'workout_templates', ['user_id'])

    # Create workout_steps table
    op.create_table(
        'workout_steps',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('workout_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('order', sa.Integer(), nullable=False),
        sa.Column('step_type', sa.Enum('warmup', 'interval', 'recovery', 'cooldown', 'repeat', name='steptype'), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('duration_type', sa.Enum('time', 'distance', 'calories', 'heart_rate', 'open', name='durationtype'), nullable=False),
        sa.Column('duration_value', sa.Float(), nullable=True),
        sa.Column('target_type', sa.Enum('pace', 'speed', 'heart_rate', 'power', 'cadence', 'open', name='targettype'), nullable=False),
        sa.Column('target_value_low', sa.Float(), nullable=True),
        sa.Column('target_value_high', sa.Float(), nullable=True),
        sa.Column('repeat_times', sa.Integer(), default=1),
        sa.Column('repeat_steps', postgresql.JSONB(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['workout_id'], ['workout_templates.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_workout_steps_workout_id', 'workout_steps', ['workout_id'])


def downgrade() -> None:
    op.drop_index('ix_workout_steps_workout_id')
    op.drop_table('workout_steps')
    op.drop_index('ix_workout_templates_user_id')
    op.drop_table('workout_templates')
    op.drop_index('ix_users_email')
    op.drop_table('users')

    # Drop enums
    op.execute('DROP TYPE IF EXISTS targettype')
    op.execute('DROP TYPE IF EXISTS durationtype')
    op.execute('DROP TYPE IF EXISTS steptype')
    op.execute('DROP TYPE IF EXISTS workouttype')
