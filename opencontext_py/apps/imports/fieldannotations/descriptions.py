import uuid as GenUUID
from django.conf import settings
from django.db import models
from opencontext_py.libs.general import LastUpdatedOrderedDict
from opencontext_py.apps.ocitems.assertions.models import Assertion
from opencontext_py.apps.ocitems.manifest.models import Manifest
from opencontext_py.apps.ocitems.predicates.models import Predicate
from opencontext_py.apps.ocitems.predicates.management import PredicateManagement
from opencontext_py.apps.ocitems.octypes.models import OCtype
from opencontext_py.apps.ocitems.octypes.management import TypeManagement
from opencontext_py.apps.ocitems.strings.models import OCstring
from opencontext_py.apps.ocitems.strings.management import StringManagement
from opencontext_py.apps.entities.entity.models import Entity
from opencontext_py.apps.imports.fields.models import ImportField
from opencontext_py.apps.imports.fields.templating import ImportProfile
from opencontext_py.apps.imports.fieldannotations.models import ImportFieldAnnotation
from opencontext_py.apps.imports.records.models import ImportCell
from opencontext_py.apps.imports.records.process import ProcessCells
from opencontext_py.apps.imports.fieldannotations.general import ProcessGeneral
from opencontext_py.apps.imports.records.unimport import UnImport


