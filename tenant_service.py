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

from wstore.asset_manager.resource_plugins.plugin import Plugin
from wstore.asset_manager.resource_plugins.plugin_error import PluginError

from token_service import get_token
from settings import TENANT_MANAGER, ACCESS_ROLE, UNITS

TENANT_URL = '/tenant-manager/tenant/{}'

class TenantService(Plugin):

    def __init__(self, plugin_model):
        super(TenantService, self).__init__(plugin_model)
        self._units = UNITS

    def get_tenant(self, tenant_id):
        # Get tenant info
        url = urljoin(TENANT_MANAGER, TENANT_URL.format(tenant_id))
        resp = requests.get(url, headers={
            'Authorization': 'Bearer ' + get_token()
        })

        if resp.status_code == 404:
            raise PluginError('The specified tenant does not exist')

        if resp.status_code == 401 or resp.status_code == 403:
            raise PluginError('You are not authorized to publish an offering for the specified tenant')

        if resp.status_code != 200:
            raise PluginError('An error happened accessing to the tenant')

        return resp.json()

    def on_post_product_spec_validation(self, provider, asset):
        tenant_info = self.get_tenant(asset.meta_info['tenant_id'])

        # Check that the user making the request is authorized to create an offering for the tenant
        if provider.private:
            # If the user making the request is a user, he must be the owner
            if tenant_info['owner_id'] != provider.name
                raise PluginError('You are not authorized to publish an offering for the specified tenant')
        else:
            # if the user making the request is an organization, it must be the tenant organization
            if tenant_info['owner_organization'] != provider.name:
                raise PluginError('You are not authorized to publish an offering for the specified tenant')

    def on_post_product_offering_validation(self, asset, product_offering):
        # Validate that the pay-per-use model (if any) is supported by the backend
        if 'productOfferingPrice' in product_offering:
            has_usage = False
            supported_units = [unit['name'].lower() for unit in self._units]

            for price_model in product_offering['productOfferingPrice']:
                if price_model['priceType'] == 'usage':
                    has_usage = True

                    if price_model['unitOfMeasure'].lower() not in supported_units:
                        raise PluginError('Unsupported accounting unit ' +
                                          price_model['unit'] + '. Supported units are: ' + ','.join(supported_units))

    def on_product_acquisition(self, asset, contract, order):
        # Check if the acquisition is being made by an organization
        if not order.owner_organization.private:
            raise PluginError('A tenant cannot buy access to another tenant')

        # Add the customer to the tenant
        tenant_id = asset.meta_info['tenant_id']
        tenant_info = self.get_tenant(tenant_id)

        found = len([user_id for user in tenant_info['users'] if user['id'] != order.owner_organization.name) > 0

        if not found:
            patch = [
                {'op': 'add', 'path': '/users/-', 'value': {
                    'id': order.customer.username, 'name': order.customer.userprofile.actor_id, 'roles': [ACCESS_ROLE]}},
            ]

            resp = requests.patch(urljoin(TENANT_MANAGER, TENANT_URL.format(tenant_id)), json=patch, headers={
                'Authorization': 'Bearer ' + get_token()
            })

            if resp.status_code != 200:
                raise PluginError('An error happened updating tenant')

    def on_product_suspension(self, asset, contract, order):
        url = urljoin(TENANT_MANAGER, TENANT_URL.format(tenant_id))
        tenant_id = asset.meta_info['tenant_id']
        user_id = order.owner_organization.name
        i = 0

        while not done and i < 5:
            tenant_info = self.get_tenant(tenant_id)
            index = 0

            patch = [
                { 'op': 'test', 'path': '/users/{}/id'.format(index), 'value': user_id },
                { 'op': 'remove', 'path': '/users/{}'.format(index) }
            ]

            resp = requests.patch(urljoin(TENANT_MANAGER, TENANT_URL.format(tenant_id)), json=patch, headers={
                'Authorization': 'Bearer ' + get_token()
            })

            if response.status_code == 200:
                done = True

            i += 1

        if not done:
            raise PluginError('An error happened removing user from tenant')

    def get_usage_specs(self):
        return self._units

    def get_pending_accounting(self, asset, contract, order):
        accounting = []
        last_usage = None
        # Read pricing model to know the query to make
        if 'pay_per_use' in contract.pricing_model:
            unit = contract.pricing_model['pay_per_use'][0]['unit']

            # Read the date of the last SDR
            if contract.last_usage is not None:
                start_at = unicode(contract.last_usage.isoformat()).replace(' ', 'T') + 'Z'
            else:
                # The maximum time between refreshes is 30 days, so in the worst case
                # consumption started 30 days ago
                start_at = unicode((datetime.utcnow() - timedelta(days=31)).isoformat()).replace(' ', 'T') + 'Z'

            # Retrieve pending usage
            last_usage = datetime.utcnow()
            end_at = unicode(last_usage.isoformat()).replace(' ', 'T') + 'Z'

            # Check the accumulated usage for all the resources of the dataset
            # Accounting is always done by Umbrella no mather who validates permissions
            

        return accounting, last_usage