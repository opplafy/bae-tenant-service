# -*- coding: utf-8 -*-

# Copyright (c) 2019 Future Internet Consulting and Development Solutions S.L.

# This file is part of BAE Tenant Service plugin.

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import unicode_literals

import requests
from urlparse import urljoin

from wstore.asset_manager.resource_plugins.plugin_error import PluginError

from settings import UMBRELLA_KEY, UMBRELLA_TOKEN, UMBRELLA_URL


def _post_request(path, body):
    url = urljoin(UMBRELLA_URL, path)
    try:
        resp = requests.post(url, data=body, headers={
            'X-Api-Key': UMBRELLA_KEY,
            'X-Admin-Auth-Token': UMBRELLA_ADMIN_TOKEN
        }, verify=False)
    except requests.ConnectionError:
        raise PermissionDenied('Invalid resource: API Umbrella server is not responding')

    if resp.status_code == 404:
        raise PluginError('The provided Umbrella resource does not exist')
    elif resp.status_code != 200:
        raise PluginError('Umbrella gives an error accessing the provided resource')

    return resp.json()


def _get_null_rule(field):
    return {
        'id': field,
        'field': field,
        'type': 'string',
        'input': 'select',
        'operator': 'is_null',
        'value': None
    }


def _get_rule(field, value, operator='equal'):
    return {
        'id': field,
        'field': field,
        'type': 'string',
        'input': 'text',
        'operator': operator,
        'value': value
    }


def _paginate_accounting(params, accounting, aggregator, unit):
    page_len = 500
    start = 0
    processed = False

    current_day = None
    current_value = 0

    while not processed:
        params['start'] = start
        params['length'] = page_len
        result = _post_request('/api-umbrella/v1/analytics/logs.json', params)

        # There is no remaining elements
        if not len(result['data']):
            processed = True

        for elem in result['data']:
            # Process log timestamp (Which includes milliseconds)
            date = datetime.utcfromtimestamp(elem['request_at']/1000.0)
            day = date.date()

            if current_day is None:
                # New day to be aggregated
                current_day = day

            # If new day is higher save the accounting info
            if day > current_day:
                accounting.append({
                    'unit': unit,
                    'value': current_value,
                    'date': unicode(current_day.isoformat()) + 'T00:00:00Z'
                })

                # Set current day and reset value
                current_day = day
                current_value = 0

            current_value += accounting_aggregator(elem)
        start += page_len

    # Save last info
    if current_value > 0:
        accounting.append({
            'unit': unit,
            'value': current_value,
            'date': unicode(current_date.isoformat()) + 'T00:00:00Z'
        })


def _process_call_accounting(tenant, params, unit):
    accounting = []

    def call_aggregator(elem):
        account = 1
        # Check in request headers the tenant
        return account

    return _paginate_accounting(params, accounting, call_aggregator, unit)


def get_accounting(email, path, tenant, start_at, end_at, unit):
    rules = [
        _get_null_rule('gatekeeper_denied_code'),
        _get_rule('user_email', email),
        _get_rule('request_path', path, operator='begins_with')
    ]

    query = {
        'condition': 'AND',
        'rules': rules,
        'valid': True
    }

    params = {
        'start_at': start_at,
        'end_at': end_at,
        'query': json.dumps(query)
    }

    return _process_call_accounting(tenant, params, unit)
