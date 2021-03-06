import re
import json
import geojson
from django.conf import settings
from geojson import Feature, Point, Polygon, GeometryCollection, FeatureCollection
from urllib.parse import urlparse, parse_qs
from django.utils.http import urlquote, quote_plus, urlquote_plus
from opencontext_py.libs.isoyears import ISOyears
from opencontext_py.libs.general import LastUpdatedOrderedDict
from opencontext_py.libs.globalmaptiles import GlobalMercator
from opencontext_py.apps.searcher.solrsearcher.filterlinks import FilterLinks


class GeoJsonRegions():

    def __init__(self, solr_json):
        self.geojson_regions = []
        self.total_found = False
        self.filter_request_dict_json = False
        self.spatial_context = False
        self.aggregation_depth = 6
        # max precision of tiles in the current filtered set
        self.max_tile_precision = 0
        self.max_depth = 20
        self.result_depth = self.aggregation_depth
        self.min_date = False
        self.max_date = False
        try:
            self.total_found = solr_json['response']['numFound']
        except KeyError:
            self.total_found = False

    def process_solr_tiles(self, solr_tiles):
        """ processes the solr_json 
            discovery geo tiles,
            aggregating to a certain
            depth
        """
        # first aggregate counts for tile that belong togther
        aggregate_tiles = self.aggregate_spatial_tiles(solr_tiles)
        # now generate GeoJSON for each tile region
        # print('Total tiles: ' + str(t) + ' reduced to ' + str(len(aggregate_tiles)))
        i = 0
        for tile_key, aggregate_count in aggregate_tiles.items():
            i += 1
            add_region = True
            fl = FilterLinks()
            fl.base_request_json = self.filter_request_dict_json
            fl.spatial_context = self.spatial_context
            new_rparams = fl.add_to_request('disc-geotile',
                                            tile_key)
            record = LastUpdatedOrderedDict()
            record['id'] = fl.make_request_url(new_rparams)
            record['json'] = fl.make_request_url(new_rparams, '.json')
            record['count'] = aggregate_count
            record['type'] = 'Feature'
            record['category'] = 'oc-api:geo-facet'
            if self.min_date is not False \
               and self.max_date is not False:
                when = LastUpdatedOrderedDict()
                when['id'] = '#event-' + tile_key
                when['type'] = 'oc-gen:formation-use-life'
                # convert numeric to GeoJSON-LD ISO 8601
                when['start'] = ISOyears().make_iso_from_float(self.min_date)
                when['stop'] = ISOyears().make_iso_from_float(self.max_date)
                record['when'] = when
            gm = GlobalMercator()
            geo_coords = gm.quadtree_to_geojson_poly_coords(tile_key)
            geometry = LastUpdatedOrderedDict()
            geometry['id'] = '#geo-disc-tile-geom-' + tile_key
            geometry['type'] = 'Polygon'
            geometry['coordinates'] = geo_coords
            record['geometry'] = geometry
            properties = LastUpdatedOrderedDict()
            properties['id'] = '#geo-disc-tile-' + tile_key
            properties['href'] = record['id']
            properties['label'] = 'Discovery region (' + str(i) + ')'
            properties['feature-type'] = 'discovery region (facet)'
            properties['count'] = aggregate_count
            properties['early bce/ce'] = self.min_date
            properties['late bce/ce'] = self.max_date
            record['properties'] = properties
            if len(tile_key) >= 6:
                if tile_key[:6] == '211111':
                    # no bad coordinates (off 0, 0 coast of Africa)
                    add_region = False  # don't display items without coordinates
            if add_region:
                self.geojson_regions.append(record)

    def set_aggregation_depth(self, request_dict_json):
        """ sets the aggregatin depth for
            aggregating geospatial tiles

            aggregation depth varies between 3 and 20
            with 20 being the most fine-grain, specific
            level of spatial depth
        """
        # now set up for filter requests, by removing the
        request_dict = json.loads(request_dict_json)
        filter_request_dict = request_dict
        if 'geodeep' in request_dict:
            deep = request_dict['geodeep'][0]
            # filter out non numeric characters
            deep = re.sub(r'[^0-9]', r'', deep)
            if len(deep) > 0:
                self.aggregation_depth = int(float(deep))
        if 'disc-geotile' in request_dict:
            req_param_tile = request_dict['disc-geotile'][0]
            req_param_tile = re.sub(r'\|', r'', req_param_tile)  # strip ors
            self.aggregation_depth += len(req_param_tile)
            filter_request_dict.pop('disc-geotile', None) # so as to set up for filter links
        if self.aggregation_depth < 3:
            self.aggregation_depth = 3
        elif self.aggregation_depth > self.max_depth:
            self.aggregation_depth = self.max_depth
        # now make sure we've got a 'clean' request dict
        # to make filter links
        self.filter_request_dict_json = json.dumps(filter_request_dict,
                                                   ensure_ascii=False,
                                                   indent=4)
        self.result_depth = self.aggregation_depth
        return self.aggregation_depth

    def aggregate_spatial_tiles(self, solr_tiles, aggregation_depth=False):
        """ Aggregates tiles to a depth that gives multiple tiles, since single tile maps
            are not very useful
        """
        if aggregation_depth is False:
            aggregation_depth = self.aggregation_depth
        aggregate_tiles = {}
        i = -1
        t = 0
        all_tile_lens = []
        for tile_key in solr_tiles[::2]:
            t += 1
            i += 2
            solr_facet_count = solr_tiles[i]
            # to compute the main tile precision level
            # for this filtered set of data
            if tile_key[:6] != '211111':
                # a bit of a hack to exclude display of
                # erroroneous data without spatial reference
                tile_key_len = len(tile_key)
                if tile_key_len > 6:
                    all_tile_lens.append(tile_key_len)
                trim_tile_key = tile_key[:aggregation_depth]
                if trim_tile_key not in aggregate_tiles:
                    aggregate_tiles[trim_tile_key] = 0
                aggregate_tiles[trim_tile_key] += solr_facet_count
        if len(all_tile_lens) > 0:
            # gets the average tile depth, so clients don't over-zoom
            mean_tile_len = sum(all_tile_lens) / len(all_tile_lens)
            # print(str(mean_tile_len))
            self.max_tile_precision = round(mean_tile_len)
        if aggregation_depth != self.aggregation_depth:
            self.aggregation_depth = aggregation_depth
            self.result_depth = self.aggregation_depth
        # print('Num tiles: ' + str(len(aggregate_tiles)))
        if len(aggregate_tiles) < 2:
            # only 1 tile, aggregate at a greater depth
            aggregation_depth += 3
            if aggregation_depth <= self.max_depth:
                aggregate_tiles = self.aggregate_spatial_tiles(solr_tiles,
                                                               aggregation_depth)
        return aggregate_tiles

    def make_url_from_val_string(self,
                                 partial_url,
                                 use_cannonical=True):
        """ parses a solr value if it has
            '___' delimiters, to get the URI part
            string.
            if it's already a URI part, it makes
            a URL
        """
        if use_cannonical:
            base_url = settings.CANONICAL_HOST
        else:
            base_url = settings.DEPLOYED_HOST
            if settings.DEBUG:
                base_url = 'http://127.0.0.1:8000'
        solr_parts = self.parse_solr_value_parts(partial_url)
        if isinstance(solr_parts, dict):
            partial_url = solr_parts['uri']
        if 'http://' not in partial_url \
           and 'https://' not in partial_url:
            url = base_url + partial_url
        else:
            url = partial_url
        return url

    def parse_solr_value_parts(self, solr_value):
        """ parses a solr_value string into
            slug, solr-data-type, uri, and label
            parts
        """
        output = False
        if '___' in solr_value:
            solr_ex = solr_value.split('___')
            if len(solr_ex) == 4:
                output = {}
                output['slug'] = solr_ex[0]
                output['data_type'] = solr_ex[1]
                output['uri'] = solr_ex[2]
                output['label'] = solr_ex[3]
        return output

    def get_key_val(self, key, dict_obj):
        """ returns the value associated
            with a key, if the key exists
            else, none
        """
        output = None
        if isinstance(dict_obj, dict):
            if key in dict_obj:
                output = dict_obj[key]
        return output
