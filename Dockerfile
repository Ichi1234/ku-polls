FROM python:3-alpine
# An argument needed to be passed
ARG SECRET_KEY="django-insecure-d$to%ku2=3!njhhneey^s$z&qqj9)973ge+t)u7dcix@@-s^_@"
# ARG ALLOWED_HOSTS=127.0.0.1,localhost
# ARG DATABASE_URL
# ARG DB_USER
# ARG DB_PWD

WORKDIR /app/polls

# Set needed settings
# ENV SECRET_KEY=${SECRET_KEY}
# ENV DEBUG=True
# ENV TIMEZONE=UTC
# ENV ALLOWED_HOSTS=${ALLOWED_HOSTS:-127.0.0.1,localhost}
# ENV DATABASE_URL=${DATABASE_URL}
# ENV DB_USER=${DB_USER}
# ENV DB_PWD=${DB_PWD}

# # Test for secret key
# RUN if [ -z "$SECRET_KEY" ]; then echo "No secret key specified in build-arg"; exit 1; fi

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Running Django functions in here is not good!
# Apply migrations
# RUN python ./manage.py migrate

# Apply fixtures
# RUN python manage.py loaddata data/polls-v4.json data/votes-v4.json data/users.json


# Create superuser
# RUN python ./manage.py createsuperuser --username admin --email admin@example.com --noinput

RUN chmod +x ./entrypoint.sh

EXPOSE 8000
# Run application
CMD [ "./entrypoint.sh" ]