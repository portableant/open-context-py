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
from opencontext_py.apps.searcher.sets import views as SetsViews
from opencontext_py.apps.entities.entity import views as EntityViews
from opencontext_py.apps.edit.items import views as EditItemViews
from opencontext_py.apps.imports.sources import views as Imp_sources
from opencontext_py.apps.imports.fields import views as Imp_fields
from opencontext_py.apps.imports.fieldannotations import views as Imp_field_annos

urlpatterns = patterns('',
                       # Examples:
                       # url(r'^$', 'opencontext_py.views.home', name='home'),
                       # url(r'^blog/', include('blog.urls')),
                       # Subjects views for main records (subjects of observations)
                       url(r'^subjects/(?P<uuid>\S+).json', SubjectViews.json_view, name='subjects_json'),
                       url(r'^subjects/(?P<uuid>\S+)', SubjectViews.html_view, name='subjects_html'),
                       url(r'^subjects', SubjectViews.index, name='subjects_index'),
                       # Sets views
                       url(r'^sets/(?P<spatial_context>\S+)?.json', SetsViews.json_view, name='sets_json'),
                       url(r'^sets/(?P<spatial_context>\S+)?', SetsViews.html_view, name='sets_html'),
                       # Media views (media resources / metadata + binary files)
                       url(r'^media/(?P<uuid>\S+).json', MediaViews.json_view, name='media_json'),
                       url(r'^media/(?P<uuid>\S+)', MediaViews.html_view, name='media_html'),
                       url(r'^media', MediaViews.index, name='media_index'),
                       # Document views for HTML document items
                       url(r'^documents/(?P<uuid>\S+).json', DocumentViews.json_view, name='documents_json'),
                       url(r'^documents/(?P<uuid>\S+)', DocumentViews.html_view, name='documents_html'),
                       url(r'^documents', DocumentViews.index, name='documents_index'),
                       # Person views for Person / organization items
                       url(r'^persons/(?P<uuid>\S+).json', PersonViews.json_view, name='persons_json'),
                       url(r'^persons/(?P<uuid>\S+)', PersonViews.html_view, name='persons_html'),
                       url(r'^persons', PersonViews.index, name='persons_index'),
                       # Project views for projects
                       url(r'^projects/(?P<uuid>\S+).json', ProjectViews.json_view, name='projects_json'),
                       url(r'^projects/(?P<uuid>\S+)', ProjectViews.html_view, name='projects_html'),
                       url(r'^projects', ProjectViews.index, name='projects_index'),
                       # Predicates views for descriptive variables and linking relations from OC contributors
                       url(r'^predicates/(?P<uuid>\S+).json', PredicateViews.json_view, name='predicates_json'),
                       url(r'^predicates/(?P<uuid>\S+)', PredicateViews.html_view, name='predicates_html'),
                       url(r'^predicates', PredicateViews.index, name='predicates_index'),
                       # Types views for controlled vocabulary entities from OC contributors
                       url(r'^types/(?P<uuid>\S+).json', OCtypeViews.json_view, name='types_json'),
                       url(r'^types/(?P<uuid>\S+)', OCtypeViews.html_view, name='types_html'),
                       url(r'^types', OCtypeViews.index, name='types_index'),
                       # --------------------------
                       # IMPORTER INTERFACE PAGES
                       # --------------------------
                       url(r'^imports/project/(?P<project_uuid>\S+)',  Imp_sources.project,
                           name='imp_sources_project'),
                       url(r'^imports/field-types/(?P<source_id>\S+)', Imp_sources.field_types,
                           name='field_types'),
                       url(r'^imports/field-types-more/(?P<source_id>\S+)', Imp_sources.field_types_more,
                           name='field_types_more'),
                       url(r'^imports/field-entity-relations/(?P<source_id>\S+)', Imp_sources.field_entity_relations,
                           name='field_entity_relations'),
                       url(r'^imports/field-descriptions/(?P<source_id>\S+)', Imp_sources.field_descriptions,
                           name='field_descriptions'),
                       url(r'^imports/finalize/(?P<source_id>\S+)', Imp_sources.finalize,
                           name='imp_source_finalize'),
                       # --------------------------
                       # IMPORTER PROJECT POST REQUESTS
                       # --------------------------
                       url(r'^imports/create-project', Imp_sources.create_project,
                           name='imp_sources_create_project'),
                       url(r'^imports/edit-project/(?P<project_uuid>\S+)', Imp_sources.edit_project,
                           name='imp_sources_edit_project'),
                       # --------------------------
                       # BELOW ARE URLs FOR IMPORTER AJAX REQUESTS
                       # --------------------------
                       url(r'^imports/project-import-refine/(?P<project_uuid>\S+)', Imp_sources.project_import_refine,
                           name='imp_sources_project_import_refine'),
                       url(r'^imports/import-finalize/(?P<source_id>\S+)', Imp_sources.import_finalize,
                           name='imp_sources_import_finalize'),
                       url(r'^imports/field-classify/(?P<source_id>\S+)', Imp_fields.field_classify,
                           name='imp_field_classify'),
                       url(r'^imports/field-meta-update/(?P<source_id>\S+)', Imp_fields.field_meta_update,
                           name='imp_field_meta_update'),
                       url(r'^imports/field-list/(?P<source_id>\S+)', Imp_fields.field_list,
                           name='imp_field_list'),
                       url(r'^imports/field-annotations/(?P<source_id>\S+)', Imp_field_annos.view,
                           name='imp_field_annos_view'),
                       url(r'^imports/subjects-hierarchy-examples/(?P<source_id>\S+)', Imp_field_annos.subjects_hierarchy_examples,
                           name='imp_field_annos_subjects_hierarchy_examples'),
                       url(r'^imports/field-described-examples/(?P<source_id>\S+)', Imp_field_annos.described_examples,
                           name='imp_field_annos_described_examples'),
                       url(r'^imports/field-linked-examples/(?P<source_id>\S+)', Imp_field_annos.linked_examples,
                           name='imp_field_annos_linked_examples'),
                       url(r'^imports/field-annotation-delete/(?P<source_id>\S+)/(?P<annotation_id>\S+)', Imp_field_annos.delete,
                           name='imp_field_annos_delete'),
                       url(r'^imports/field-annotation-create/(?P<source_id>\S+)', Imp_field_annos.create,
                           name='imp_field_annos_create'),
                       # --------------------------
                       # BELOW IS THE INDEX PAGE FOR THE IMPORTER
                       # --------------------------
                       url(r'^imports/', Imp_sources.index,
                           name='imp_sources_index'),
                       # --------------------------
                       # BELOW ARE URLs FOR ENTITY EDITS INTERFACE PAGES
                       # --------------------------
                       url(r'^edit/items/(?P<uuid>\S+)', EditItemViews.html_view,
                           name='edit_item_html_view'),
                       # --------------------------
                       # BELOW ARE URLs FOR ENTITY EDITS AJAX REQUESTS
                       # --------------------------
                       url(r'^edit/update-item/(?P<uuid>\S+)', EditItemViews.update_item,
                           name='edit_update_item'),
                       # --------------------------
                       # BELOW ARE URLs FOR ENTITY LOOKUP AJAX REQUESTS
                       # --------------------------
                       url(r'^entities/hierarchy-children/(?P<identifier>\S+)', EntityViews.hierarchy_children,
                           name='entity_hierarchy_children'),
                       url(r'^entities/look-up/(?P<item_type>\S+)', EntityViews.look_up,
                           name='entity_look_up'),
                       # Admin route
                       # Admin route
                       url(r'^admin/', include(admin.site.urls)),
                       ) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
if settings.DEBUG:
    import debug_toolbar
    urlpatterns += patterns('',
                            url(r'^__debug__/', include(debug_toolbar.urls)),
                            )
