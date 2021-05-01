#!/bin/sh
redis-server --daemonize yes
. /pagermaid/venv/bin/activate
/usr/bin/env python3 -m pagermaid
