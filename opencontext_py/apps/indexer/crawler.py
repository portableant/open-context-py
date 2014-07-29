import time
from itertools import islice
from opencontext_py.libs.solrconnection import SolrConnection
from opencontext_py.libs.crawlerutilites import CrawlerUtilities as crawlutil
from opencontext_py.apps.indexer.uuidlist import UUIDList
from opencontext_py.apps.indexer.solrdocument import SolrDocument


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
                        documents.append(solrdocument)
                        document_count += 1
                        print("(" + str(document_count) + ")\t" + uuid)
                    else:
                        print('Error: Skipping document due to a datatype '
                              'mismatch -----> ' + uuid)
                except Exception as error:
                    print("Error: {0}".format(error) + " -----> " + uuid)
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
