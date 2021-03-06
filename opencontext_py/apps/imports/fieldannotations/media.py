import uuid as GenUUID
from django.conf import settings
from django.db import models
from opencontext_py.libs.general import LastUpdatedOrderedDict
from opencontext_py.apps.ocitems.manifest.models import Manifest
from opencontext_py.apps.ocitems.mediafiles.models import Mediafile
from opencontext_py.apps.imports.fields.models import ImportField
from opencontext_py.apps.imports.fieldannotations.models import ImportFieldAnnotation
from opencontext_py.apps.imports.records.models import ImportCell
from opencontext_py.apps.imports.records.process import ProcessCells
from opencontext_py.apps.imports.fieldannotations.general import ProcessGeneral
from opencontext_py.apps.imports.sources.unimport import UnImport


# Processes to generate media items for an import
class ProcessMedia():

    def __init__(self, source_id):
        self.source_id = source_id
        pg = ProcessGeneral(source_id)
        pg.get_source()
        self.project_uuid = pg.project_uuid
        self.media_fields = []
        self.start_row = 1
        self.batch_size = settings.IMPORT_BATCH_SIZE
        self.end_row = self.batch_size
        self.count_active_fields = 0
        self.new_entities = []
        self.reconciled_entities = []
        self.not_reconciled_entities = []

    def clear_source(self):
        """ Clears a prior import if the start_row is 1.
            This makes sure new entities and assertions are made for
            this source_id, and we don't duplicate things
        """
        if self.start_row <= 1:
            # get rid of "subjects" related assertions made from this source
            unimport = UnImport(self.source_id,
                                self.project_uuid)
            unimport.delete_media_entities()

    def process_media_batch(self):
        """ process media items
        """
        self.clear_source()  # clear prior import for this source
        self.end_row = self.start_row + self.batch_size
        self.get_media_fields()
        if len(self.media_fields) > 0:
            for field_obj in self.media_fields:
                pc = ProcessCells(self.source_id,
                                  self.start_row)
                distinct_records = pc.get_field_records(field_obj.field_num,
                                                        False)
                if distinct_records is not False:
                    for rec_hash, dist_rec in distinct_records.items():
                        # print('Checking on: ' + dist_rec['imp_cell_obj'].record)
                        cm = CandidateMedia()
                        cm.project_uuid = self.project_uuid
                        cm.source_id = self.source_id
                        cm.class_uri = field_obj.field_value_cat
                        cm.import_rows = dist_rec['rows']  # list of rows where this record value is found
                        cm.reconcile_manifest_item(dist_rec['imp_cell_obj'])
                        if cm.uuid is not False:
                            if cm.new_entity:
                                self.new_entities.append({'id': str(cm.uuid),
                                                          'label': cm.label})
                            else:
                                self.reconciled_entities.append({'id': str(cm.uuid),
                                                                 'label': cm.label})
                            # we have a media item! Now we can add files to it
                            for part_field_obj in field_obj.parts:
                                pc = ProcessCells(self.source_id,
                                                  self.start_row)
                                part_dist_records = pc.get_field_records(part_field_obj.field_num,
                                                                         cm.import_rows)
                                if part_dist_records is not False:
                                    for rec_hash, part_dist_rec in part_dist_records.items():
                                        # distinct records for the media file parts of a media item
                                        cmf = CandidateMediaFile(cm.uuid)
                                        cmf.project_uuid = self.project_uuid
                                        cmf.source_id = self.source_id
                                        # file type is in the field_value_cat
                                        cmf.file_type = part_field_obj.field_value_cat
                                        file_uri = part_dist_rec['imp_cell_obj'].record
                                        cmf.reconcile_media_file(file_uri)
                        else:
                            bad_id = str(dist_rec['imp_cell_obj'].field_num)
                            bad_id += '-' + str(dist_rec['imp_cell_obj'].row_num)
                            self.not_reconciled_entities.append({'id': bad_id,
                                                                 'label': dist_rec['imp_cell_obj'].record})

    def get_media_fields(self):
        """ Makes a list of media fields that have media parts
        """
        part_of = ImportFieldAnnotation.PRED_MEDIA_PART_OF
        media_fields = []
        raw_media_fields = ImportField.objects\
                                      .filter(source_id=self.source_id,
                                              field_type='media')
        for media_field_obj in raw_media_fields:
            part_of_field = ImportFieldAnnotation.objects\
                                                 .filter(predicate=part_of,
                                                         object_field_num=media_field_obj.field_num)\
                                                 .values_list('field_num')
            if len(part_of_field) > 0:
                part_fields = ImportField.objects\
                                         .filter(source_id=self.source_id,
                                                 field_type='media',
                                                 field_num__in=part_of_field)
                media_field_obj.parts = part_fields
                media_fields.append(media_field_obj)
        if len(media_fields) > 0:
            self.media_fields = media_fields
        return self.media_fields


