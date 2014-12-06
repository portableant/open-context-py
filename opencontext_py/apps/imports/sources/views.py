import json
from django.http import HttpResponse, Http404, HttpResponseRedirect
from opencontext_py.apps.imports.sources.projects import ImportProjects
from opencontext_py.apps.imports.sources.models import ImportSource
from opencontext_py.apps.imports.sources.navtemplate import ImportNavigation
from opencontext_py.apps.imports.fields.templating import ImportProfile
from opencontext_py.apps.imports.fields.describe import ImportFieldDescribe
from django.template import RequestContext, loader
from django.views.decorators.csrf import ensure_csrf_cookie


# These views display an HTML form for classifying import fields,
# and handles AJAX requests / responses to change classifications
@ensure_csrf_cookie
def index(request):
    """ Index for sources is going to be a list of projects """
    ipr = ImportProjects()
    projs = ipr.get_all_projects()
    template = loader.get_template('imports/projects.html')
    context = RequestContext(request,
                             {'projs': projs})
    return HttpResponse(template.render(context))


def create_project(request):
    """ Create a new project """
    valid_post = False
    if request.method == 'POST':
        label = False
        short_des = False
        if 'label' in request.POST:
            label = request.POST['label']
        if 'short_des' in request.POST:
            short_des = request.POST['short_des']
        if label is not False and short_des is not False:
            valid_post = True
    if valid_post:
        ipr = ImportProjects()
        project_uuid = ipr.create_project(label,
                                          short_des)
        """
            proj = ipr.get_project(project_uuid)
            template = loader.get_template('imports/project.html')
            context = RequestContext(request,
                                     {'proj': proj})
            return HttpResponse(template.render(context))
        """
        return HttpResponseRedirect('../../imports/project/' + project_uuid)
    else:
        return HttpResponseForbidden


def edit_project(request, project_uuid):
    """ Create a new project """
    valid_post = False
    if request.method == 'POST':
        label = False
        short_des = False
        if 'label' in request.POST:
            label = request.POST['label']
        if 'short_des' in request.POST:
            short_des = request.POST['short_des']
        if label is not False and short_des is not False:
            valid_post = True
    if valid_post:
        ipr = ImportProjects()
        ok = ipr.edit_project(project_uuid,
                              label,
                              short_des)
        if ok:
            """
            proj = ipr.get_project(project_uuid)
            template = loader.get_template('imports/project.html')
            context = RequestContext(request,
                                     {'proj': proj})
            return HttpResponse(template.render(context))
            """
            return HttpResponseRedirect('../../imports/project/' + project_uuid)
        else:
            raise Http404
    else:
        return HttpResponseForbidden


@ensure_csrf_cookie
def project(request, project_uuid):
    """ Show HTML form further classifying subject fields """
    ipr = ImportProjects()
    proj = ipr.get_project(project_uuid)
    if proj is not False:
        imnav = ImportNavigation()
        proj['nav'] = imnav.set_nav('project',
                                    project_uuid,
                                    False)
        template = loader.get_template('imports/project.html')
        context = RequestContext(request,
                                 {'proj': proj})
        return HttpResponse(template.render(context))
    else:
        raise Http404


@ensure_csrf_cookie
def field_types(request, source_id):
    """ Show HTML form listing fields classified by field type """
    ip = ImportProfile(source_id)
    if ip.project_uuid is not False:
        ip.get_fields()
        imnav = ImportNavigation()
        ip.nav = imnav.set_nav('field-types',
                               ip.project_uuid,
                               source_id)
        template = loader.get_template('imports/field-types.html')
        context = RequestContext(request,
                                 {'ip': ip})
        return HttpResponse(template.render(context))
    else:
        raise Http404


@ensure_csrf_cookie
def field_types_more(request, source_id):
    """ Show HTML form further classifying subject fields """
    ip = ImportProfile(source_id)
    if ip.project_uuid is not False:
        ip.get_subject_type_fields()
        imnav = ImportNavigation()
        ip.nav = imnav.set_nav('field-types-more',
                               ip.project_uuid,
                               source_id)
        if len(ip.fields) > 0:
            template = loader.get_template('imports/field-types-more.html')
            context = RequestContext(request,
                                     {'ip': ip})
            return HttpResponse(template.render(context))
        else:
            redirect = '../../imports/field-types/' + source_id
            return HttpResponseRedirect(redirect)
    else:
        raise Http404


@ensure_csrf_cookie
def field_entity_relations(request, source_id):
    """ Show HTML form to change relationships for entities
        to be created / or updated from an import table
    """
    ip = ImportProfile(source_id)
    if ip.project_uuid is not False:
        ip.get_fields()
        if len(ip.fields) > 0:
            ip.get_field_annotations()
            ip.jsonify_field_annotations()
            imnav = ImportNavigation()
            ip.nav = imnav.set_nav('field-entity-relations',
                                   ip.project_uuid,
                                   source_id)
            template = loader.get_template('imports/field-entity-relations.html')
            context = RequestContext(request,
                                     {'ip': ip})
            return HttpResponse(template.render(context))
        else:
            redirect = '../../imports/field-types/' + source_id
            return HttpResponseRedirect(redirect)
    else:
        raise Http404


@ensure_csrf_cookie
def field_descriptions(request, source_id):
    """ Show HTML form to change relationships for entities
        to be created / or updated from an import table
    """
    ip = ImportProfile(source_id)
    if ip.project_uuid is not False:
        ip.get_fields()
        imnav = ImportNavigation()
        ip.nav = imnav.set_nav('field-descriptions',
                               ip.project_uuid,
                               source_id)
        template = loader.get_template('imports/field-descriptions.html')
        context = RequestContext(request,
                                 {'ip': ip})
        return HttpResponse(template.render(context))
    else:
        raise Http404
