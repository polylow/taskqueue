import os
import sys
import redis
from django.conf import settings
from django.conf.urls import url
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.template import RequestContext, loader
from taskqueue import workers, redis_ip, redis_port, rconn, getint, getstr
from random import randrange


# settings.py
BASE_DIR = os.path.abspath('.')

settings.configure(
    DEBUG=True,
    BASE_DIR = BASE_DIR,
    # TEMPLATE_DIRS = os.path.join('.', 'templates'),
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
    'django.contrib.staticfiles',
    ),
    TEMPLATES = [{
        'BACKEND': 'django.template.backends.jinja2.Jinja2',
        'DIRS': [
            'templates',
        ],
        'APP_DIRS': False,
        'OPTIONS': {
        },
    },],
    STATICFILES_DIRS=(
        os.path.join(BASE_DIR, 'static'),
    ),
    STATIC_URL='/static/',
)

# views.py

def task(request, task_id):
    pass

def get_io(request):
    return JsonResponse({'input': getint("input") or 0,
                    'output': getint("output") or 0})

def worker(request, worker_id):
    available = bool(getint(worker_id+".available"))
    if not available:
        current = getstr(worker_id+".current")
    else:
        current = None
    count_success = getint(worker_id+".count_success") or 0
    count_failed = getint(worker_id+".count_failed") or 0
    throughput = (count_failed or 0) + (count_success or 0) # total no of tasks finished
    data = {
        'available': available,
        'current': current,
        'throughput': throughput,
        'count_success': count_success,
        'count_failed': count_failed,
    }
    return JsonResponse(data)

def get_fake_io(request):
    return JsonResponse({'input': randrange(15,20), 'output': randrange(15,20)})


def get_fake_json(request):
    return JsonResponse({'data': randrange(15,20)})

class ChartData:
    def __init__(self, slug, graph_title):
        self.slug = slug
        self.graph_title = graph_title


def home_dashboard(request):
    context = {'page_title':"Task Queue Dashboard",
                'json_slug': [
                            ChartData('input', 'Input'),
                            ChartData('output', 'Output'),
                ],
    }
    return render(request, 'main_dashboard.html', context)

def worker_dashboard(request, worker_id):
    return render(request, 'worker_dashboard.html', {'page_title':"worker_dashboard", 'json_slug': ChartData('data', 'lolols')})

def task_dashboard(request):
    return render(request, 'main_dashboard.html', {'page_title':"lollypops"})


# urls.py

urlpatterns = (
    url(r'^$', home_dashboard),
    url(r'^worker/(?P<worker_id>[0-9a-z]{8})$', worker_dashboard),
    url(r'^worker/(?P<worker_id>[0-9a-z]{8}).json$', worker),
    url(r'^task/(?P<task_id>[0-9a-z]{32})$', task_dashboard),
    url(r'^task/(?P<task_id>[0-9a-z]{32}).json$', task),
    url(r'^io.json', get_io),
    url(r'^io1.json',get_fake_io),
    url(r'^data.json', get_fake_json),
)

# manage.py

if __name__ == "__main__":
    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)