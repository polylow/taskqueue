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


def get_fake_json(request):
    from random import randrange
    return JsonResponse({'data': randrange(200)})


def home_dashboard(request):
    return render(request, 'templates/main_dashboard.html', {'page_title':"lollypops"})

def worker_dashboard(request, worker_id):
    return render(request, 'templates/worker_dashboard.html', {'page_title':"worker_dashboard"})

def task_dashboard(request):
    return render(request, 'templates/main_dashboard.html', {'page_title':"lollypops"})


# urls.py

urlpatterns = (
    url(r'^$', home_dashboard),
    url(r'^worker/(?P<worker_id>[0-9a-z]{8})$', worker_dashboard),
    url(r'^worker/(?P<worker_id>[0-9a-z]{8}).json$', worker),
    url(r'^task/(?P<task_id>[0-9a-z]{32})$', task_dashboard),
    url(r'^task/(?P<task_id>[0-9a-z]{32}).json$', task),
    url(r'^input.json', get_input),
    url(r'^output.json', get_output),
)

# manage.py

if __name__ == "__main__":
    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
