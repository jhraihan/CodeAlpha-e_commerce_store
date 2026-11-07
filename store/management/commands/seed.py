from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils.text import slugify

from store.models import Category, Product

CATEGORIES = [
    "Dress",
    "Diver",
    "Chronograph",
    "Field",
]

PRODUCTS = [
    {
        "name": "AURIX Chrono AX-C120 - 42 MM",
        "category": "Chronograph",
        "price": "249.00",
        "stock": 14,
        "badge": "50% OFF",
        "description": (
            "A chronograph built for people who measure their days in moments, not "
            "hours. The AX-C120 pairs a 42 mm brushed steel case with a navy NATO "
            "strap and a dial that stays readable in any light."
        ),
    },
    {
        "name": "NOVA Classic NV-A98 - 42 MM",
        "category": "Dress",
        "price": "199.00",
        "stock": 22,
        "badge": "New Arrival",
        "description": (
            "Quiet, considered, and dressed for anything. The NV-A98 keeps a slim "
            "profile under a cuff while its sapphire crystal takes the knocks of a "
            "normal week without complaint."
        ),
    },
    {
        "name": "STEEL PRO SP-X55 - 44 MM",
        "category": "Diver",
        "price": "299.00",
        "stock": 9,
        "badge": "50% OFF",
        "description": (
            "Rated to 10 ATM and finished to a standard you would expect well above "
            "its price. A unidirectional bezel, luminous markers, and a bracelet that "
            "sits flat on the wrist."
        ),
    },
    {
        "name": "ATLAS Field AT-F30 - 40 MM",
        "category": "Field",
        "price": "179.00",
        "stock": 18,
        "badge": "",
        "description": (
            "The field watch stripped to what matters. High-contrast numerals, a "
            "canvas strap that softens with wear, and a movement that keeps time "
            "whether or not anyone is watching."
        ),
    },
    {
        "name": "MERIDIAN Automatic MR-A70 - 41 MM",
        "category": "Dress",
        "price": "429.00",
        "stock": 6,
        "badge": "New Arrival",
        "description": (
            "An automatic movement visible through an exhibition caseback, wrapped in "
            "a case thin enough to forget you are wearing it. Roman numerals, applied "
            "by hand."
        ),
    },
    {
        "name": "ORBIT Diver OR-D88 - 44 MM",
        "category": "Diver",
        "price": "359.00",
        "stock": 11,
        "badge": "",
        "description": (
            "Built around a screw-down crown and a scratch-resistant bezel insert. "
            "The OR-D88 handles salt water, sand, and the commute back home."
        ),
    },
    {
        "name": "VERTEX Chrono VX-C45 - 43 MM",
        "category": "Chronograph",
        "price": "389.00",
        "stock": 7,
        "badge": "30% OFF",
        "description": (
            "Three subdials, one tachymeter, no wasted space. A chronograph that reads "
            "cleanly at a glance instead of asking you to study it."
        ),
    },
    {
        "name": "HARBOR Classic HB-C22 - 39 MM",
        "category": "Dress",
        "price": "219.00",
        "stock": 16,
        "badge": "",
        "description": (
            "A 39 mm case for wrists that find 44 mm absurd. Domed crystal, slim "
            "leather strap, and a dial finished in warm off-white."
        ),
    },
    {
        "name": "RANGER Field RG-F18 - 40 MM",
        "category": "Field",
        "price": "159.00",
        "stock": 25,
        "badge": "50% OFF",
        "description": (
            "Lightweight, legible, and priced to be worn rather than kept in a drawer. "
            "Lume that lasts the night and a strap you can rinse under a tap."
        ),
    },
    {
        "name": "SUMMIT Automatic SM-A91 - 42 MM",
        "category": "Field",
        "price": "469.00",
        "stock": 4,
        "badge": "New Arrival",
        "description": (
            "An in-house automatic with a 42-hour reserve, housed in a case that has "
            "been drop-tested rather than described as durable."
        ),
    },
    {
        "name": "CORAL Diver CR-D60 - 42 MM",
        "category": "Diver",
        "price": "329.00",
        "stock": 0,
        "badge": "",
        "description": (
            "A diver finished in deep teal, with a ceramic bezel that resists the "
            "marks a steel one collects. Currently between production runs."
        ),
    },
    {
        "name": "ECHO Chrono EC-C33 - 41 MM",
        "category": "Chronograph",
        "price": "279.00",
        "stock": 13,
        "badge": "",
        "description": (
            "A compact chronograph at 41 mm, with pushers that give a clean mechanical "
            "click and a dial laid out for reading, not decoration."
        ),
    },
]


class Command(BaseCommand):
    help = "Create sample categories and products"

    def handle(self, *args, **options):
        categories = {}
        for name in CATEGORIES:
            category, _ = Category.objects.get_or_create(
                name=name, defaults={"slug": slugify(name)}
            )
            categories[name] = category

        created = 0
        for entry in PRODUCTS:
            slug = slugify(entry["name"])
            if Product.objects.filter(slug=slug).exists():
                continue
            Product.objects.create(
                name=entry["name"],
                slug=slug,
                description=entry["description"],
                price=Decimal(entry["price"]),
                stock=entry["stock"],
                badge=entry["badge"],
                category=categories[entry["category"]],
            )
            created += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"{len(categories)} categories ready, {created} products created"
            )
        )
