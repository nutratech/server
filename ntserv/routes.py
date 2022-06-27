# -*- coding: utf-8 -*-
"""
Created on Sat Jan  4 18:20:27 2020

@author: shane
"""

from sanic import Sanic, html

from ntserv import __module__
from ntserv.controllers.accounts import (
    get_confirm_email,
    get_email_change,
    get_password_change,
    get_user_details,
    post_login,
    post_password_new_request,
    post_password_new_reset,
    post_register,
    post_username_forgot,
    post_v2_login,
)
from ntserv.controllers.calculate import (
    get_nutrients,
    post_calc_1rm,
    post_calc_bmr,
    post_calc_body_fat,
    post_calc_lb_limits,
)
from ntserv.controllers.sync import opt_sync
from ntserv.env import PROXY_SECRET
from ntserv.persistence.psql import get_pg_version
from ntserv.utils.cache import reload
from ntserv.utils.libserver import exc_req, home_page_text, self_route_rules

# Load SQL cache in-memory, if accessible
reload()

# Export the Sanic app
app = Sanic(__module__)
app.config.FORWARDED_SECRET = PROXY_SECRET


# TODO: blueprinting, e.g. /auth, /calc


# -------------------------
# Routes
# -------------------------
@app.route("/")
async def _(*args):
    _ = args
    url_map = self_route_rules(app)
    home_page = home_page_text(url_map)
    return html(f"<pre>{home_page}</pre>", 200)


@app.route("/user_details")
async def _(request):
    return exc_req(get_user_details, request)


@app.route("/pg/version")
async def _(request):
    return exc_req(get_pg_version, request)


# ------------------------------------------------
# Public functions: /nutrients
# ------------------------------------------------
@app.route("/nutrients")
async def _(request):
    return exc_req(get_nutrients, request)


@app.route("/nutrients/html")
async def _(request):
    return exc_req(get_nutrients, request, response_type="HTML")


# ------------------------------------------------
# Public functions: /calc
# ------------------------------------------------
@app.route("/calc/1rm", methods=["POST"])
async def _(request):
    return exc_req(post_calc_1rm, request)


@app.route("/calc/bmr", methods=["POST"])
async def _(request):
    return exc_req(post_calc_bmr, request)


@app.route("/calc/body-fat", methods=["POST"])
async def _(request):
    return exc_req(post_calc_body_fat, request)


@app.route("/calc/lbm-limits", methods=["POST"])
async def _(request):
    return exc_req(post_calc_lb_limits, request)


# -------------------------
# Account functions
# -------------------------
@app.route("/register", methods=["POST"])
async def _(request):
    return exc_req(post_register, request)


@app.route("/login", methods=["POST"])
async def _(request):
    return exc_req(post_login, request)


@app.route("/v2/login", methods=["POST"])
async def _(request):
    return exc_req(post_v2_login, request)


@app.route("/email/confirm")
async def _(request):
    return exc_req(get_confirm_email, request)


@app.route("/email/change")
async def _(request):
    return exc_req(get_email_change, request)


@app.route("/password/change")
async def _(request):
    return exc_req(get_password_change, request)


@app.route("/username/forgot", methods=["POST"])
async def _(request):
    return exc_req(post_username_forgot, request)


@app.route("/password/new/request")
async def _(request):
    return exc_req(post_password_new_request, request)


@app.route("/password/new/reset")
async def _(request):
    return exc_req(post_password_new_reset, request)


# ------------------------------------------------
# Sync functions
# ------------------------------------------------
@app.route("/sync", methods=["GET", "POST"])
async def _(request):
    return exc_req(opt_sync, request)
