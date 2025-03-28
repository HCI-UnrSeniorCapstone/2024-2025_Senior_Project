from flask import Blueprint, current_app, request, jsonify, Response, send_file
from app.utility.db_connection import get_db_connection

bp = Blueprint("permutations", __name__)


from app.utility.permutations import (
    get_within_perm, 
    get_between_perm,
    calc_perm_hash,
)


# Endpoint will be dev here next