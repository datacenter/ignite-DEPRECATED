from __future__ import absolute_import
from django.utils import timezone
import pytz
import os
import requests
import json
from celery import Celery
from celery import shared_task
from group.models import *
from group.scripts import *
import imp
import concurrent.futures
from ignite.conf import RMQ_USERNAME, RMQ_PASSWORD, RMQ_VHOST
from ignite.settings import BASE_DIR
import datetime
from group.job import *

SCRIPTS_DIR = os.path.join(BASE_DIR, "group/scripts")
CELERY_ENABLE_UTC = True
BROKER = "amqp://" + RMQ_USERNAME + ":" + RMQ_PASSWORD + "@127.0.0.1/" + RMQ_VHOST
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ignite.settings')
app = Celery("ignite", backend="amqp", broker=BROKER)


def run_task_on_single_switch(switch, task):
    file_name = os.path.join(SCRIPTS_DIR, str(task['file_name']))
    dummy = imp.load_source('module', file_name)
    method = getattr(dummy, task['function'])
    print 'try number: '+str(switch['retry'])+' on '+switch['name']
    try:
        status = method(switch, **task['params'])
    except Exception as e:
       status = {}
       status['status']  = 'EXCEPTION'
       print 'Exception', e
       status['log'] = str(e)
    return switch,status


def run_task_switches(switches, task, pool):
    switch_count = len(switches)
    count = 0
    break_flag = 0
    runsize = int(task['run_size'])
    pending_switches = []
    if task['failure_action_ind']!='continue':
        pending_switches = switches[runsize:]
        switches = switches[:runsize]
    while switches:
        retry_switches = []
        threads = {pool.submit(run_task_on_single_switch, switch, task) for switch in switches}
        for future in concurrent.futures.as_completed(threads):
            switch, status = future.result()
            switch['retry'] = switch['retry'] - 1
            if status['status'] == 'SUCCESS' or not (switch['retry'] > 0):
                state = {}
                state['id'] = switch['id']
                state['name'] = switch['name']
                state['status'] = status['status']
                state['log'] = status['log']
                ctime = str(datetime.datetime.utcnow())
                ctime = datetime.datetime.strptime(ctime, '%Y-%m-%d %H:%M:%S.%f')
                ctime = timezone.make_aware(ctime, pytz.timezone('UTC'))
                state['ctime'] = ctime
                task['group']['switches'].append(state)
                if(status['status'] == 'SUCCESS'):
                    count = count + 1
                elif task['failure_action_ind']!='continue':
                    break_flag = 1
            else:
                retry_switches.append(switch)
        switches = retry_switches
        if break_flag and not switches:
            for switch in pending_switches: 
                state = {}
                state['id'] = switch['id']
                state['name'] = switch['name']
                state['status'] = 'SKIPPED'
                task['group']['switches'].append(state)
            break
        elif not switches:
            switches = pending_switches[:runsize]
            pending_switches=pending_switches[runsize:]    
    if count == switch_count:
        task['status'] = 'SUCCESS'
    else:
        task['status'] = 'FAILURE'
    return task['status']


def get_all_switches(task):
    gid = task['group_id']
    grp = Group.objects.get(id=int(gid))
    gsh = GroupSwitch.objects.filter(group__id=int(gid))
    task['group'] = {}
    task['group']['group_name'] = grp.name
    task['group']['username'] = grp.username
    task['group']['password'] = grp.password
    switches = []
    task['group']['switches'] = []
    index = 0
    for i in gsh:
        sw = {}
        sw['ip'] = i.grp_switch.mgmt_ip.split('/')[0]
        sw['id'] = i.grp_switch.id
        sw['name'] = i.grp_switch.name
        sw['user'] = grp.username
        #i.username if i.username else grp.username
        sw['pwd'] = grp.password
        #i.password if i.password else grp.password
        sw['retry'] = int(task['retry_count']) + 1
        switches.append(sw)
    return switches


def run_single_sequence(task,break_flag=False):
    print 'break_flag is',break_flag
    print 'Running sequence ' + ' on group ' + str(task['group_id'])
    switches = get_all_switches(task)
    if break_flag:
        for switch in switches:
            switche['status'] = 'SKIPPED'
        task['group']['switches'] = switches
        task['status'] = 'SKIPPED'
    else:
        runsize = task['run_size']
        #create a threadpool of size runsize
        with concurrent.futures.ThreadPoolExecutor(max_workers=runsize) as pool:
            run_task_switches(switches, task, pool)
    ctime = str(datetime.datetime.utcnow())
    ctime = datetime.datetime.strptime(ctime, '%Y-%m-%d %H:%M:%S.%f')
    ctime = timezone.make_aware(ctime, pytz.timezone('UTC'))
    task['ctime'] = ctime
    return task['status']


def fill_image_details(task):
    image_profile = ImageProfile.objects.get(pk=int(task['image_id']))
    image = {}
    if image_profile.system_image == None:
        raise Exception("No system image is found in "+image_profile.profile_name)
    if task['type'] == 'epld_upgrade' and image_profile.epld_image == None:
        raise Exception("No epld image is found in "+image_profile.profile_name)
    task['params'] = {}
    image['profile_name'] = image_profile.profile_name
    image['system_image'] = image_profile.system_image
    image['id'] = image_profile.id
    image['image_server_ip'] = image_profile.image_server_ip
    image['image_server_username'] = image_profile.image_server_username
    image['image_server_password'] = image_profile.image_server_password
    image['access_protocol'] = image_profile.access_protocol
    if task['type'] == 'epld_upgrade':
        image['epld_image'] = image_profile.epld_image
    task['params']['image'] = image


def fill_task_input(task):
    if task['type'] in ['switch_upgrade','epld_upgrade']:
        fill_image_details(task)


def get_task_parameters(task):
    print task
    if task['type'] == 'switch_upgrade':
        task['function'] = 'update_os_image_single_switch'
        task['file_name'] = 'upgrade.py'
    elif task['type'] == 'epld_upgrade':
        task['function'] = 'update_epld_image_single_switch'
        task['file_name'] = 'upgrade.py'
    fill_task_input(task)


@shared_task
def run_single_job(jid, time):
    print 'celery worker got a job with id ' + str(jid) + ' and time ' + str(time)
    jb = Job.objects.get(id=jid)
    jb.status = 'RUNNING'
    jb.save()
    tasks = []
    count = 0
    break_flag = False
    try:
        for task in jb.tasks:
            get_task_parameters(task)
            try: 
                status = run_single_sequence(task,break_flag)
            except Exception as e:
                status = 'EXCEPTION'
                print e
            if status == 'SUCCESS':
                count = count + 1
            elif task['failure_action_grp']!='continue':
               break_flag = True
            tasks.append(task)
        if count == len(tasks):
            jb.status = 'SUCCESS'
        else:
            jb.status = 'FAILURE'
        jb.tasks = tasks
    except Exception as e:
        print e
        jb.status = 'EXCEPTION'
    ref_count_delete(jb)
    ctime = str(datetime.datetime.utcnow())
    ctime = datetime.datetime.strptime(ctime, '%Y-%m-%d %H:%M:%S.%f')
    ctime = timezone.make_aware(ctime, pytz.timezone('UTC'))
    jb.ctime = ctime
    print tasks
    jb.save()