# Processes to generate descriptions 
class ProcessDescriptions():

    def __init__(self, source_id):
        self.source_id = source_id
        pg = ProcessGeneral(source_id)
        pg.get_source()
        self.project_uuid = pg.project_uuid
        self.description_annotations = False
        self.des_rels = False
        self.start_row = 1
        self.batch_size = 250
        self.end_row = self.batch_size
        self.example_size = 5

    def clear_source(self):
        """ Clears a prior import if the start_row is 1.
            This makes sure new entities and assertions are made for
            this source_id, and we don't duplicate things
        """
        if self.start_row <= 1:
            # will clear an import of descriptions
            unimport = UnImport(self.source_id,
                                self.project_uuid)
            unimport.delete_descibe_assertions()
            unimport.delete_predicate_vars()
            unimport.delete_types_entities()
            unimport.delete_strings()
        return True

    def get_description_examples(self):
        """ Gets example entities described by other fields
        """
        example_entities = []
        self.get_description_annotations()
        if self.des_rels is not False:
            for subj_field_num, ent_obj in self.des_rels.items():
                # get some example records 
                pc = ProcessCells(self.source_id,
                                  self.start_row)
                distinct_records = pc.get_field_records(subj_field_num,
                                                        False)
                if distinct_records is not False:
                    entity_example_count = 0
                    # sort the list in row_order from the import table
                    distinct_records = self.order_distinct_records(distinct_records)
                    for row_key, dist_rec in distinct_records.items():
                        if entity_example_count < self.example_size:
                            # if we're less than the example size, make
                            # an example object
                            entity_example_count += 1
                            entity = LastUpdatedOrderedDict()
                            entity_label = dist_rec['imp_cell_obj'].record
                            if len(entity_label) < 1:
                                entity_label = '[BLANK]'
                            entity_label = ent_obj['field'].value_prefix + entity_label
                            entity['label'] = entity_label
                            entity['id'] = str(subj_field_num) + '-' + str(row_key)
                            entity['descriptions'] = []
                            example_rows = []
                            example_rows.append(dist_rec['rows'][0])
                            for des_field_obj in ent_obj['des_by_fields']:
                                des_item = LastUpdatedOrderedDict()
                                des_item['predicate'] = LastUpdatedOrderedDict()
                                # values are in a list, in case there are more than 1 (variable-value)
                                des_item['objects'] = []
                                des_item['predicate']['type'] = des_field_obj.field_type
                                if des_field_obj.field_type == 'description':
                                    # set the predicate for this description
                                    des_item['predicate']['label'] = des_field_obj.label
                                    des_item['predicate']['id'] = des_field_obj.field_num
                                    # now get a value for this description from the imported cells
                                    pc = ProcessCells(self.source_id,
                                                      self.start_row)
                                    val_recs = pc.get_field_records(des_field_obj.field_num,
                                                                    example_rows)
                                    val_rec = self.get_first_distinct_record(val_recs)
                                    if val_rec is not False:
                                        object_val = LastUpdatedOrderedDict()
                                        object_val['record'] = val_rec['imp_cell_obj'].record
                                        object_val['id'] = val_rec['rows'][0]
                                        des_item['objects'].append(object_val)
                                elif des_field_obj.field_type == 'variable':
                                    # need to get the predicate from the imported cells
                                    pc = ProcessCells(self.source_id,
                                                      self.start_row)
                                    var_recs = pc.get_field_records(des_field_obj.field_num,
                                                                    example_rows)
                                    var_rec = self.get_first_distinct_record(var_recs)
                                    if var_rec is not False:
                                        des_item['predicate']['label'] = var_rec['imp_cell_obj'].record
                                        pid = str(des_field_obj.field_num) + '-' + str(var_rec['rows'][0])
                                        des_item['predicate']['id'] = pid
                                        # now need to get fields that have object values for the predicate
                                        valueof_fields = self.get_variable_valueof(des_field_obj)
                                        for val_field_obj in valueof_fields:
                                            pc = ProcessCells(self.source_id,
                                                              self.start_row)
                                            val_recs = pc.get_field_records(val_field_obj.field_num,
                                                                            example_rows)
                                            val_rec = self.get_first_distinct_record(val_recs)
                                            if val_rec is not False:
                                                object_val = LastUpdatedOrderedDict()
                                                object_val['record'] = val_rec['imp_cell_obj'].record
                                                oid = str(val_field_obj.field_num) + '-' + str(val_rec['rows'][0])
                                                object_val['id'] = oid
                                                des_item['objects'].append(object_val)
                                entity['descriptions'].append(des_item)
                            example_entities.append(entity)
        return example_entities

    def process_description_batch(self):
        """ processes fields describing a subject (subjects, media, documents, persons, projects)
            entity field.
            if start_row is 1, then this makes new predicate entities
        """
        self.clear_source()  # clear prior import for this source
        self.end_row = self.start_row + self.batch_size
        self.get_description_annotations()
        if self.des_rels is not False:
            for subj_field_num, ent_obj in self.des_rels.items():
                # get records for the subject of the description
                pc = ProcessCells(self.source_id,
                                  self.start_row)
                distinct_records = pc.get_field_records(subj_field_num,
                                                        False)
                if distinct_records is not False:
                    distinct_records = self.order_distinct_records(distinct_records)
                    # loop through the fields that describe the subj_field_num
                    for des_field_obj in ent_obj['des_by_fields']:
                        if des_field_obj.field_type == 'description':
                            pass
                        elif des_field_obj.field_type == 'variable':
                            pass
                        pass
                    for row_key, dist_rec in distinct_records.items():
                        if dist_rec['imp_cell_obj'].cell_ok:
                            # the subject record is OK to use for creating
                            # description records
                            pass

    def get_description_annotations(self):
        """ Gets descriptive annotations, and a 
            or a list of fields that are not in containment relationships
        """
        self.description_annotations = ImportFieldAnnotation.objects\
                                                            .filter(source_id=self.source_id,
                                                                    predicate=ImportFieldAnnotation.PRED_DESCRIBES)\
                                                            .order_by('field_num')
        if len(self.description_annotations) > 0:
            self.des_rels = LastUpdatedOrderedDict()
            for des_anno in self.description_annotations:
                add_descriptor_field = False
                if des_anno.object_field_num not in self.des_rels:
                    # entities being described are in the field identified by object_field_num
                    field_obj = self.get_field_obj(des_anno.object_field_num)
                    if field_obj is not False:
                        if field_obj.field_type in ImportProfile.DEFAULT_SUBJECT_TYPE_FIELDS:
                            self.des_rels[des_anno.object_field_num] = LastUpdatedOrderedDict()
                            self.des_rels[des_anno.object_field_num]['field'] = field_obj
                            self.des_rels[des_anno.object_field_num]['des_by_fields'] = []
                            add_descriptor_field = True
                else:
                    add_descriptor_field = True
                if add_descriptor_field:
                    # the descriptive field is identified by the field_num
                    des_field_obj = self.get_field_obj(des_anno.field_num)
                    if des_field_obj is not False:
                        self.des_rels[des_anno.object_field_num]['des_by_fields'].append(des_field_obj)

    def order_distinct_records(self, distinct_records):
        """ returns distict records in their proper order """
        row_key_recs = {}
        row_key_list = []
        for rec_hash, dist_rec in distinct_records.items():
            row_key = dist_rec['rows'][0]
            row_key_recs[row_key] = dist_rec
            row_key_list.append(row_key)
        row_key_list = sorted(row_key_list)
        row_key_ordered_recs = LastUpdatedOrderedDict()
        for row_key in row_key_list:
            row_key_ordered_recs[row_key] = row_key_recs[row_key]
        return row_key_ordered_recs

    def get_first_distinct_record(self, distinct_records):
        """ returns the first distinct record dictionary object """
        output = False
        if distinct_records is not False:
            for rec_hash, dist_rec in distinct_records.items():
                output = dist_rec
                break
        return output

    def get_variable_valueof(self, des_field_obj):
        """ Checks to see if the des_by_field is a variable that has designated values """
        valueof_fields = []
        if des_field_obj.field_type == 'variable':
            # get list of field_nums that have the des_by_field as their object
            val_annos = ImportFieldAnnotation.objects\
                                             .filter(source_id=self.source_id,
                                                     predicate=ImportFieldAnnotation.PRED_VALUE_OF,
                                                     object_field_num=des_field_obj.field_num)\
                                             .order_by(field_num)
            if len(val_annos) > 1:
                for val_anno in val_annos:
                    val_obj = self.get_field_obj(val_anno.field_num)
                    if val_obj is not False:
                        if val_obj.field_type == 'value':
                            valueof_fields.append(val_obj)
        return valueof_fields

    def get_field_obj(self, field_num):
        """ Gets a field object based on a field_num """
        output = False
        f_objs = ImportField.objects\
                            .filter(source_id=self.source_id,
                                    field_num=field_num)[:1]
        if len(f_objs) > 0:
            output = f_objs[0]
        return output


