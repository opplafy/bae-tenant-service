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

import base64
import requests
from urlparse import urljoin

from wstore.asset_manager.resource_plugins.plugin_error import PluginError

from settings import IDM_USER, IDM_PASSWD, IDM_URL, CLIENT_ID, CLIENT_SECRET


TOKEN_SERVICE_ENDPOINT = '/oauth2/password'


def get_token():
    url = urljoin(IDM_URL, TOKEN_SERVICE_ENDPOINT)

    params = {
        'grant_type': 'password',
        'username': IDM_USER,
        'password': IDM_PASSWD
    }

    credentials = base64.encode('{}:{}'.format(CLIENT_ID, CLIENT_SECRET))
    resp = requests.post(url, data=params, headers={
        'Content-Type': 'application/x-www-form-urlencoded',
        'Authorization': 'Bearer ' + credentials
    })

    if resp.status_code != 200:
        raise PluginError('It was not possible to generate a valid access token')

    return resp.json()['access_token']
