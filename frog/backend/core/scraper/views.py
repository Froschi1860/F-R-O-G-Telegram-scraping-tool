import datetime
from . import scraper_route

from flask import make_response, render_template, request, jsonify
from frog.backend.core.globals import client_handler, scrape_handler
from frog.backend.core.interface_classes.Credentials import (
    query_all_credentials,
    query_all_phone_numbers,
)
from frog.backend.core.interface_classes.ClientHandler import (
    start_client,
    disconnect_client,
)
from frog.backend.core.interface_classes.Channel import query_meta_data
from frog.backend.core.scraper_util.mapper_util import map_ref_to_id
from .util import start_scraper_thread


@scraper_route.route("/")
def start_scraper(scrape_handler=scrape_handler):
    return render_template(
        "scraper.html", active_scrapers=scrape_handler.any_active_scraper()
    )


@scraper_route.route("/active-scrapers")
def scraper_route_active_scrapers(scrape_handler=scrape_handler):
    phone_numbers = query_all_phone_numbers()
    active = list()
    for phone in phone_numbers:
        if scrape_handler.active_scraper(phone):
            active.append(
                {
                    "phone": phone,
                    "cur_id": scrape_handler.cur_id(phone),
                    "last_scraped": scrape_handler.last_scraped(phone),
                }
            )
    if len(active) == 0:
        return make_response(
            {
                "message": "No active scrapers.",
                "errors": scrape_handler.errors_on_scrape(),
            },
            404,
        )
    return jsonify(
        {"active_scrapers": active, "errors": scrape_handler.errors_on_scrape()}
    )


@scraper_route.route("/single-channel-setup")
async def one_channel_setup_with_ref():
    channel_ref = request.args.get("channel_ref")
    if channel_ref == None:
        return make_response({"message": "No channel reference given."}, 400)
    credential = None
    all_credentials = query_all_credentials()
    for cred in all_credentials:
        if not client_handler.active_client(cred.phone()) and client_handler.authorized(
            cred.phone()
        ):
            credential = cred
    if credential == None:
        return make_response({"message": "No client available."}, 409)
    client = await start_client(credential.as_dict(), client_handler)
    if client == None:
        return make_response({"message": "Client is busy"}, 409)
    channel_id = await map_ref_to_id(client, channel_ref)
    await disconnect_client(credential.as_dict(), client, client_handler)
    if channel_id == -1:
        return make_response({"message": "Channel does not exist"}, 404)
    meta = query_meta_data(channel_id).as_dict()
    meta["channel_id"] = channel_id
    return jsonify(meta)


@scraper_route.route("/scrape-channels", methods=["GET", "PUT", "POST", "DELETE"])
async def scrape_channels():
    if request.method == "GET":
        if scrape_handler.scraper_queue().empty():
            return make_response({"message": "No scraping jobs scheduled."}, 404)
        return make_response({"jobs": scrape_handler.scraper_queue().qsize()}, 200)
    if request.method == "DELETE":
        scrape_handler.reset_queue()
        return make_response({"message": "Scheduled jobs reset."}, 200)
    refs = request.json.get("refs")
    if refs == None or type(refs) != list:
        return make_response({"message": "List of references is neccessary."}, 400)
    if request.method == "PUT":
        if (
            scrape_handler.user_queue_reset()
            or scrape_handler.scraper_queue().qsize == 0
            or scrape_handler.any_inactive_scraper()
        ):
            return make_response({"message": "Too few jobs remaining."}, 404)
        scrape_handler.add_to_queue(refs)
        return make_response({"jobs": scrape_handler.scraper_queue().qsize()}, 201)
    if request.method == "POST":
        try:
            scrape_handler.create_scraper_queue(refs)
        except ValueError:
            return make_response({"message": "Scraper jobs already scheduled."}, 409)
        scrape_handler.reset_errors_on_scrape()
        scraper_threads = list()
        all_credentials = query_all_credentials()
        for cred in all_credentials:
            if client_handler.is_ready_for_scraping(cred):
                scraper_threads.append(
                    start_scraper_thread(scrape_handler, client_handler, cred)
                )
        if len(scraper_threads) == 0:
            return make_response({"message": "No scrapers available."}, 404)
        body = jsonify(
            {
                "threads": len(scraper_threads),
            }
        )
        return make_response(body, 201)


@scraper_route.route("/abort-scraper", methods=["DELETE"])
async def abort_scraper():
    phone = request.json.get("phone")
    phone_numbers = query_all_phone_numbers()
    if phone == None or phone not in phone_numbers:
        return make_response({"message": "No or invalid phone number."}, 400)
    if not scrape_handler.active_scraper(phone):
        return make_response({"message": "No active scraper for phone number."}, 404)
    scrape_handler.set_abort_scraper(phone)
    return make_response({"message": "Aborted scraper"})


@scraper_route.route("/config", methods=["GET", "PUT", "DELETE"])
def scraper_route_config(scrape_handler=scrape_handler):
    if request.method == "GET":
        cfg = scrape_handler.cfg()
        return jsonify(
            {
                "start_date": cfg["start_date"],
                "end_date": cfg["offset_date"],
                "max_msgs": cfg["total_count_limit"],
                "force_full": cfg["force_full"],
            }
        )
    if scrape_handler.any_active_scraper():
        return make_response(
            {"message": "Scraper is active. Only possible when no scraper is running."},
            409,
        )
    if request.method == "DELETE":
        scrape_handler.reset_cfg()
        cfg = scrape_handler.cfg()
        return jsonify(
            {
                "start_date": cfg["start_date"],
                "end_date": cfg["offset_date"],
                "max_msgs": cfg["total_count_limit"],
                "force_full": cfg["force_full"],
            }
        )
    start_date = request.json.get("start_date")
    if len(start_date) != 0:
        try:
            start_date = datetime.date.fromisoformat(start_date)
            if start_date > datetime.date.today():
                return make_response(
                    {"message": "Start date cannot be in the future."}, 400
                )
        except ValueError:
            return make_response(
                {"message": "Start date given in invalid format."}, 400
            )
    else:
        start_date = None
    end_date = request.json.get("end_date")
    if len(end_date) != 0:
        try:
            end_date = datetime.date.fromisoformat(end_date)
            if end_date > datetime.date.today():
                return make_response(
                    {"message": "End date cannot be in the future."}, 400
                )
        except ValueError:
            return make_response({"message": "End date given in invalid format."}, 400)
    else:
        end_date = None
    if start_date != None and end_date != None:
        if start_date >= end_date:
            return make_response({"message": "End date must be after start date."}, 400)
    max_msgs = request.json.get("max_msgs")
    if type(max_msgs) != int or max_msgs < 0 or max_msgs % 100 != 0:
        return make_response(
            {"message": "Max messages must be a positive integer divisible by 100."},
            400,
        )
    force_full = request.json.get("force_full")
    if type(force_full) != bool:
        return make_response(
            {"message": "Force full must be a boolean."},
            400,
        )
    if force_full:
        start_date = None
        end_date = None
        max_msgs = 0
    scrape_handler.set_cfg("start_date", start_date)
    scrape_handler.set_cfg("total_count_limit", max_msgs)
    scrape_handler.set_cfg("offset_date", end_date)
    scrape_handler.set_cfg("force_full", force_full)
    cfg = scrape_handler.cfg()
    return jsonify(
        {
            "start_date": cfg["start_date"],
            "end_date": cfg["offset_date"],
            "max_msgs": cfg["total_count_limit"],
            "force_full": cfg["force_full"],
        }
    )
