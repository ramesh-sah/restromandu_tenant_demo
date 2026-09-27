install:
	python3 -m venv .venv
	. .venv/bin/activate && pip install -r requirements.txt

migrations:
	python manage.py makemigrations tenants accounts products orders

shared:
	python manage.py migrate_schemas --shared

demo:
	python manage.py create_demo_tenants

run:
	python manage.py runserver 0.0.0.0:8000
