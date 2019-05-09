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

import os

UNITS = [{
    'name': 'Api call',
    'description': 'The final price is calculated based on the number of calls made to the API'
}]

TENANT_MANAGER = os.environ.get('TENANT_MANAGER_URL', 'https://tampere.apinf.cloud/')
ACCESS_ROLE = os.environ.get('BROKER_CONSUMER_ROLE', 'data-consumer')

UMBRELLA_URL = os.environ.get('UMBRELLA_URL', 'https://umbrella.docker:8443')
UMBRELLA_TOKEN = os.environ.get('UMBRELLA_TOKEN', 'cIeuoqCWk01jvQl9X0Y9Ff6zxLCh2Ppqc7PYq0I4')
UMBRELLA_KEY = os.environ.get('UMBRELLA_KEY', 'KawIYnpqPt8VG7YbVAJzAOR2odEK3ENT66ckvx5l')

IDM_URL = os.environ.get('IDM_URL', 'http://idm.docker:3000')
IDM_USER = os.environ.get('IDM_USER', 'fdelavega@conwet.com')
IDM_PASSWD = os.environ.get('IDM_PASSWD', '123456789')
IDM_USER_ID = os.environ.get('IDM_USER_ID', 'admin')

CLIENT_ID = os.environ.get('BAE_LP_OAUTH2_CLIENT_ID', '')
CLIENT_SECRET = os.environ.get('BAE_LP_OAUTH2_CLIENT_SECRET', '')

secrets_file = "/run/secrets/{}".format(os.environ.get("CREDENTIALS_FILE", "credentials.json"))
if os.path.isfile(secrets_file):
    with open(secrets_file, "r") as f:
        data = json.load(f)
        ACCESS_ROLE = data.get('broker', {}).get('client_id', ACCESS_ROLE)
        IDM_USER = data.get('idm', {}).get('user', IDM_USER)
        IDM_PASSWD = data.get('idm', {}).get('password', IDM_PASSWD)
        IDM_USER_ID = data.get('idm', {}).get('user_id', IDM_USER_ID)
        CLIENT_SECRET = data.get('idm', {}).get('secret', CLIENT_SECRET)
        UMBRELLA_TOKEN = data.get('umbrella', {}).get('token', UMBRELLA_TOKEN)
        UMBRELLA_KEY = data.get('umbrella', {}).get('key', UMBRELLA_KEY)
