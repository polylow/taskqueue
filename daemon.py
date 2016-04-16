import os
import sys
import redis
from django.conf import settings
from django.conf.urls import url
from django.http import HttpResponse, JsonResponse
from django.template import RequestContext, loader
from taskqueue import workers, redis_ip, redis_port
from utils import rconn, getint, getstr


# settings.py

settings.configure(
    DEBUG=True,
    BASE_DIR = os.path.abspath('.'),
    TEMPLATE_DIRS = os.path.join('.', 'templates'),
    SECRET_KEY='thisisthesecretkey',
    ROOT_URLCONF=__name__,
    MIDDLEWARE_CLASSES=(
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.middleware.clickjacking.XFrameOptionsMiddleware',
    ),
    INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
)
)

# views.py

def get_input(request):
    return JsonResponse({'data': getint("input") or 0})

def get_output(request):
    return JsonResponse({'data': getint("output") or 0})


def get_fake_json(request):
    from random import randrange
    return JsonResponse({'data': randrange(200)})


def home(request):
    template = loader.get_template('templates/dashboard.html')
    return HttpResponse(template.render({}))

# urls.py

urlpatterns = (
    url(r'^$', home),
    url(r'^data.json', get_fake_json),
)

# manage.py

if __name__ == "__main__":
    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
