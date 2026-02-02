"""
Authentication and Authorization Decorators

These decorators provide security middleware for Flask routes.
Created as part of emergency security patch for CRPF MHMS deployment.
"""

from functools import wraps
from flask import session, jsonify
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


def require_admin(f):
    """
    Decorator to require admin authentication for a route.

    Checks:
    1. User is logged in (session contains user_id)
    2. Session has not expired
    3. User role is 'admin'

    Returns 401 if not authenticated, 403 if not authorized.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if user is logged in
        if 'user_id' not in session:
            logger.warning(f"Unauthorized access attempt to {f.__name__}: No session")
            return jsonify({
                'error': 'Authentication required',
                'code': 'AUTH_REQUIRED'
            }), 401

        # Check if session is expired
        if 'expires_at' in session:
            try:
                expires_at = datetime.fromisoformat(session['expires_at'])
                if datetime.now() > expires_at:
                    logger.warning(f"Expired session access attempt by {session.get('user_id')}")
                    session.clear()
                    return jsonify({
                        'error': 'Session expired. Please login again.',
                        'code': 'SESSION_EXPIRED'
                    }), 401
            except (ValueError, TypeError) as e:
                logger.error(f"Invalid session expires_at format: {e}")
                session.clear()
                return jsonify({
                    'error': 'Invalid session. Please login again.',
                    'code': 'SESSION_INVALID'
                }), 401

        # Check if user is admin
        if session.get('role') != 'admin':
            logger.warning(f"Non-admin access attempt to {f.__name__} by {session.get('user_id')}")
            return jsonify({
                'error': 'Admin access required',
                'code': 'ADMIN_REQUIRED'
            }), 403

        return f(*args, **kwargs)
    return decorated_function


def require_auth(f):
    """
    Decorator to require any authenticated user (admin or soldier).

    Checks:
    1. User is logged in (session contains user_id)
    2. Session has not expired

    Returns 401 if not authenticated.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if user is logged in
        if 'user_id' not in session:
            logger.warning(f"Unauthorized access attempt to {f.__name__}: No session")
            return jsonify({
                'error': 'Authentication required',
                'code': 'AUTH_REQUIRED'
            }), 401

        # Check if session is expired
        if 'expires_at' in session:
            try:
                expires_at = datetime.fromisoformat(session['expires_at'])
                if datetime.now() > expires_at:
                    logger.warning(f"Expired session access attempt by {session.get('user_id')}")
                    session.clear()
                    return jsonify({
                        'error': 'Session expired. Please login again.',
                        'code': 'SESSION_EXPIRED'
                    }), 401
            except (ValueError, TypeError) as e:
                logger.error(f"Invalid session expires_at format: {e}")
                session.clear()
                return jsonify({
                    'error': 'Invalid session. Please login again.',
                    'code': 'SESSION_INVALID'
                }), 401

        return f(*args, **kwargs)
    return decorated_function
