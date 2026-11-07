# TradeSphere

A small e-commerce store built with Django and PostgreSQL. Browse a watch catalog, add
items to a cart, register an account, and place an order. Staff manage products and
orders through the Django admin.

Server-rendered Django templates, one hand-written stylesheet, and vanilla JavaScript.
No frontend framework, no build step, no bundler.

## Features

- Product catalog with category filtering and pagination
- Product detail pages with stock status
- Session-based cart that works before you log in and survives login
- Inline cart quantity updates without a page reload
- Registration, login, and logout
- Checkout inside a single database transaction, with a stock re-check
- Order confirmation and per-user order history
- Django admin for catalog and order management

## Requirements

- Python 3.12
- PostgreSQL 14 or newer

## Setup

Clone the repository and enter it:

```bash
git clone <your-repository-url>
cd e-commerce-store
```

Create a virtual environment and install the dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

On Windows, activate with `.venv\Scripts\activate` instead.

Create the PostgreSQL database:

```bash
createdb tradesphere
```

Copy the environment template and fill in your own values:

```bash
cp .env.example .env
```

`.env` holds the settings the project reads at startup:

| Variable | Meaning |
|----------|---------|
| `SECRET_KEY` | Django secret key. Generate a fresh one, never reuse the example. |
| `DEBUG` | `True` for local development, `False` everywhere else |
| `DB_NAME` | Database name |
| `DB_USER` | Database user |
| `DB_PASSWORD` | Database password |
| `DB_HOST` | Database host, defaults to `localhost` |
| `DB_PORT` | Database port, defaults to `5432` |

Generate a secret key with:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Apply the migrations:

```bash
python manage.py migrate
```

Load the sample catalog of 4 categories and 12 products:

```bash
python manage.py seed
```

Start the server:

```bash
python manage.py runserver
```

The store is at http://127.0.0.1:8000/.

## Demo accounts

For local evaluation, create a demo customer and a demo superuser:

```bash
python manage.py seed_demo_users
```

| Role | Username | Password |
|------|----------|----------|
| Customer | `demo` | `demo12345` |
| Superuser | `admin` | `admin12345` |

The customer credentials also appear on the login page with a button that fills the form,
so you can sign in without copying anything. That panel is shown only when `DEBUG` is
true.

These passwords are public and deliberately weak. The command refuses to run when
`DEBUG=False`, so it cannot seed known credentials into a deployed instance. For a real
deployment, create your superuser with `python manage.py createsuperuser` and do not
create the `demo` account at all.

## Product images

The repository ships without product images; `media/` is not committed. After seeding,
products fall back to a typographic placeholder.

To use your own photographs, drop JPEGs into `media/products/` named after each product
slug, for example `echo-chrono-ec-c33-41-mm.jpg`. Run this to list the expected names:

```bash
python manage.py shell -c "from store.models import Product; [print(p.slug) for p in Product.objects.all()]"
```

Staff can also upload an image per product in the admin.

## URL map

| Method | URL | Page | Access |
|--------|-----|------|--------|
| GET | `/` | Product list | Anyone |
| GET | `/category/<slug>/` | Products in a category | Anyone |
| GET | `/product/<slug>/` | Product detail | Anyone |
| GET | `/cart/` | Cart | Anyone |
| POST | `/cart/add/<id>/` | Add to cart | Anyone |
| POST | `/cart/update/<id>/` | Change quantity | Anyone |
| POST | `/cart/remove/<id>/` | Remove a line | Anyone |
| GET, POST | `/checkout/` | Checkout | Logged in |
| GET | `/order/<id>/` | Order confirmation | Owner only |
| GET | `/orders/` | Order history | Logged in |
| GET, POST | `/accounts/register/` | Registration | Anyone |
| GET, POST | `/accounts/login/` | Login | Anyone |
| POST | `/accounts/logout/` | Logout | Logged in |
| — | `/admin/` | Admin panel | Staff |

Every state-changing request is a POST carrying Django's CSRF token.

## Data model

`Category` and `Product` hold the catalog. `Order` and `OrderItem` hold placed orders.
Users come from Django's built-in `auth.User`.

`OrderItem` copies the product name and price at checkout rather than reading them
through the foreign key. If staff later rename or reprice a product, past orders still
show what the customer actually bought and paid.

The cart is not a database table. It lives in the session as a dictionary keyed by
product ID, so a visitor can fill a cart before registering.

## Project layout

```
config/      settings, root URL configuration, WSGI
store/       catalog, cart, orders
accounts/    registration and login
templates/   base layout, store pages, auth pages
static/      style.css and cart.js
media/       uploaded product images, not committed
```

Two apps. `store` owns the catalog, the cart, and orders; `accounts` owns registration
and login.

## Security notes

- Passwords are stored as Django PBKDF2 hashes
- CSRF protection and template auto-escaping are left on
- All queries go through the ORM, so they are parameterized
- `SECRET_KEY`, the database password, and `DEBUG` are read from the environment
- `.env` is gitignored and must never be committed
- Order queries are filtered by the logged-in user, and requesting another user's order
  returns 404 rather than 403, because a 403 would confirm the order exists
- Checkout re-reads stock and price from the database inside the transaction, so a
  crafted request cannot set its own price or oversell stock

## Not included

No real payment processing, product reviews, wishlists, discount codes, shipping-rate
calculation, email sending, product search, multiple images per product, or product
variants. Orders are placed as `pending` and settled cash on delivery.

Full requirements are in `PRD.md`.
