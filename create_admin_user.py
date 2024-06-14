import asyncio
from tortoise import Tortoise, run_async
from models import User, Team
from werkzeug.security import generate_password_hash

async def create_admin_user():
    # Initialize Tortoise ORM
    await Tortoise.init(
        db_url='sqlite://site.db',
        modules={'models': ['models']}
    )

    # Generate password hash
    password_hash = generate_password_hash("admin")

    # Get or create the admin team
    team, created = await Team.get_or_create(name="admin")

    # Create the admin user
    user, created = await User.get_or_create(
        username="admin",
        defaults={
            "password_hash": password_hash,
            "team": team,
            "is_admin": True
        }
    )

    if created:
        print("Admin user created successfully.")
    else:
        print("Admin user already exists.")

    # Close Tortoise ORM connections
    await Tortoise.close_connections()

if __name__ == "__main__":
    run_async(create_admin_user())
