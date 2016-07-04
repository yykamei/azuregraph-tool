#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import json
import six
import sys
from six.moves import configparser
from six.moves.urllib.parse import urlencode, quote
from six.moves.urllib.request import Request, urlopen
from six.moves.urllib.error import URLError


class AzureConnector(object):
    def __init__(self, fp):
        conf = configparser.ConfigParser()
        conf.readfp(fp)
        self.tenant_id = conf.get('azure', 'tenant_id')
        self.client_id = conf.get('azure', 'client_id')
        self.client_secret = conf.get('azure', 'client_secret')
        self._get_token()

    def get(self, resource_path, name):
        query = {'api-version': '1.6'}
        headers = {
            'Authorization': '%(token_type)s %(access_token)s' % self.token_info,
            'Content-Type': 'application/json; charset=UTF-8',
        }
        endpoint = 'https://graph.windows.net/%(tenant_id)s/%(resource_path)s/%(name)s?%(query)s' % {
            'tenant_id': self.tenant_id,
            'resource_path': resource_path,
            'name': quote(name),
            'query': urlencode(query),
        }
        request = Request(endpoint, headers=headers)
        try:
            response = urlopen(request)
        except URLError as e:
            obj = json.loads(e.read().decode('utf-8'))  # application/json; charset=utf-8
            six.print_(json.dumps(obj, indent=2), file=sys.stderr)
            sys.exit(1)
        obj = json.loads(response.read().decode('utf-8'))  # charset=utf-8
        six.print_(json.dumps(obj, indent=2, ensure_ascii=False))

    def list(self,
             resource_path,
             filter=None,
             top=None,
             orderby=None,
             expand=None,
             format=None,
             skiptoken=None):
        query = {'api-version': '1.6'}
        if filter is not None:
            query['$filter'] = filter
        if top is not None:
            query['$top'] = top
        if orderby is not None:
            query['$orderby'] = orderby
        if expand is not None:
            query['$expand'] = expand
        if format is not None:
            query['$format'] = format
        if skiptoken is not None:
            query['$skiptoken'] = skiptoken
        headers = {
            'Authorization': '%(token_type)s %(access_token)s' % self.token_info,
            'Content-Type': 'application/json; charset=UTF-8',
        }
        endpoint = 'https://graph.windows.net/%(tenant_id)s/%(resource_path)s?%(query)s' % {
            'tenant_id': self.tenant_id,
            'resource_path': resource_path,
            'query': urlencode(query),
        }
        request = Request(endpoint, headers=headers)
        try:
            response = urlopen(request)
        except URLError as e:
            obj = json.loads(e.read().decode('utf-8'))  # application/json; charset=utf-8
            six.print_(json.dumps(obj, indent=2), file=sys.stderr)
            sys.exit(1)
        obj = json.loads(response.read().decode('utf-8'))  # charset=utf-8
        # obj has 'value' key
        six.print_(json.dumps(obj['value'], indent=2, ensure_ascii=False))

    def _get_token(self):
        body = urlencode({
            'grant_type': 'client_credentials',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
        })
        endpoint = 'https://login.windows.net/%(tenant_id)s/oauth2/token' % {
            'tenant_id': quote(self.tenant_id),
        }
        try:
            response = urlopen(endpoint, body.encode('utf-8'))
        except URLError as e:
            pass
        self.token_info = json.loads(response.read().decode('utf-8'))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-I',
        '--info',
        type=argparse.FileType(),
        required=True)
    subcommands = parser.add_subparsers(dest='subcommand')
    list = subcommands.add_parser('list')
    list.add_argument('--filter')
    list.add_argument('--top', type=int)
    list.add_argument('--orderby')
    list.add_argument('--expand')
    list.add_argument('--skiptoken')
    list.add_argument('resource_path', choices=[
        'applications',
        'contacts',
        'contracts',
        'devices',
        'directoryObjects',
        'directoryRoles',
        'directoryRoleTemplates',
        'domains',
        'groups',
        'oauth2PermissionGrants',
        'servicePrincipals',
        'subscribedSkus',
        'tenantDetails',
        'users',
    ])
    get = subcommands.add_parser('get')
    get.add_argument('resource_path', choices=[
        'applications',
        'contacts',
        'contracts',
        'devices',
        'directoryObjects',
        'directoryRoles',
        'directoryRoleTemplates',
        'domains',
        'groups',
        'oauth2PermissionGrants',
        'servicePrincipals',
        'subscribedSkus',
        'tenantDetails',
        'users',
    ])
    get.add_argument('name')
    # Parse sys.argv[1:]
    ns = parser.parse_args()
    connector = AzureConnector(ns.info)
    del ns.info
    if ns.subcommand == 'get':
        del ns.subcommand
        connector.get(**vars(ns))
    elif ns.subcommand == 'list':
        del ns.subcommand
        connector.list(**vars(ns))
