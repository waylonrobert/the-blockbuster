"""Serve the Blockbuster archive from Flask.

Drop the generated editions (and the auto-built index.html) into
``<app>/static/blockbuster/``, then register these routes. Adjust the
``static/blockbuster`` path to match your app's static folder.
"""
from flask import send_from_directory


def register_blockbuster_routes(app):
    @app.route("/blockbuster")
    @app.route("/blockbuster/")
    def blockbuster_index():
        # index.html redirects to the latest edition; archive.html lists all (see publish.py)
        return send_from_directory("static/blockbuster", "index.html", max_age=300)

    @app.route("/blockbuster/<path:filename>")
    def blockbuster_static(filename):
        # Editions are static and immutable once published -> long cache
        return send_from_directory("static/blockbuster", filename, max_age=604800)
