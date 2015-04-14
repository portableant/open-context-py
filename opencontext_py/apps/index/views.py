from django.http import HttpResponse, Http404
from django.conf import settings
from django.template import RequestContext, loader
from opencontext_py.libs.rootpath import RootPath
from opencontext_py.libs.requestnegotiation import RequestNegotiation


def index(request):
    """ Get the search context JSON-LD """
    rp = RootPath()
    base_url = rp.get_baseurl()
    req_neg = RequestNegotiation('text/html')
    new_view = False
    template = loader.get_template('index/view.html')
    if 'test' in request.GET:
        template = loader.get_template('index/view-initial-minimal.html')
        new_view = True
    context = RequestContext(request,
                             {'base_url': base_url,
                              'new_view': new_view,
                              'page_title': 'Open Context: Publisher of Research Data',
                              'act_nav': 'home',
                              'nav_items': settings.NAV_ITEMS})
    if 'HTTP_ACCEPT' in request.META:
        req_neg.check_request_support(request.META['HTTP_ACCEPT'])
    if req_neg.supported:
        # requester wanted a mimetype we DO support
        return HttpResponse(template.render(context))
    else:
        # client wanted a mimetype we don't support
        return HttpResponse(template.render(context),
                            status=415)
