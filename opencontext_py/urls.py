from django.conf.urls import patterns, include, url
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
admin.autodiscover()

from opencontext_py.apps.ocitems.subjects import views as SubjectViews
from opencontext_py.apps.ocitems.mediafiles import views as MediaViews
from opencontext_py.apps.ocitems.documents import views as DocumentViews
from opencontext_py.apps.ocitems.persons import views as PersonViews
from opencontext_py.apps.ocitems.projects import views as ProjectViews
from opencontext_py.apps.ocitems.predicates import views as PredicateViews
from opencontext_py.apps.ocitems.octypes import views as OCtypeViews


urlpatterns = patterns('',
                       # Examples:
                       # url(r'^$', 'opencontext_py.views.home', name='home'),
                       # url(r'^blog/', include('blog.urls')),
                       # Subjects views for main records (subjects of observations)
                       url(r'^subjects/(?P<uuid>\S+).json', SubjectViews.json_view, name='subjects_json'),
                       url(r'^subjects/(?P<uuid>\S+)', SubjectViews.html_view, name='subjects_html'),
                       url(r'^subjects', SubjectViews.index, name='index'),
                       # Media views (media resources / metadata + binary files)
                       url(r'^media/(?P<uuid>\S+).json', MediaViews.json_view, name='media_json'),
                       url(r'^media/(?P<uuid>\S+)', MediaViews.html_view, name='media_html'),
                       url(r'^media', MediaViews.index, name='index'),
                       # Document views for HTML document items
                       url(r'^documents/(?P<uuid>\S+).json', DocumentViews.json_view, name='documents_json'),
                       url(r'^documents/(?P<uuid>\S+)', DocumentViews.html_view, name='documents_html'),
                       url(r'^documents', DocumentViews.index, name='index'),
                       # Person views for Person / organization items
                       url(r'^persons/(?P<uuid>\S+).json', PersonViews.json_view, name='json_view'),
                       url(r'^persons/(?P<uuid>\S+)', PersonViews.html_view, name='html_view'),
                       url(r'^persons', PersonViews.index, name='index'),
                       # Project views for projects
                       # url(r'^projects/(?P<uuid>\S+).json', ProjectViews.json_view, name='json_view'),
                       # url(r'^projects/(?P<uuid>\S+)', ProjectViews.html_view, name='html_view'),
                       # url(r'^projects', ProjectViews.index, name='index'),
                       # Predicates views for descriptive variables and linking relations from OC contributors
                       url(r'^predicates/(?P<uuid>\S+).json', PredicateViews.json_view, name='predicates_json'),
                       url(r'^predicates/(?P<uuid>\S+)', PredicateViews.html_view, name='predicates_html'),
                       url(r'^predicates', PredicateViews.index, name='index'),
                       # Types views for controlled vocabulary entities from OC contributors
                       url(r'^types/(?P<uuid>\S+).json', OCtypeViews.json_view, name='types_json'),
                       url(r'^types/(?P<uuid>\S+)', OCtypeViews.html_view, name='types_html'),
                       url(r'^types', OCtypeViews.index, name='index'),
                       # Admin route
                       url(r'^admin/', include(admin.site.urls)),
                       ) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
if settings.DEBUG:
    import debug_toolbar
    urlpatterns += patterns('',
                            url(r'^__debug__/', include(debug_toolbar.urls)),
                            )
