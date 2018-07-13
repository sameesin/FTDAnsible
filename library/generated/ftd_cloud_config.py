#!/usr/bin/python

# Copyright (c) 2018 Cisco Systems, Inc.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'network'}

DOCUMENTATION = """
---
module: ftd_cloud_config
short_description: Manages CloudConfig objects on Cisco FTD devices
version_added: "2.7"
author: "Cisco Systems, Inc."
options:
  operation:
    description:
      - Specified the name of the operation to execute in the task.
    required: true
  register_as:
    description:
      - Specifies Ansible fact name that is used to register received response from the FTD device.
  enableAutomaticUpdates
    description:
      - A Boolean value, TRUE or FALSE (the default). The TRUE value indicates that the device will automatically download URL category and reputation updates.
  filter
    description:
      - The criteria used to filter the models you are requesting. It should have the following format: {field}{operator}{value}[;{field}{operator}{value}]. Supported operators are: "!"(not equals), ":"(equals), "<"(null), "~"(similar), ">"(null). Supported fields are: "name".
  id
    description:
      - A unique string identifier assigned by the system when the object is created. No assumption can be made on the format or content of this identifier. The identifier must be provided whenever attempting to modify/delete (or reference) an existing object.<br>Field level constraints: must match pattern ^((?!;).)*$. (Note: Additional constraints might exist)
  limit
    description:
      - An integer representing the maximum amount of objects to return. If not specified, the maximum amount is 10
  offset
    description:
      - An integer representing the index of the first requested object. Index starts from 0. If not specified, the returned objects will start from index 0
  queryCloudUnknown
    description:
      - A Boolean value, TRUE or FALSE (the default). The TRUE value indicates that the device will query Cisco Collective Security Intelligence for unknown URLs.
  sort
    description:
      - The field used to sort the requested object list
  type
    description:
      - A UTF8 string, all letters lower-case, that represents the class-type. This corresponds to the class name.
  urlCacheReloadTTL
    description:
      - An enum value that specifies how long to cache the category and reputation lookup values for a given URL When the time to live expires, the next attempted access of the URL results in a fresh category/reputation lookup. Value can be one of the following: <br> NEVER (default) <br> TWO_HRS <br> FOUR_HRS <br> EIGHT_HRS <br> TWELVE_HRS <br> TWENTY_FOUR_HRS <br> FOURTY_EIGHT_HRS <br> ONE_WEEK
  version
    description:
      - A unique string version assigned by the system when the object is created or modified. No assumption can be made on the format or content of this identifier. The identifier must be provided whenever attempting to modify/delete an existing object. As the version will change every time the object is modified, the value provided in this identifier must match exactly what is present in the system or the request will be rejected.

extends_documentation_fragment: ftd
"""

EXAMPLES = """
- name: Fetch CloudConfig with a given name
  ftd_cloud_config:
    hostname: "https://127.0.0.1:8585"
    access_token: 'ACCESS_TOKEN'
    refresh_token: 'REFRESH_TOKEN'
    operation: "getCloudConfigByName"
    name: "Ansible CloudConfig"
"""

RETURN = """
response:
  description: HTTP response returned from the API call.
  returned: success
  type: dict
error_code:
  description: HTTP error code returned from the server.
  returned: error
  type: int
msg:
  description: Error message returned from the server.
  returned: error
  type: dict
"""
import json

from ansible.module_utils.authorization import retry_on_token_expiration
from ansible.module_utils.basic import AnsibleModule, to_text
from ansible.module_utils.http import construct_url, base_headers, iterate_over_pageable_resource
from ansible.module_utils.misc import dict_subset, construct_module_result, copy_identity_properties
from ansible.module_utils.six.moves.urllib.error import HTTPError
from ansible.module_utils.urls import open_url


class CloudConfigResource(object):
    
    @staticmethod
    @retry_on_token_expiration
    def editCloudConfig(params):
        path_params = dict_subset(params, ['objId'])
        body_params = dict_subset(params, ['enableAutomaticUpdates', 'id', 'queryCloudUnknown', 'type', 'urlCacheReloadTTL', 'version'])

        url = construct_url(params['hostname'], '/devicesettings/default/cloudconfig/{objId}', path_params=path_params)
        request_params = dict(
            headers=base_headers(params['access_token']),
            method='PUT',
            data=json.dumps(body_params)
        )

        response = open_url(url, **request_params).read()
        return json.loads(to_text(response)) if response else response

    @staticmethod
    @retry_on_token_expiration
    def getCloudConfig(params):
        path_params = dict_subset(params, ['objId'])

        url = construct_url(params['hostname'], '/devicesettings/default/cloudconfig/{objId}', path_params=path_params)
        request_params = dict(
            headers=base_headers(params['access_token']),
            method='GET',
        )

        response = open_url(url, **request_params).read()
        return json.loads(to_text(response)) if response else response

    @staticmethod
    @retry_on_token_expiration
    def getCloudConfigList(params):
        query_params = dict_subset(params, ['filter', 'limit', 'offset', 'sort'])

        url = construct_url(params['hostname'], '/devicesettings/default/cloudconfig', query_params=query_params)
        request_params = dict(
            headers=base_headers(params['access_token']),
            method='GET',
        )

        response = open_url(url, **request_params).read()
        return json.loads(to_text(response)) if response else response

    @staticmethod
    @retry_on_token_expiration
    def getCloudConfigByName(params):
        search_params = params.copy()
        search_params['filter'] = 'name:%s' % params['name']
        item_generator = iterate_over_pageable_resource(CloudConfigResource.getCloudConfigList, search_params)
        return next(item for item in item_generator if item['name'] == params['name'])

    @staticmethod
    @retry_on_token_expiration
    def editCloudConfigByName(params):
        existing_object = CloudConfigResource.getCloudConfigByName(params)
        params = copy_identity_properties(existing_object, params)
        return CloudConfigResource.editCloudConfig(params)


def main():
    fields = dict(
        hostname=dict(type='str', required=True),
        access_token=dict(type='str', required=True),
        refresh_token=dict(type='str', required=True),

        operation=dict(type='str', choices=['editCloudConfig', 'getCloudConfig', 'getCloudConfigList', 'getCloudConfigByName', 'editCloudConfigByName'], required=True),
        register_as=dict(type='str'),

        enableAutomaticUpdates=dict(type='bool'),
        filter=dict(type='str'),
        id=dict(type='str'),
        limit=dict(type='int'),
        objId=dict(type='str'),
        offset=dict(type='int'),
        queryCloudUnknown=dict(type='bool'),
        sort=dict(type='str'),
        type=dict(type='str'),
        urlCacheReloadTTL=dict(type='str'),
        version=dict(type='str'),
    )

    module = AnsibleModule(argument_spec=fields)
    params = module.params

    try:
        method_to_call = getattr(CloudConfigResource, params['operation'])
        response = method_to_call(params)
        result = construct_module_result(response, params)
        module.exit_json(**result)
    except HTTPError as e:
        err_msg = to_text(e.read())
        module.fail_json(changed=False, msg=json.loads(err_msg) if err_msg else {}, error_code=e.code)
    except Exception as e:
        module.fail_json(changed=False, msg=str(e))


if __name__ == '__main__':
    main()
