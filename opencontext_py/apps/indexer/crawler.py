import time
from datetime import datetime
from itertools import islice
from django.conf import settings
import logging
from opencontext_py.libs.solrconnection import SolrConnection
from opencontext_py.libs.crawlerutilites import CrawlerUtilities as crawlutil
from opencontext_py.apps.indexer.uuidlist import UUIDList
from opencontext_py.apps.indexer.solrdocument import SolrDocument
from opencontext_py.apps.ocitems.manifest.models import Manifest


class Crawler():
    '''
    The Open Context Crawler indexes Open Context items and makes them
    searchable in Apache Solr.
    '''
    def __init__(self):
        '''
        To use, import this library and instantiate a crawler object:

        crawler = Crawler()

        Then crawl as follows:

        crawler.crawl()

        Crawling a single document is also supported with the
        index_single_document method. Just provide the document's UUID.
        For example:

        crawler.index_single_document('9E474B89-E36B-4B9D-2D38-7C7CCBDBB030')
        '''
        # The list of Open Context items to crawl
        self.uuidlist = UUIDList().uuids
        # Connect to Solr
        self.solr = SolrConnection().connection

    def crawl(self, chunksize=100):
        '''
        For efficiency, this method processes documents in "chunks." The
        default chunk size is 100, but one can specify other values. For
        example, to specify a chunksize of 500, use this method as follows:

        crawler = Crawler()
        crawler.crawl(500)
        '''

        # Get a logger
        logger = logging.getLogger(__name__)

        start_time = time.time()
        print('\n\nStarting crawl...\n')
        print("(#)\tUUID")
        print('--------------------------------------------')
        document_count = 0
        while self.uuidlist is not None:
            documents = []
            # Process the UUID list in chunks
            for uuid in islice(self.uuidlist, 0, chunksize):
                try:
                    solrdocument = SolrDocument(uuid).fields
                    if crawlutil().is_valid_document(solrdocument):
                        try:
                            manifest = Manifest.objects.get(uuid=uuid)
                            manifest.indexed_save()  # saves the time this was indexed
                        except Manifest.DoesNotExist:
                            print("Error: {0} Database bizzare error -----> " + uuid)
                            logger.error('[' + datetime.now().strftime('%x %X ') +
                                         settings.TIME_ZONE + '] Error: Missing manifest record for => ' + uuid)
                        documents.append(solrdocument)
                        document_count += 1
                        print("(" + str(document_count) + ")\t" + uuid)
                    else:
                        print('Error: Skipping document due to a datatype '
                              'mismatch -----> ' + uuid)
                except Exception as error:
                    print("Error: {0}".format(error) + " -----> " + uuid)
                    logger.error('[' + datetime.now().strftime('%x %X ') +
                                 settings.TIME_ZONE + '] Error: ' + str(error)
                                 + ' => ' + uuid)
            # Send the documents to Solr while saving the
            # response status code (e.g, 200, 400, etc.)
            solr_status = self.solr.update(documents, 'json',
                                           commit=False).status
            if solr_status == 200:
                self.solr.commit()
                print('--------------------------------------------')
                print('Crawl Rate: ' + crawlutil().get_crawl_rate_in_seconds(
                    document_count, start_time) + ' documents per second')
                print('--------------------------------------------')
            else:
                print('Error: ' + str(self.solr.update(
                    documents, 'json', commit=False
                    ).raw_content['error']['msg']))
        # Once the crawl has completed...
        self.solr.optimize()
        print('\n--------------------------------------------')
        print('Crawl completed')
        print('--------------------------------------------\n')

    def index_document_list(self,
                            uuid_list,
                            chunksize=20,
                            stop_at_invalid=True):
        """
        Indexes a list of uuids. The list is generated elsewhere.
        """
        if isinstance(uuid_list, list):
            document_count = 0
            documents = []
            total_count = len(uuid_list)
            i = 0;
            for uuid in uuid_list:
                try:
                    manifest = Manifest.objects.get(uuid=uuid)
                except Manifest.DoesNotExist:
                    print('Where is ' + uuid + ' in the manifest?')
                    manifest = False
                if manifest is not False:
                    try:
                        solrdocument = SolrDocument(uuid).fields
                        if crawlutil().is_valid_document(solrdocument):
                            i += 1
                            print('OK to index: ' + uuid)
                            documents.append(solrdocument)
                            manifest.indexed_save()  # saves the time this was indexed
                        else:
                            print('Not valid: ' + uuid )
                            if stop_at_invalid:
                                break
                    except Exception as error:
                        print("Error: {0}".format(error) + " -----> " + uuid)
                        if stop_at_invalid:
                                break
                if len(documents) >= chunksize:
                    ok = self.commit_documents(documents, i, total_count)
                    if ok is False and stop_at_invalid:
                        # a problem in committing the documents
                        break
                    documents = []
            # now finish off the remaining documents
            if len(documents) > 0:
                ok = self.commit_documents(documents, i, total_count)

    def commit_documents(self,
                         documents,
                         last_index=False,
                         total_docs=False):
        """ commits a set of documents to the Solr index """
        ok = False
        solr_status = self.solr.update(documents, 'json',
                                       commit=False).status
        if solr_status == 200:
            last_message = ''
            if last_index is not False and total_docs is not False:
                last_message = '(' + str(last_index) + ' of ' + str(total_docs) + ')'
            ok = True
            self.solr.commit()
            print('--------------------------------------------')
            print('Committed : ' + str(len(documents)) + ' docs. ' + last_message)
            print('--------------------------------------------')
        else:
            print('Error: ' + \
                  str(self.solr.update(
                  documents, 'json', commit=False
                  ).raw_content['error']['msg']))
        return ok

    def index_single_document(self, uuid):
        '''
        Use this method to crawl a single document. Provide the item's
        UUID as an argument. For example:

        crawler = Crawler()
        crawler.index_single_document('9E474B89-E36B-4B9D-2D38-7C7CCBDBB030')
        '''
        print('\nAttempting to index document ' + uuid + '...\n')
        start_time = time.time()
        try:
            solrdocument = SolrDocument(uuid).fields
            if crawlutil().is_valid_document(solrdocument):
                # Commit the document and save the response status.
                # Note: solr.update() expects a list
                solr_status = self.solr.update(
                    [solrdocument], 'json', commit=True).status
                if solr_status == 200:
                    print('Successfully indexed ' + uuid + ' in ' +
                          crawlutil().get_elapsed_time_in_seconds(start_time)
                          + ' seconds.')
                else:
                    print('Error: ' + str(self.solr.update(
                        [solrdocument], 'json', commit=True
                        ).raw_content['error']['msg'])
                    )
            else:
                print('Error: Unable to index ' + uuid + ' due to '
                      'a datatype mismatch.')
        except TypeError:
            print("Error: Unable to process document " + uuid + '.')
        except Exception as error:
            print("Error: {0}".format(error) + " -----> " + uuid)
