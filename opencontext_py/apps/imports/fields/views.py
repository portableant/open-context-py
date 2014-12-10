import json
from django.http import HttpResponse, Http404
from opencontext_py.apps.imports.fields.templating import ImportProfile
from opencontext_py.apps.imports.fields.describe import ImportFieldDescribe
from django.template import RequestContext, loader
from django.views.decorators.csrf import ensure_csrf_cookie


# These views display an HTML form for classifying import fields,
# and handles AJAX requests / responses to change classifications
def index(request):
    return HttpResponse("Hello, world. You're at the imports fields index.")


def field_classify(request, source_id):
    """ Classifies one or more fields with posted data """
    if request.method == 'POST':
        ip = ImportProfile(source_id)
        if ip.project_uuid is not False:
            ifd = ImportFieldDescribe(source_id)
            if 'field_type' in request.POST and 'field_num' in request.POST:
                ifd.update_field_type(request.POST['field_type'],
                                      request.POST['field_num'])
            elif 'field_data_type' in request.POST and 'field_num' in request.POST:
                ifd.update_field_data_type(request.POST['field_data_type'],
                                           request.POST['field_num'])
            ip.get_fields(ifd.field_num_list)
            json_output = json.dumps(ip.jsonify_fields(),
                                     indent=4,
                                     ensure_ascii=False)
            return HttpResponse(json_output,
                                content_type='application/json; charset=utf8')
        else:
            raise Http404
    else:
        return HttpResponseForbidden


def field_meta_update(request, source_id):
    """ Classifies one or more fields with posted data """
    if request.method == 'POST':
        ip = ImportProfile(source_id)
        if ip.project_uuid is not False:
            ifd = ImportFieldDescribe(source_id)
            if 'label' in request.POST and 'field_num' in request.POST:
                ifd.update_field_label(request.POST['label'],
                                       request.POST['field_num'])
            elif 'value_prefix' in request.POST and 'field_num' in request.POST:
                ifd.update_field_value_prefix(request.POST['value_prefix'],
                                              request.POST['field_num'])
            elif 'field_value_cat' in request.POST and 'field_num' in request.POST:
                ifd.update_field_value_cat(request.POST['field_value_cat'],
                                           request.POST['field_num'])
            ip.get_subject_type_fields()
            json_output = json.dumps(ip.jsonify_fields(),
                                     indent=4,
                                     ensure_ascii=False)
            return HttpResponse(json_output,
                                content_type='application/json; charset=utf8')
        else:
            raise Http404
    else:
        return HttpResponseForbidden


def field_list(request, source_id):
    """ Classifies one or more fields with posted data """
    ip = ImportProfile(source_id)
    if ip.project_uuid is not False:
        ip.get_fields()
        json_output = json.dumps(ip.jsonify_fields(),
                                 indent=4,
                                 ensure_ascii=False)
        return HttpResponse(json_output,
                            content_type='application/json; charset=utf8')
    else:
        raise Http404