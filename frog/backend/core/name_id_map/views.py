from . import name_id_map_route

from flask import make_response, render_template, request, jsonify
from frog.backend.core.globals import client_handler, scrape_handler
from frog.backend.core.scraper_util.mapper_util import map_ref_to_id, map_id_to_refs
from frog.backend.core.interface_classes.ClientHandler import (
    start_client,
    disconnect_client,
)
from frog.backend.core.interface_classes.Credentials import query_all_credentials


@name_id_map_route.route("/")
def name_id_map_route_root(scrape_handler=scrape_handler):
    return render_template(
        "name-id-map.html", active_scrapers=scrape_handler.any_active_scraper()
    )


@name_id_map_route.route("/by-id")
async def name_id_map_route_id():
    channel_id = request.args.get("channel_id", type=int)
    if channel_id == None or channel_id < 1:
        return make_response({"message": "Channel ID must be a positive integer."}, 400)
    credentials = None
    all_credentials = query_all_credentials()
    for cred in all_credentials:
        if not client_handler.active_client(cred.phone()) and client_handler.authorized(
            cred.phone()
        ):
            credentials = cred
    if credentials == None:
        return make_response({"message": "No client available."}, 409)
    client = await start_client(credentials.as_dict(), client_handler)
    if client == None:
        return make_response({"message": "An active client is already running."}, 409)
    channel_refs = await map_id_to_refs(client, channel_id)
    await disconnect_client(credentials.as_dict(), client, client_handler)
    if channel_refs == None:
        return make_response({"message": "Channel does not exist."}, 404)
    return jsonify({channel_id: channel_refs})


@name_id_map_route.route("/by-reference")
async def name_id_map_route_ref():
    ref = request.args.get("channel_ref")
    if ref == None:
        return make_response({"message": "No reference provided."}, 400)
    credentials = None
    all_credentials = query_all_credentials()
    for cred in all_credentials:
        if not client_handler.active_client(cred.phone()) and client_handler.authorized(
            cred.phone()
        ):
            credentials = cred
    if credentials == None:
        return make_response({"message": "No client available."}, 409)
    client = await start_client(credentials.as_dict(), client_handler)
    if client == None:
        return make_response({"message": "An active client is already running."}, 409)
    id = await map_ref_to_id(client, ref)
    await disconnect_client(credentials.as_dict(), client, client_handler)
    if id == -1:
        return make_response({"message": "Channel does not exist"}, 404)
    return jsonify({ref: id})
