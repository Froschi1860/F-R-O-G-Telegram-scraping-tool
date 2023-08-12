from flask import jsonify, make_response, render_template, request

from frog.backend.core.interface_classes.Channel import (
    query_meta_data,
    query_msgs_as_list,
    delete_msgs,
    delete_channel,
)
from frog.backend.core.interface_classes.ErrorLog import write_error_log
from frog.backend.core.interface_classes.NameIdMap import (
    query_name_id_mapping,
    delete_mappings_by_id,
)
from frog.backend.core.interface_classes.NameIdMap import (
    query_all_mappings_sorted_by_ref,
)
from frog.backend.core.io_util.export import (
    write_msgs_to_csv,
    write_msgs_to_json,
    write_meta_to_json,
    write_name_id_maps_csv,
)
from frog.backend.core.paths import output_dir
from frog.backend.core.globals import scrape_handler
from . import data_view_route
from .util import evaluate_string_as_bool
import traceback


@data_view_route.route("/")
def data_view_route_root(scrape_handler=scrape_handler):
    return render_template(
        "data-view.html", active_scrapers=scrape_handler.any_active_scraper()
    )


@data_view_route.route("/all-channels-refs")
def data_view_route_all_channel_refs():
    mappings = query_all_mappings_sorted_by_ref()
    return jsonify(mappings)


@data_view_route.route("/meta-by-id")
def data_view_route_meta_by_id():
    channel_id = request.args.get("channel_id", type=int)
    if channel_id == None or channel_id < 1:
        return make_response({"message": "ID must be a positive integer."}, 400)
    meta = query_meta_data(channel_id)
    if meta == None:
        return make_response({"message": "Channel not found."}, 404)
    meta_dict = meta.as_dict()
    meta_dict["channel_id"] = channel_id
    return jsonify(meta_dict)


@data_view_route.route("/meta-by-ref")
def data_view_route_meta_by_ref():
    channel_ref = request.args.get("channel_ref")
    if channel_ref == None:
        return make_response({"message": "No channel reference provided."}, 400)
    name_id_map = query_name_id_mapping(channel_ref)
    if name_id_map == None:
        return make_response({"message": "Channel not found."}, 404)
    meta = query_meta_data(name_id_map.channel_id())
    if meta == None:
        return make_response({"message": "Channel not found."}, 404)
    meta_dict = meta.as_dict()
    meta_dict["channel_id"] = name_id_map.channel_id()
    return jsonify(meta_dict)


@data_view_route.route("/msgs-by-id")
def data_view_route_msgs_by_id():
    channel_id = request.args.get("channel_id", type=int)
    if channel_id == None or channel_id < 1:
        return make_response({"message": "ID must be a positive integer."}, 400)
    msgs = query_msgs_as_list(channel_id)
    if msgs == None:
        return make_response({"message": "Channel not found."}, 404)
    return jsonify({"msgs": msgs})


@data_view_route.route("/export-msgs")
def data_view_route_export_msgs():
    channel_id = request.args.get("channel_id", type=int)
    if channel_id == None or channel_id < 1:
        return make_response({"message": "ID must be a positive integer."}, 400)
    filetype = request.args.get("filetype")
    if filetype == None or not (filetype == "csv" or filetype == "json"):
        return make_response({"message": "Filetype must be csv or json."}, 400)
    overwrite = request.args.get(
        "overwrite", default=False, type=evaluate_string_as_bool
    )
    try:
        path = output_dir
        if filetype == "csv":
            path = write_msgs_to_csv(output_dir, channel_id, overwrite)
        if filetype == "json":
            path = write_msgs_to_json(output_dir, channel_id, overwrite)
        if path == None:
            res = jsonify({"path": path})
            res.status_code = 300
            return res
        return jsonify({"path": path})
    except FileNotFoundError:
        write_error_log("DirectoryNotFound", "Output directory does not exist.")
        return make_response({"message": "Output directory does not exist."}, 409)
    except ValueError:
        write_error_log(
            "ChannelNotFound",
            f"No metadata and messages found for channel ID {channel_id}",
        )
        return make_response({"message": "Channel not found."}, 404)
    except Exception:
        write_error_log("Unkown", traceback.format_exc())
        return make_response({"message": "Internal server error."}, 500)


