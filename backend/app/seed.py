"""Seed script to populate the database with demo data."""

from sqlmodel import Session, select

from app.auth import hash_password
from app.database import create_db_and_tables, engine
from app.models import Category, Comment, PriorityEnum, StatusEnum, Ticket, User


def seed():
    """Insert demo users, categories, tickets, and comments."""
    create_db_and_tables()

    with Session(engine) as session:
        # Check if already seeded
        existing = session.exec(select(User)).first()
        if existing:
            print("Database already contains data — skipping seed.")
            return

        # ── Users ──────────────────────────────────────────────────────────
        admin = User(
            username="admin",
            email="admin@helpdesk.com",
            hashed_password=hash_password("admin123"),
            role="admin",
        )
        user1 = User(
            username="user1",
            email="user1@helpdesk.com",
            hashed_password=hash_password("user123"),
        )
        user2 = User(
            username="user2",
            email="user2@helpdesk.com",
            hashed_password=hash_password("user123"),
        )
        session.add_all([admin, user1, user2])
        session.commit()
        for u in [admin, user1, user2]:
            session.refresh(u)

        # ── Categories ─────────────────────────────────────────────────────
        categories = [
            Category(name="Bug Report", description="Software bugs and errors"),
            Category(name="Feature Request", description="New feature suggestions"),
            Category(name="Hardware", description="Hardware-related issues"),
            Category(name="Network", description="Network and connectivity problems"),
            Category(name="General", description="General inquiries"),
        ]
        session.add_all(categories)
        session.commit()
        for c in categories:
            session.refresh(c)

        # ── Tickets ────────────────────────────────────────────────────────
        tickets = [
            Ticket(
                title="Login page crashes on mobile",
                description="When I try to log in on my phone, the page freezes and eventually crashes. "
                "This happens on both iOS Safari and Android Chrome.",
                status=StatusEnum.open,
                priority=PriorityEnum.high,
                category_id=categories[0].id,
                creator_id=user1.id,
            ),
            Ticket(
                title="Add dark mode support",
                description="It would be great to have a dark mode option in the settings. "
                "Many users prefer dark themes for reduced eye strain.",
                status=StatusEnum.open,
                priority=PriorityEnum.low,
                category_id=categories[1].id,
                creator_id=user1.id,
            ),
            Ticket(
                title="Printer not detected on Floor 3",
                description="The shared printer on floor 3 is not showing up in available devices. "
                "I've tried restarting my computer but the issue persists.",
                status=StatusEnum.in_progress,
                priority=PriorityEnum.medium,
                category_id=categories[2].id,
                creator_id=user2.id,
                assignee_id=admin.id,
            ),
            Ticket(
                title="VPN connection drops frequently",
                description="My VPN connection drops every 10-15 minutes while working remotely. "
                "This causes interruptions in my workflow.",
                status=StatusEnum.resolved,
                priority=PriorityEnum.high,
                category_id=categories[3].id,
                creator_id=user2.id,
                assignee_id=admin.id,
            ),
            Ticket(
                title="Request for new keyboard",
                description="My keyboard's spacebar is not functioning properly. "
                "Requesting a replacement keyboard.",
                status=StatusEnum.closed,
                priority=PriorityEnum.low,
                category_id=categories[2].id,
                creator_id=user1.id,
                assignee_id=admin.id,
            ),
            Ticket(
                title="Email notifications not working",
                description="I am not receiving email notifications for new ticket updates. "
                "I've checked my spam folder and notification settings.",
                status=StatusEnum.open,
                priority=PriorityEnum.critical,
                category_id=categories[0].id,
                creator_id=user2.id,
            ),
        ]
        session.add_all(tickets)
        session.commit()
        for t in tickets:
            session.refresh(t)

        # ── Comments ───────────────────────────────────────────────────────
        comments = [
            Comment(
                content="I can reproduce this issue. Looking into it now.",
                ticket_id=tickets[0].id,
                author_id=admin.id,
            ),
            Comment(
                content="This also happens on Firefox mobile for me.",
                ticket_id=tickets[0].id,
                author_id=user1.id,
            ),
            Comment(
                content="I've installed new drivers for the printer. Can you check again?",
                ticket_id=tickets[2].id,
                author_id=admin.id,
            ),
            Comment(
                content="It's showing up now. Thanks!",
                ticket_id=tickets[2].id,
                author_id=user2.id,
            ),
            Comment(
                content="The VPN configuration has been updated. Please reconnect and test.",
                ticket_id=tickets[3].id,
                author_id=admin.id,
            ),
            Comment(
                content="Working perfectly now, no disconnections in the past 2 hours.",
                ticket_id=tickets[3].id,
                author_id=user2.id,
            ),
            Comment(
                content="New keyboard has been delivered to your desk.",
                ticket_id=tickets[4].id,
                author_id=admin.id,
            ),
        ]
        session.add_all(comments)
        session.commit()

        print("[OK] Demo data seeded successfully!")
        print(f"   Users:      {len([admin, user1, user2])}")
        print(f"   Categories: {len(categories)}")
        print(f"   Tickets:    {len(tickets)}")
        print(f"   Comments:   {len(comments)}")
        print()
        print("Demo credentials:")
        print("  Admin  → admin / admin123")
        print("  User 1 → user1 / user123")
        print("  User 2 → user2 / user123")


if __name__ == "__main__":
    seed()
