import traceback
from flask import render_template, make_response, request
from . import error_log_route
from frog.backend.core.interface_classes.ErrorLog import (
    query_error_log,
    write_error_log,
    delete_error_log,
)
from frog.backend.core.io_util.export import write_error_log_csv
from frog.backend.core.paths import output_dir


@error_log_route.route("/", methods=["GET", "DELETE"])
def error_log_route_root():
    if request.method == "DELETE":
        try:
            delete_error_log()
            return make_response({"message": "Succesfully deleted error log."})
        except Exception:
            return make_response({"message": "Internal server error."}, 500)
    try:
        return render_template("error-log.html", errors=query_error_log())
    except Exception:
        return render_template("error-log.html", exception=True)


@error_log_route.route("/export", methods=["POST"])
def error_log_route_export():
    try:
        path = write_error_log_csv(output_dir)
        if path == None:
            return make_response({"message": "No errors found."}, 404)
        return make_response({"output_path": path}, 201)
    except FileNotFoundError:
        write_error_log("DirectoryNotFound", "Output directory does not exist.")
        return make_response({"message": "Output directory does not exist."}, 409)
    except Exception:
        write_error_log("Unkown", traceback.format_exc())
        return make_response({"message": "Internal server error."}, 500)