@data_view_route.route("/export-multiple", methods=["POST"])
def data_view_route_export_multiple():
    body = request.json
    channel_ids = body.get("channel_ids")
    filetype = body.get("filetype")
    include_meta = body.get("include_meta")
    if channel_ids == None or type(channel_ids) != list:
        return make_response({"message": "No list of channel IDs provided."}, 400)
    if filetype != "csv" and filetype != "json":
        return make_response({"message": "Invalid filetype."}, 400)
    written = []
    path = ""
    not_found = 0
    for channel_id in channel_ids:
        try:
            if filetype == "csv":
                path = write_msgs_to_csv(output_dir, channel_id, True)
            if filetype == "json":
                path = write_msgs_to_json(output_dir, channel_id, True)
            if include_meta:
                path = write_meta_to_json(output_dir, channel_id, True)
            written.append(channel_id)
        except FileNotFoundError:
            write_error_log("DirectoryNotFound", "Output directory does not exist.")
            return make_response({"message": "Output directory does not exist."}, 409)
        except ValueError:
            write_error_log(
                "ChannelNotFound",
                f"No metadata and messages found for channel ID {channel_id}",
            )
            not_found += 1
            continue
        except Exception:
            write_error_log("Unkown", traceback.format_exc())
            body = jsonify({"written": written, "path": path, "not_found": not_found})
            return make_response(body, 500)
    if len(written) == 0:
        return make_response({"messsage": "No channels exported."}, 200)
    body = jsonify({"written": written, "path": path, "not_found": not_found})
    return make_response(body, 201)


@data_view_route.route("/export-meta")
def data_view_route_export_meta():
    channel_id = request.args.get("channel_id", type=int)
    if channel_id == None or channel_id < 1:
        return make_response({"message": "ID must be a positive integer."}, 400)
    overwrite = request.args.get(
        "overwrite", default=False, type=evaluate_string_as_bool
    )
    try:
        path = write_meta_to_json(output_dir, channel_id, overwrite)
        if path == None:
            res = jsonify({"path": path})
            res.status_code = 300
            return res
        return jsonify({"path": path})
    except FileNotFoundError:
        write_error_log("DirectoryNotFound", "Output directory does not exist.")
        return make_response({"message": "Output directory does not exist."}, 409)
    except ValueError:
        write_error_log(
            "ChannelNotFound",
            f"No metadata and messages found for channel ID {channel_id}",
        )
        return make_response({"message": "Channel not found."}, 404)
    except Exception:
        write_error_log("Unkown", traceback.format_exc())
        return make_response({"message": "Internal server error."}, 500)


@data_view_route.route("/delete-channel", methods=["DELETE"])
def data_view_route_delete_channel():
    channel_id = request.json.get("channel_id", None)
    if channel_id == None or channel_id < 0:
        return make_response({"message": "Channel ID must be a positive integer."}, 400)
    include_meta = request.json.get("include_meta", None)
    if include_meta == None or type(include_meta) != bool:
        return make_response({"message": "Include meta must be a boolean."}, 400)
    res = {"msgs": False, "meta": False}
    if not delete_msgs(channel_id):
        return make_response({"message": "Channel not found."}, 404)
    res["msgs"] = True
    if include_meta:
        res["meta"] = delete_channel(channel_id)
    body = jsonify(res)
    return make_response(body, 200)


@data_view_route.route("/export-mappings", methods=["POST"])
def data_view_route_export_mappings():
    try:
        path = write_name_id_maps_csv(output_dir)
        if path == None:
            return make_response({"message": "No name-ID-maps found."}, 404)
        return make_response({"output_path": path}, 201)
    except FileNotFoundError:
        write_error_log("DirectoryNotFound", "Output directory does not exist.")
        return make_response({"message": "Output directory does not exist."}, 409)
    except Exception:
        write_error_log("Unkown", traceback.format_exc())
        return make_response({"message": "Internal server error."}, 500)


@data_view_route.route("/delete-name-id-maps", methods=["DELETE"])
def data_view_route_delete_name_id_maps():
    channel_id = request.json.get("channel_id", None)
    if channel_id == None or type(channel_id) != int or channel_id < 0:
        return make_response({"message": "Channel ID must be a positive integer."}, 400)
    if delete_mappings_by_id(channel_id):
        return make_response(
            {"message": f"Successfully deleted mappings for ID {channel_id}"}, 200
        )
    return make_response({"message": f"No mappings found for ID {channel_id}"}, 404)