class CandidateMedia():

    def __init__(self):
        self.project_uuid = False
        self.source_id = False
        self.class_uri = 'oc-gen:image'  # default to a image
        self.label = False
        self.uuid = False  # final, uuid for the item
        self.imp_cell_obj = False  # ImportCell object
        self.import_rows = False
        self.new_entity = False

    def reconcile_manifest_item(self, imp_cell_obj):
        """ Checks to see if the item exists in the manifest """
        self.imp_cell_obj = imp_cell_obj
        if len(imp_cell_obj.record) > 0:
            self.label = imp_cell_obj.record
        if self.label is not False:
            match_found = self.match_against_manifest(self.label)
            if match_found is False:
                # create new subject, manifest objects. Need new UUID, since we can't assume
                # the fl_uuid for the ImportCell reflects unique entities in a field, since
                # uniqueness depends on context (values in other cells)
                self.new_entity = True
                self.uuid = GenUUID.uuid4()
                self.create_media_item()
        self.update_import_cell_uuid()

    def create_media_item(self):
        """ Create and save a new subject object"""
        new_man = Manifest()
        new_man.uuid = self.uuid
        new_man.project_uuid = self.project_uuid
        new_man.source_id = self.source_id
        new_man.item_type = 'media'
        new_man.repo = ''
        new_man.class_uri = self.class_uri
        new_man.label = self.label
        new_man.des_predicate_uuid = ''
        new_man.views = 0
        new_man.save()

    def update_import_cell_uuid(self):
        """ Saves the uuid to the import cell record """
        if self.uuid is not False:
            if self.imp_cell_obj.fl_uuid != self.uuid:
                up_cells = ImportCell.objects\
                                     .filter(source_id=self.source_id,
                                             field_num=self.imp_cell_obj.field_num,
                                             rec_hash=self.imp_cell_obj.rec_hash)
                for up_cell in up_cells:
                    # save each cell with the correct UUID
                    up_cell.fl_uuid = self.uuid
                    up_cell.cell_ok = True
                    up_cell.save()

    def match_against_manifest(self, label):
        """ Checks to see if the item exists in the subjects table """
        match_found = False
        media_objs = Manifest.objects\
                             .filter(project_uuid=self.project_uuid,
                                     item_type='media',
                                     label=label)[:1]
        if len(media_objs) > 0:
            match_found = True
            self.uuid = media_objs[0].uuid
        return match_found


class CandidateMediaFile():

    def __init__(self, uuid):
        self.uuid = uuid
        self.project_uuid = False
        self.source_id = False
        self.file_type = False
        self.file_uri = False  
        self.new_entity = False

    def reconcile_media_file(self, file_uri):
        """ Checks to see if the item exists in the manifest """
        media_list = Mediafile.objects\
                              .filter(file_uri=file_uri)[:1]
        if len(media_list) < 1:
            self.file_uri = file_uri
            if self.validate_media_file():
                self.new_entity = True
                self.create_media_file()           

    def validate_media_file(self):
        """ validates data for creating a media file """
        is_valid = True
        if not isinstance(self.file_type, str):
            is_valid = False
        if not isinstance(self.file_uri, str):
            is_valid = False
        return is_valid

    def create_media_file(self):
        """ Create and save a new media file object"""
        mf = Mediafile()
        mf.uuid = self.uuid
        mf.project_uuid = self.project_uuid
        mf.source_id = self.source_id
        mf.file_type = self.file_type
        mf.file_uri = self.file_uri
        mf.filesize = 0
        mf.mime_type_ur = ''
        mf.save()