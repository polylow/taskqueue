import os
import sys
import datetime
import dill, types
from django.conf import settings
from django.conf.urls import url
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.template import RequestContext, loader
from taskqueue import rconn, getint, getstr, fetch_task
from random import randrange


# settings.py
BASE_DIR = os.path.abspath('.')

settings.configure(
    DEBUG=True,
    BASE_DIR=BASE_DIR,
    # TEMPLATE_DIRS = os.path.join('.', 'templates'),
    SECRET_KEY='thisisthesecretkey',
    ROOT_URLCONF=__name__,
    MIDDLEWARE_CLASSES=(
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.middleware.clickjacking.XFrameOptionsMiddleware',
    ),
    INSTALLED_APPS=(
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.messages',
        'django.contrib.staticfiles',
    ),
    TEMPLATES=[{
        'BACKEND': 'django.template.backends.jinja2.Jinja2',
        'DIRS': [
            'templates',
        ],
        'APP_DIRS': False,
        'OPTIONS': {
        },
    }, ],
    STATICFILES_DIRS=(
        os.path.join(BASE_DIR, 'static'),
    ),
    STATIC_URL='/static/',
)

# views.py


def fails(request):
    rindex = rconn.llen('fail')
    if rindex > 10:
        lindex = rindex - 10
    else:
        lindex = 0
    results = rconn.lrange('fail', lindex, rindex)
    results = (x.decode('utf-8') for x in results)
    return results


def get_io(request):
    return JsonResponse({'input': getint('input') or 0,
                         'output': getint('output') or 0})


def worker(request, worker_id):
    available = bool(getint('worker:' + worker_id + '.available'))
    if not available:
        current = getstr('worker:' + worker_id + '.current')
    else:
        current = None
    count_success = getint('worker:' + worker_id + '.count_success') or 0
    count_failed = getint('worker:' + worker_id + '.count_failed') or 0
    # total no of tasks finished
    throughput = (count_failed or 0) + (count_success or 0)
    data = {
        'available': available,
        'current': current,
        'throughput': throughput,
        'count_success': count_success,
        'count_failed': count_failed,
    }
    return JsonResponse(data)


def workers(request):
    results = rconn.lrange("workers", 0, -1)
    workers_list = [x.decode('utf-8') for x in results]
    results = {}

    for worker in workers_list:
        worker_id = worker.split()[0]
        available = bool(getint('worker:' + worker_id + '.available'))
        if not available:
            current = getstr('worker:' + worker_id + '.current')
        else:
            current = None
        count_success = getint('worker:' + worker_id + '.count_success') or 0
        count_failed = getint('worker:' + worker_id + '.count_failed') or 0
        data = {
            'id': worker_id,
            'ip': worker.split()[1],
            'port': worker.split()[2],
            'available': available,
            'current': current,
            'count_success': count_success,
            'count_failed': count_failed,
        }
        results[worker_id] = data

    return render(request, 'workers.html', {'workers': results})


def home_dashboard(request):
    context = {'page_title': 'Task Queue Dashboard'}
    return render(request, 'main_dashboard.html', context)


def worker_dashboard(request, worker_id):
    return render(request, 'worker_dashboard.html', {'page_title': 'worker_dashboard', 'json_slug': worker_id})


def task_dashboard(request, task_id):
    task = fetch_task(task_id)
    task = dill.loads(task)
    data = {
        'id': task_id,
        'creation_time' : datetime.datetime.fromtimestamp(task.creation_time),
        'running_time' : task.running_time,
        'result' : task.result
    }
    return render(request, 'task.html', data)

def tasklist(request):
    tasks = rconn.lrange("tasks", 0, -1)
    tasklist = []
    for t in tasks:
        td = fetch_task(t.decode('utf-8'))
        td = dill.loads(td)
        td.creation_time = datetime.datetime.fromtimestamp(td.creation_time)
        td.id = t.decode('utf-8');
        tasklist.append(td)
    totaltasks = len(tasklist)
    return render(request, 'tasklist.html', {'page_title':'tasklist', 'tasks': tasklist, 'total': totaltasks})

# urls.py

urlpatterns = (
    url(r'^$', home_dashboard),
    url(r'^workers/$', workers),
    url(r'^worker/(?P<worker_id>[0-9a-z]{8})$', worker_dashboard),
    url(r'^worker/(?P<worker_id>[0-9a-z]{8}).json$', worker),
    url(r'^task/(?P<task_id>[0-9a-z]{32})$', task_dashboard),
    url(r'^alltasks/$', tasklist),
    url(r'^io.json', get_io),
)

# manage.py

if __name__ == '__main__':
    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
