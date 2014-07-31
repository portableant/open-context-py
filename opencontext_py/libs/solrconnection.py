import sys
import requests
from mysolr import Solr


class SolrConnection():
    '''
    Provides a connection to our Solr instance. This is useful for both
    crawling and searching.
    '''
    def __init__(self, solr_host='localhost', solr_port='8983'):
        self.session = requests.Session()
        solr_connection_string = 'http://' + solr_host + ':' + solr_port \
            + '/solr'
        try:
            self.connection = Solr(solr_connection_string,
                                   make_request=self.session)
        except requests.ConnectionError:
            print('\nError: Could not connect to Solr. Please '
                  'verify your Solr instance and configuration.\n')
            sys.exit(1)