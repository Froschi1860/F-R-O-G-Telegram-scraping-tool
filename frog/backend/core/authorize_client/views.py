import threading

from flask import jsonify, make_response, render_template, request
from frog.backend.core.globals import client_handler
from frog.backend.core.interface_classes.Credentials import query_credentials

from . import authorize_client_route
from .util import run_verification_thread


@authorize_client_route.route("/", methods=["GET", "POST"])
def authorize_client_route_root(client_handler=client_handler):
    phone = None
    if request.method == "GET":
        phone = request.args.get("phone").replace(" ", "+")
        if phone == None:
            return make_response({"message": "No phone number given."}, 400)
        if client_handler.authorized(phone):
            ### Maybe show another view here to offer option to log out ###
            return make_response({"message": "User is authorized"}, 200)
        credentials = query_credentials(phone).as_dict()
        client_handler.verification_code_entered().clear()
        client_handler.wrong_verification_code().clear()
        threading.Thread(
            target=run_verification_thread,
            args=[client_handler, credentials],
        ).start()

    if request.method == "POST":
        code = request.json.get("verification_code")
        phone = request.json.get("phone")
        if phone == None:
            return make_response({"message": "No phone number given."}, 400)
        try:
            code = int(code)
            if code < 0:
                raise ValueError
        except ValueError:
            return make_response(
                {"message": "Verification code must be a positive integer."}, 400
            )
        client_handler.set_verification_code(code)
        client_handler.verification_code_entered().set()

    while not client_handler.verification_code_neccesary().wait(1):
        if client_handler.wrong_verification_code().is_set():
            break

        if client_handler.error_on_auth():
            body = jsonify(
                {
                    "invalid_phone": client_handler.invalid_phone(),
                    "invalid_api_id": client_handler.invalid_api_id(),
                    "phone": phone,
                }
            )
            client_handler.clear_error_on_auth()
            client_handler.clear_invalid_phone()
            client_handler.clear_invalid_api_id()
            return make_response(body, 500)

        if client_handler.client_ready().is_set():
            client_handler.client_ready().clear()
            return make_response({"message": "User is authorized"}, 200)

    client_handler.verification_code_neccesary().clear()
    body = jsonify({"mesage": "Session verification is neccessary.", "phone": phone})
    return make_response(body, 401)


@authorize_client_route.route("/verify-session")
def authorize_client_route_verify_session():
    phone = request.args.get("phone")
    return render_template("verify-session.html", phone=phone)
