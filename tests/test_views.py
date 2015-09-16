# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015 CERN.
#
# Invenio is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

import os

import httpretty
import mock

from invenio_grobid.errors import GrobidRequestError

from invenio.base.globals import cfg
from invenio.testsuite import InvenioTestCase


class TestViews(InvenioTestCase):

    """Test invenio_grobid's views."""

    def setup_class(self):
        """Load a valid and an invalid fixture, and mock a GROBID failure."""
        self.valid_pdf = os.path.join('tests', 'fixtures', 'article.pdf')
        self.invalid_pdf = os.path.join('tests', 'fixtures', 'garbage.pdf')

        def raise_grobid_request_error(self):
            raise GrobidRequestError

        self.raise_grobid_request_error = raise_grobid_request_error

    def test_get_root(self):
        """Can GET the /grobid page."""
        self.login('admin', 'admin')
        response = self.client.get('/grobid', follow_redirects=True)

        self.assertIn('Upload new File', response.data)

    @httpretty.activate
    def test_post_valid_pdf(self):
        """Obtain GROBID's response when POSTing valid data."""
        url = os.path.join(cfg.get('GROBID_HOST'), 'processFulltextDocument')
        httpretty.register_uri(httpretty.POST, url, body='<TEI></TEI>')

        self.login('admin', 'admin')
        response = self.client.post(
            '/grobid/upload',
            content_type='multipart/form-data',
            data={'file': (self.valid_pdf,)}
        )

        self.assertIn('</TEI>', response.data)

    @mock.patch('invenio_grobid.api')
    def test_post_invalid_pdf(self, api):
        """Redirect to /grobid when POSTing invalid data."""
        api.process_pdf = self.raise_grobid_request_error

        self.login('admin', 'admin')
        response = self.client.post(
            '/grobid/upload',
            content_type='multipart/form-data',
            data={'file': (self.invalid_pdf,)}
        )

        self.assertEqual(response.status_code, 302)
        self.assertIn('/grobid', response.location)