class CandidateDescription():

    DEFAULT_BLANK = '[Blank]'

    def __init__(self):
        self.project_uuid = False
        self.source_id = False
        self.subject_uuid = False
        self.predicate_uuid = False
        self.object_uuid = False
        self.object_type = False
        self.data_num = False
        self.data_date = False


class CandidateDescriptivePredicate():
    """ Class for reconciling and generating a descriptive predicate """

    def __init__(self):
        self.label = False
        self.project_uuid = False
        self.source_id = False
        self.uuid = False
        self.data_type = False
        self.sort = 0
        self.candidate_uuid = False
        self.des_import_cell = False

    def setup_field(self, des_field_obj):
        """ sets up, with slightly different patterns for
            description field or a variable field
        """
        if des_field_obj.field_type == 'description':
            if self.label is False:
                self.label = des_field_obj.label
            if self.candidate_uuid is False:
                self.candidate_uuid = des_field_obj.f_uuid
        elif des_field_obj.field_type == 'variable':
            if self.des_import_cell is not False:
                if self.label is False:
                    self.label = self.des_import_cell.record
                if self.candidate_uuid is False:
                    self.candidate_uuid = self.des_import_cell.fl_uuid
        if self.project_uuid is False:
            self.project_uuid = des_field_obj.project_uuid
        if self.source_id is False:
            self.source_id = des_field_obj.source_id
        if self.data_type is False:
            self.data_type = des_field_obj.data_type
        if self.sort < 1:
            self.sort = des_field_obj.field_num

    def reconcile_predicate_var(self, des_field_obj):
        """ reconciles a predicate variable from the Import Field
        """
        output = False
        self.setup_field(des_field_obj)
        if len(self.label) > 0:
            output = True
            pm = PredicateManagement()
            pm.project_uuid = self.project_uuid
            pm.source_id = self.source_id
            pm.sort = self.sort
            pm.candidate_uuid = self.candidate_uuid
            predicate = pm.get_make_predicate(self.label,
                                              'variable',
                                              self.data_type)
            self.uuid = predicate.uuid
            if predicate.uuid != self.candidate_uuid:
                if self.des_import_cell is False:
                    # update the reconcilted UUID with for the import field object
                    des_field_obj.f_uuid = predicate.uuid
                    des_field_obj.save()
                else:
                    # update the reconcilted UUID for import cells with same rec_hash
                    up_cells = ImportCell.objects\
                                         .filter(source_id=self.source_id,
                                                 field_num=self.des_import_cell.field_num,
                                                 rec_hash=self.des_import_cell.rec_hash)
                    for up_cell in up_cells:
                        # save each cell with the correct UUID
                        up_cell.fl_uuid = self.uuid
                        up_cell.save()
        return output
