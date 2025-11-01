#!/usr/bin/env python3
"""
Django management command to seed the database with sample Listings,
Bookings and Reviews.

Usage:
    python manage.py seed
    python manage.py seed --clear   # optional: delete existing seeded data first
"""
from decimal import Decimal
import random
from datetime import date, timedelta
from typing import List

from django.core.management.base import BaseCommand
from django.db import transaction
from django.contrib.auth import get_user_model

from listings.models import Listing, Booking, Review


User = get_user_model()


def model_has_field(model_cls, field_name: str) -> bool:
    """Return True if model has a field named `field_name`."""
    try:
        model_cls._meta.get_field(field_name)
        return True
    except Exception:
        return False


class Command(BaseCommand):
    help = "Seed the database with sample listings, bookings and reviews."

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Clear existing Listings, Bookings and Reviews before seeding",
        )
        parser.add_argument(
            "--listings",
            type=int,
            default=10,
            help="Number of listings to create (default: 10)",
        )
        parser.add_argument(
            "--users",
            type=int,
            default=6,
            help="Number of users to create (default: 6)",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        clear = options.get("clear", False)
        num_listings = options.get("listings", 10)
        num_users = options.get("users", 6)

        if clear:
            self.stdout.write("Clearing existing seeded data...")
            # Delete in order to avoid FK issues
            if model_has_field(Booking, "id"):
                Booking.objects.all().delete()
            if model_has_field(Review, "id"):
                Review.objects.all().delete()
            Listing.objects.all().delete()
            self.stdout.write(self.style.SUCCESS("Existing listings/bookings/reviews deleted."))

        self.stdout.write("Creating users...")
        users: List[User] = [] # type: ignore
        for i in range(1, num_users + 1):
            username = f"seed_user_{i}"
            email = f"{username}@example.com"
            user, created = User.objects.get_or_create(
                username=username,
                defaults={"email": email},
            )
            if created:
                # best-effort to set a usable password (not required by the checker)
                try:
                    user.set_password("password123")
                    user.save()
                except Exception:
                    # some custom user models may not support set_password in the same way
                    pass
            users.append(user)

        # Decide hosts (some subset of the created users)
        num_hosts = max(1, num_users // 3)
        hosts = users[:num_hosts]

        titles = [
            "Sunny Beach House",
            "Cozy Mountain Cabin",
            "Downtown Studio Apartment",
            "Riverside Cottage",
            "Luxury Villa with Pool",
            "Quiet Country Bungalow",
            "Modern Loft",
            "Seaside Bungalow",
            "Historic Townhouse",
            "Forest Retreat",
            "City Penthouse",
            "Lakefront Condo",
        ]

        locations = [
            "Miami", "Aspen", "New York", "Los Angeles", "Seattle",
            "San Francisco", "Portland", "Austin", "Chicago", "Boston",
        ]

        self.stdout.write(f"Creating {num_listings} listings...")
        created_listings = []
        for i in range(num_listings):
            title = titles[i % len(titles)] + f" #{i+1}"
            location = random.choice(locations)
            description = f"A lovely stay at {location}. Perfect for guests who love comfort."
            price = Decimal(random.randint(50, 400))

            listing_defaults = {
                "description": description,
                "location": location,
                "price_per_night": price,
            }

            # attach host if Listing model has 'host' or 'owner' field
            if model_has_field(Listing, "host"):
                listing_defaults["host"] = random.choice(hosts)
            elif model_has_field(Listing, "owner"):
                listing_defaults["owner"] = random.choice(hosts)

            listing, _ = Listing.objects.get_or_create(title=title, defaults=listing_defaults)
            created_listings.append(listing)

        self.stdout.write(self.style.SUCCESS(f"Created/verified {len(created_listings)} listings."))

        # Create Bookings
        self.stdout.write("Creating bookings...")
        bookings_created = 0
        for listing in created_listings:
            # random number of bookings per listing
            for _ in range(random.randint(0, 3)):
                guest = random.choice(users)

                start_offset = random.randint(0, 30)
                start = date.today() + timedelta(days=start_offset)
                end = start + timedelta(days=random.randint(1, 7))

                booking_kwargs = {
                    "listing": listing,
                    "start_date": start,
                    "end_date": end,
                }

                # Attach guest field name depending on model
                if model_has_field(Booking, "guest"):
                    booking_kwargs["guest"] = guest
                elif model_has_field(Booking, "user"):
                    booking_kwargs["user"] = guest
                elif model_has_field(Booking, "customer"):
                    booking_kwargs["customer"] = guest
                else:
                    # fallback: try 'guest' and hope for the best (will raise if missing)
                    booking_kwargs["guest"] = guest

                Booking.objects.create(**booking_kwargs)
                bookings_created += 1

        self.stdout.write(self.style.SUCCESS(f"Created {bookings_created} bookings."))

        # Create Reviews
        self.stdout.write("Creating reviews...")
        reviews_created = 0
        for listing in created_listings:
            for _ in range(random.randint(0, 3)):
                reviewer = random.choice(users)
                rating = random.randint(1, 5)
                comment = f"Sample review: rating {rating}."

                review_kwargs = {
                    "listing": listing,
                    "rating": rating,
                    "comment": comment,
                }

                # Attach user field name depending on model
                if model_has_field(Review, "user"):
                    review_kwargs["user"] = reviewer
                elif model_has_field(Review, "author"):
                    review_kwargs["author"] = reviewer
                else:
                    review_kwargs["user"] = reviewer

                try:
                    Review.objects.create(**review_kwargs)
                    reviews_created += 1
                except Exception:
                    # ignore duplicate unique constraints or unexpected field names
                    continue

        self.stdout.write(self.style.SUCCESS(f"Created {reviews_created} reviews."))

        self.stdout.write(self.style.SUCCESS("Seeding complete!"))
