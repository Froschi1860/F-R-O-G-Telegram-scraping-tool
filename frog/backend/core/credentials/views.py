import webview

from . import credentials_route
from flask import jsonify, make_response, render_template, request
from frog.backend.core.globals import client_handler, scrape_handler
from frog.backend.core.interface_classes.Credentials import (
    save_credentials,
    query_all_credentials,
    delete_credentials,
    update_credentials,
    query_credentials,
    Credentials,
)
from frog.backend.core.scraper_util.auth_util import check_auth_for_credentials


@credentials_route.route("/view")
def credentials_route_all_credentials(scrape_hander=scrape_handler):
    return render_template(
        "credentials.html", active_scrapers=scrape_handler.any_active_scraper()
    )


@credentials_route.route("/", methods=["GET", "DELETE", "POST"])
async def credentials_route_root(
    client_handler=client_handler, scrape_handler=scrape_handler
):
    if request.method == "GET":
        all_credentials = query_all_credentials()
        await check_auth_for_credentials(all_credentials, client_handler)
        if len(all_credentials) == 0:
            return make_response({"message": "No credentials found."}, 404)
        for idx in range(len(all_credentials)):
            all_credentials[idx] = all_credentials[idx].as_dict()
        return jsonify({"credentials": all_credentials})
    phone = request.json.get("phone")
    if phone == None:
        return make_response({"message": "No phone number given"}, 400)
    if request.method == "DELETE":
        if not delete_credentials(phone):
            return ({"message": "Phone number not found"}, 404)
        client_handler.remove_phone_number(phone)
        scrape_handler.remove_phone_number(phone)
        return jsonify({"message": "Deleted credentials", "phone": phone})
    username = request.json.get("username")
    api_id = request.json.get("api_id")
    api_hash = request.json.get("api_hash")
    if username == None or api_id == None or api_hash == None:
        return make_response(
            {"message": "Request is lacking neccesssary information."}, 400
        )
    credentials = Credentials()
    credentials.set_credentials(
        username=username,
        phone=phone,
        api_id=api_id,
        api_hash=api_hash,
    )
    if not save_credentials(credentials):
        return make_response({"message": "Credentials with phone number exist."}, 409)
    client_handler.add_phone_number(phone)
    scrape_handler.add_phone_number(phone)
    body = jsonify(credentials.as_dict())
    return make_response(body, 201)


@credentials_route.route("/edit", methods=["GET", "PUT"])
def credentials_route_edit(scrape_handler=scrape_handler):
    if request.method == "GET":
        phone = request.args.get("phone", int)
        if phone == None:
            return make_response({"message": "No phone number given."}, 400)
        return render_template(
            "edit-credentials.html",
            credentials=query_credentials(phone).as_dict(),
            active_scrapers=scrape_handler.any_active_scraper(),
        )
    phone = request.json.get("phone")
    username = request.json.get("username")
    api_id = request.json.get("api_id")
    api_hash = request.json.get("api_hash")
    if phone == None or username == None or api_id == None or api_hash == None:
        return make_response({"message": "Request lacks neccesssary information."}, 400)
    if not update_credentials(phone, username, api_id, api_hash):
        return make_response(
            {"message": "Phone number not found or invalid number format."}, 404
        )
    return jsonify(
        {"phone": phone, "username": username, "api_id": api_id, "api_hash": api_hash}
    )
