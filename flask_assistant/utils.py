from __future__ import absolute_import
from typing import Dict, Any
import os
import sys
import json
import logging
from google.auth import jwt
from flask_assistant.core import Assistant
from . import logger


logger.setLevel(logging.INFO)


GOOGLE_PUBLIC_KEY = json.loads(os.environ.get('GOOGLE_PUBLIC_KEY'))

# def get_public_key(project_id, location_id, key_ring_id, key_id, version_id):
#     """
#     Get the public key for an asymmetric key.
#
#     Args:
#         project_id (string): Google Cloud project ID (e.g. 'my-project').
#         location_id (string): Cloud KMS location (e.g. 'us-east1').
#         key_ring_id (string): ID of the Cloud KMS key ring (e.g. 'my-key-ring').
#         key_id (string): ID of the key to use (e.g. 'my-key').
#         version_id (string): ID of the key to use (e.g. '1').
#
#     Returns:
#         PublicKey: Cloud KMS public key response.
#
#     """
#
#     # Import the client library.
#     from google.cloud import kms
#
#     # Create the client.
#     client = kms.KeyManagementServiceClient()
#
#     # Build the key version name.
#     key_version_name = client.crypto_key_version_path(project_id, location_id, key_ring_id, key_id, version_id)
#
#     # Call the API.
#     public_key = client.get_public_key(request={'name': key_version_name})
#     print('Public key: {}'.format(public_key.pem))
#     return public_key

def import_with_3(module_name, path):
    import importlib.util

    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def import_with_2(module_name, path):
    import imp

    return imp.load_source(module_name, path)


def get_assistant(filename):
    """Imports a module from filename as a string, returns the contained Assistant object"""

    agent_name = os.path.splitext(filename)[0]

    try:
        agent_module = import_with_3(agent_name, os.path.join(os.getcwd(), filename))

    except ImportError:
        agent_module = import_with_2(agent_name, os.path.join(os.getcwd(), filename))

    for name, obj in agent_module.__dict__.items():
        if isinstance(obj, Assistant):
            return obj


def decode_token(token, client_id):
    decoded = jwt.decode(token, certs=GOOGLE_PUBLIC_KEY, verify=True, audience=client_id)
    return decoded
    
