# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015 CERN.
#
# Invenio is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston,
# MA 02111-1307, USA.
#
# In applying this license, CERN does not
# waive the privileges and immunities granted to it by virtue of its status
# as an Intergovernmental Organization or submit itself to any jurisdiction.

"""Define base Grobid Blueprint."""

from flask import Blueprint, render_template, request, Response

from flask_login import login_required

from .api import process_pdf

blueprint = Blueprint('grobid', __name__, url_prefix="/grobid",
                      template_folder='templates',
                      static_folder='static')


@blueprint.route('/')
@blueprint.route('/index')
@login_required
def index():
    """Main entry point."""
    return render_template("grobid/index.html")


@blueprint.route('/upload', methods=["POST"])
@login_required
def process_file():
    file_uploaded = request.files['file']
    results = process_pdf(file_uploaded.stream, stream=True)
    return Response(results, content_type="text/xml")
