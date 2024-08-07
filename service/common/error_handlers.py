######################################################################
# Copyright 2016, 2024 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
######################################################################
"""
Module: error_handlers
"""

from flask import current_app as app  # Import Flask application
from service.models import DataValidationError
from service import api
from . import status  # pylint: disable=E0611


######################################################################
# Error Handlers
######################################################################


@api.errorhandler(DataValidationError)
def request_validation_error(error):
    """Handles Value Errors from bad data"""
    message = str(error)
    app.logger.error(message)
    return {
        "status": status.HTTP_400_BAD_REQUEST,
        "error": "Bad Request",
        "message": message,
    }, status.HTTP_400_BAD_REQUEST


@app.errorhandler(status.HTTP_404_NOT_FOUND)
def not_found(error):
    """Handles resources not found with 404_NOT_FOUND"""
    app.logger.warning(str(error))
    return {
        "status": status.HTTP_404_NOT_FOUND,
        "error": "Not Found",
        "message": str(error),
    }, status.HTTP_404_NOT_FOUND


@app.errorhandler(status.HTTP_405_METHOD_NOT_ALLOWED)
def method_not_supported(error):
    """Handles unsupported HTTP methods with 405_METHOD_NOT_SUPPORTED"""
    app.logger.warning(str(error))
    return {
        "status": status.HTTP_405_METHOD_NOT_ALLOWED,
        "error": "Method not Allowed",
        "message": str(error),
    }, status.HTTP_405_METHOD_NOT_ALLOWED


@app.errorhandler(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
def mediatype_not_supported(error):
    """Handles unsupported media requests with 415_UNSUPPORTED_MEDIA_TYPE"""
    app.logger.warning(str(error))
    return {
        "status": status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        "error": "Unsupported media type",
        "message": str(error),
    }, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE


@app.errorhandler(status.HTTP_500_INTERNAL_SERVER_ERROR)
def internal_server_error(error):
    """Handles unexpected server error with 500_SERVER_ERROR"""
    app.logger.error(str(error))
    return {
        "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
        "error": "Internal Server Error",
        "message": str(error),
    }, status.HTTP_500_INTERNAL_SERVER_ERROR
