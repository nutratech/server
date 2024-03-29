# -*- coding: utf-8 -*-
"""
Created on Sat Jan  4 18:20:27 2020

@author: shane
"""
import sanic
from sanic_ext import Config

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
from ntserv.env import ALLOWED_ORIGINS, PROXY_SECRET
from ntserv.persistence.psql import get_pg_version
from ntserv.utils.cache import reload
from ntserv.utils.libserver import exc_req, home_page_text, self_route_rules

# Load SQL cache in-memory, if accessible
reload()

# Export the Sanic app
app = sanic.Sanic(__module__)
app.config.FORWARDED_SECRET = PROXY_SECRET

app.extend(
    config=Config(
        cors_origins=ALLOWED_ORIGINS,
        # oas_url_prefix="/apidocs",
        oas=False,
    )
)
app.config.OAS = False

# pylint: disable=missing-function-docstring

# TODO: blueprinting, e.g. /auth, /calc


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Routes
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@app.route("/")
async def get_api(*args: sanic.Request) -> sanic.HTTPResponse:
    _ = args
    url_map = self_route_rules(app)
    home_page = home_page_text(url_map)
    return sanic.html(f"<pre>{home_page}</pre>", 200)


@app.route("/robots.txt")
async def get_robots_txt(*args: sanic.Request) -> sanic.HTTPResponse:
    _ = args
    robots_txt = """# Block Google from indexing API server
User-agent: Googlebot
Disallow: /

# TODO: what about Bing and other search indexes?
User-agent: *
Allow: /
"""
    return sanic.text(robots_txt, 200)


@app.route("/user_details")
async def api_get_user_details(request: sanic.Request) -> sanic.HTTPResponse:
    return exc_req(get_user_details, request)


@app.route("/pg/version")
async def api_get_pg_version(request: sanic.Request) -> sanic.HTTPResponse:
    return exc_req(get_pg_version, request)


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Public functions: /nutrients
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@app.route("/nutrients")
async def api_get_nutrients(request: sanic.Request) -> sanic.HTTPResponse:
    return exc_req(get_nutrients, request)


@app.route("/products")
async def api_get_products(request: sanic.Request) -> sanic.HTTPResponse:
    return exc_req(get_nutrients, request)


@app.route("/nutrients/html")
async def api_get_nutrients_html(request: sanic.Request) -> sanic.HTTPResponse:
    return exc_req(get_nutrients, request, response_type="HTML")


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Public functions: /calc
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@app.route("/calc/1rm", methods=["POST"])
async def api_post_calc_1rm(request: sanic.Request) -> sanic.HTTPResponse:
    return exc_req(post_calc_1rm, request)


@app.route("/calc/bmr", methods=["POST"])
async def api_post_calc_bmr(request: sanic.Request) -> sanic.HTTPResponse:
    return exc_req(post_calc_bmr, request)


@app.route("/calc/body-fat", methods=["POST"])
async def api_post_calc_bodyfat(request: sanic.Request) -> sanic.HTTPResponse:
    return exc_req(post_calc_body_fat, request)


@app.route("/calc/lbm-limits", methods=["POST"])
async def api_post_calc_lbllimits(request: sanic.Request) -> sanic.HTTPResponse:
    return exc_req(post_calc_lb_limits, request)


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Account functions
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@app.route("/register", methods=["POST"])
async def api_post_register(request: sanic.Request) -> sanic.HTTPResponse:
    return exc_req(post_register, request)


@app.route("/login", methods=["POST"])
async def api_post_login(request: sanic.Request) -> sanic.HTTPResponse:
    return exc_req(post_login, request)


@app.route("/v2/login", methods=["POST"])
async def api_post_v2_login(request: sanic.Request) -> sanic.HTTPResponse:
    return exc_req(post_v2_login, request)


@app.route("/email/confirm")
async def api_get_email_confirm(request: sanic.Request) -> sanic.HTTPResponse:
    return exc_req(get_confirm_email, request)


@app.route("/email/change")
async def api_get_email_change(request: sanic.Request) -> sanic.HTTPResponse:
    return exc_req(get_email_change, request)


@app.route("/password/change")
async def api_get_password_change(request: sanic.Request) -> sanic.HTTPResponse:
    return exc_req(get_password_change, request)


@app.route("/username/forgot", methods=["POST"])
async def api_post_username_forgot(request: sanic.Request) -> sanic.HTTPResponse:
    return exc_req(post_username_forgot, request)


@app.route("/password/new/request")
async def api_get_password_new_request(request: sanic.Request) -> sanic.HTTPResponse:
    return exc_req(post_password_new_request, request)


@app.route("/password/new/reset")
async def api_get_password_new_reset(request: sanic.Request) -> sanic.HTTPResponse:
    return exc_req(post_password_new_reset, request)


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Sync functions
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@app.route("/sync", methods=["GET", "POST"])
async def api_get_post_sync(request: sanic.Request) -> sanic.HTTPResponse:
    return exc_req(opt_sync, request)
