from wsgiref.util import FileWrapper

from django.core.files.storage import FileSystemStorage
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
import os
from django.conf import settings
from os.path import isfile, join
from pm4py.objects.log.importer.xes import factory as xes_importer_factory
# Create your views here.
def eventlog(request):
    event_logs_path = os.path.join(settings.MEDIA_ROOT, "event_logs")
    log_attributes ={}
    if request.method =='POST':
        if "uploadButton" in request.POST:
            if "event_log" not in request.FILES:
                return HttpResponseRedirect(request.path_info)
            log = request.FILES["event_log"]
            fs = FileSystemStorage(event_logs_path)
            filename = fs.save(log.name, log)
            uploaded_file_url = fs.url(filename)
            eventlogs = [f for f in os.listdir(event_logs_path) if isfile(join(event_logs_path, f))]
            # eventlogs.append(filename)
            file_dir = os.path.join(event_logs_path, filename)
            # xes_log = xes_importer_factory.apply(file_dir)
            # no_traces = len(xes_log)
            # no_events = sum([len(trace) for trace in xes_log])
            # log_attributes['no_traces'] = no_traces
            # log_attributes['no_events'] = no_events
            return render(request, 'upload.html', {'eventlog_list': eventlogs})

        elif "deleteButton" in request.POST:  # for event logs
            if "log_list" not in request.POST:
                return HttpResponseRedirect(request.path_info)
            filename = request.POST["log_list"]
            eventlogs = [f for f in os.listdir(event_logs_path) if isfile(join(event_logs_path, f))]
            eventlogs.remove(filename)
            file_dir = os.path.join(event_logs_path, filename)
            os.remove(file_dir)
            return render(request, 'upload.html', {'eventlog_list': eventlogs})

        elif "setButton" in request.POST:
            if "log_list" not in request.POST:
                return HttpResponseRedirect(request.path_info)
            filename = request.POST["log_list"]
            settings.EVENT_LOG_NAME = filename
            file_dir = os.path.join(event_logs_path, filename)
            xes_log = xes_importer_factory.apply(file_dir)
            no_traces = len(xes_log)
            no_events = sum([len(trace) for trace in xes_log])
            log_attributes['no_traces'] = no_traces
            log_attributes['no_events'] = no_events
            eventlogs = [f for f in os.listdir(event_logs_path) if isfile(join(event_logs_path, f))]
            return render(request, 'upload.html',
                          {'eventlog_list': eventlogs, 'log_name': filename, 'log_attributes': log_attributes})
        elif "downloadButton" in request.POST:  # for event logs
            if "log_list" not in request.POST:
                return HttpResponseRedirect(request.path_info)
            filename = request.POST["log_list"]
            file_dir = os.path.join(event_logs_path, filename)
            try:
                wrapper = FileWrapper(open(file_dir, 'rb'))
                response = HttpResponse(wrapper, content_type='application/force-download')
                response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_dir)
                return response
            except Exception as e:
                return None

    else:
        eventlogs = [f for f in os.listdir(event_logs_path) if isfile(join(event_logs_path, f))]
        return render(request, 'upload.html', {'eventlog_list': eventlogs})
