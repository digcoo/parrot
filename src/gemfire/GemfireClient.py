'''
Copyright (c) 2014 Pivotal Software, Inc.  All Rights Reserved.
Licensed under the Apache License, Version 2.0 (the "License"); 
you may not use this file except in compliance with the License. 
You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0.
Unless required by applicable law or agreed to in writing, software distributed under the License 
is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  
See the License for the specific language governing permissions and limitations under the License.
'''


from datetime import datetime
from gemfire.Repository import *

class GemfireClient:
    '''
    Allows application to store and access data stored in GemFire over REST. Please see:
    http://gemfire.docs.pivotal.io/latest/userguide/index.html#gemfire_rest/setup_config.html
    for instructions on setting up GemFire's REST service.
    '''

    def __init__(self, hostname, port, debug_mode=False):
        '''Initializes the Client with the given hostname and port'''
        self.hostname = hostname
        self.port = port
        self.base_url = "http://" + hostname + ":" + str(port) + "/gemfire-api/v1/"
        if debug_mode:
            logging.basicConfig(filename=(datetime.now().strftime('pyrest_%H_%M_%d_%m_%Y.log')), level=logging.DEBUG,
                                format=(
                                    '%(filename)s: ''%(levelname)s: ''%(funcName)s(): ''%(lineno)d:\t''%(message)s'))
            logging.info('Started Client')
        self.session = requests.Session()
        self.connection()

    def connection(self):
        ''' Checks connection to the server '''
        data = self.session.get(self.base_url)
        if data.status_code == 200:
            logging.info("Client successfully connected to server at " + self.hostname)
            return True
        else:
            self.error_response(data)

    def list_all_regions(self):
        ''' Lists all names of Regions present in the server '''
        data = self.session.get(self.base_url)
        logging.debug("Sending request to " + self.base_url)
        fdata = jsonpickle.decode(data.text)
        rnames = fdata['regions']
        names = [region['name'] for region in rnames]
        if data.status_code == 200:
            logging.debug("Response from server: " + str(data))
            return names
        else:
            self.error_response(data)

    def create_repository(self, name):
        ''' Initializes and returns a Repository Object '''
        data = self.session.get(self.base_url).json()
        logging.debug("Sending request to " + self.base_url)
        rnames = data['regions']
        names = [region['name'] for region in rnames]
        for n in names:
            if n == name:
                logging.debug("Returned back Repository object for " + name)
                type = rnames[names.index(name)]["type"]
                return Repository(name, self.base_url, type)
        else:
            logging.debug("Repository " + name + " does not exist in the server")
            return False

    def list_all_queries(self):
        ''' Lists all stored Queries in the server '''
        data = self.session.get(self.base_url + "/queries")
        logging.debug("Sending request to " + self.base_url + "/queries")
        fdata = jsonpickle.decode(data.text)
        if data.status_code == 200:
            logging.debug("Response from server: " + str(data))
            return fdata["queries"]
        else:
            self.error_response(data)

    def run_query(self, query_id, query_args):
        ''' Runs the Query with specified parameters '''
        args = "{" + "'args:'" + " [" + str(query_args) + "]}"
        url = self.base_url + "queries/" + query_id
        headers = {'content-type': 'application/json'}
        jvalue = jsonpickle.encode(args)
	print jvalue
        data = self.session.post(url, data=jvalue, headers=headers)
        logging.debug("Sending request to " + url)
        if data.status_code == 200:
            logging.debug("Response from server: " + str(data))
            return jsonpickle.decode(data.text)
        else:
            self.error_response(data)

    def my_query(self, query_id, query_args, args_types):
        ''' Runs the Query with specified parameters '''
	params = []
	for i in range(0, len(query_args)):
	    dict_p = {}
	    dict_p['@type'] = args_types[i]
	    dict_p['@value'] = query_args[i]
	    params.append(dict_p)
	
        url = self.base_url + "queries/" + query_id
        headers = {'content-type': 'application/json'}
        jvalue = jsonpickle.encode(params)
#        print jvalue
        data = self.session.post(url, data=jvalue, headers=headers)
        logging.debug("Sending request to " + url)
        if data.status_code == 200:
            logging.debug("Response from server: " + str(data))
            return jsonpickle.decode(data.text)
        else:
            self.error_response(data)


    def new_query(self, query_id, query_string):
        ''' Creates a new Query and adds it to the server '''
        url = self.base_url + "/queries?id=" + str(query_id) + "&q=" + str(query_string)
        headers = {'content-type': 'application/json'}
        jvalue = jsonpickle.encode(query_string)
        data = self.session.post(url, data=jvalue, headers=headers)
        logging.debug("Sending request to " + url)
        if data.status_code == 201:
            logging.debug("Query " + query_id + " was successfully added to the server")
            return True
        else:
            self.error_response(data)

    def adhoc_query(self, query_string):
        ''' Runs an adhoc Query '''
        url = self.base_url + "queries/adhoc?q=" + str(query_string)
        data = self.session.get(url)
        logging.debug("Sending request to " + url)
        if data.status_code == 200:
            logging.debug("Response from server: " + str(data))
            return jsonpickle.decode(data.text)
        else:
            self.error_response(data)

    def list_all_functions(self):
        ''' List all stored function ID's stored on server '''
        url = self.base_url + "functions"
        data = self.session.get(url)
        logging.debug("Sending request to " + url)
        if data.status_code == 200:
            logging.debug("Response from server: " + str(data))
            return jsonpickle.decode(data.text)
        else:
            self.error_response(data)

    def execute_function(self, region_name, func_id, value):
        ''' Run function '''
        url = self.base_url + "functions/" + str(func_id) + "?onRegion=" + str(region_name)
        headers = {'content-type': 'application/json'}
        jvalue = jsonpickle.encode(value)
        data = self.session.post(url, data=jvalue, headers=headers)
        logging.debug("Sending request to " + url)
        if data.status_code == 200:
            logging.debug("Response from server: " + str(data))
            return jsonpickle.decode(data.text)
        else:
            self.error_response(data)

    def error_response(self, data):
        ''' Processes HTTP error responses '''
        logging.debug("Response from server: " + str(data.status_code) + " " + data.reason + " - " + data.text)
        return False
