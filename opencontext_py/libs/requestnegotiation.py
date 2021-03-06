#!/usr/bin/env python
from django.conf import settings


class RequestNegotiation():
    """ Useful methods for Open Context 
        to do some simple content negotiation
    """

    def __init__(self, default_type):
        self.default_type = default_type  # the default mime-type supported
        self.supported_types = []  # other types supported
        self.supported = True
        self.use_response_type = default_type  # use this response type
        self.error_message = False

    def check_request_support(self, raw_client_accepts):
        """ check to see if the client_accepts
            mimetypes are supported by
            this part of Open Context
        """
        client_accepts = str(raw_client_accepts)
        if '*/*' in client_accepts:
            # client happy to accept all
            self.use_response_type = self.default_type
        elif 'text/*' in client_accepts \
             and 'text/' in self.default_type:
            self.use_response_type = self.default_type
        elif self.default_type in client_accepts:
            # client accepts our default
            self.use_response_type = self.default_type
        else:
            # a more selective client, probably wanting
            # a machine-readable representation
            self.use_response_type = False
            client_accepts_len = len(client_accepts)
            for support_type in self.supported_types:
                # print('Support type: ' + str(support_type) + ' in ' + client_accepts)
                if len(support_type) <= client_accepts_len:
                    if support_type == client_accepts:
                        # we do support the alternative
                        self.use_response_type = support_type
                    elif support_type in client_accepts:
                        self.use_response_type = support_type
            if self.use_response_type is False:
                # client wants what we don't support
                self.supported = False
                self.use_response_type = 'text/plain'
                self.error_message = 'This resource not available in the requested mime-type: '
                self.error_message += client_accepts + '\n\n '
                self.error_message += 'The following representations are supported: \n '
                self.error_message += self.default_type + '; \n '
                self.error_message += '; \n '.join(self.supported_types)
