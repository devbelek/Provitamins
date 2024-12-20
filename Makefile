all:
	@echo "Hello $(LOGNAME), nothing to do by default"
	@echo "Try 'make help'"

run:
	python3 manage.py runserver 0.0.0.0:8000

migrate:
	python3 manage.py makemigrations
	python3 manage.py migrate

super:
	python3 manage.py createsuperuser

install:
	pip install -r requirements.txt

del_migrations:
	find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
	find . -path "*/migrations/*.pyc"  -delete
