"""Unit tests for core security module"""

import pytest
from core import hash_password, verify_password, create_access_token, decode_access_token
from fastapi import HTTPException
import time

def test_hash_password():
    """Test password hashing"""
    password = "mySecurePassword123"
    hashed = hash_password(password)
    
    assert hashed != password
    assert len(hashed) > 20

def test_verify_password():
    """Test password verification"""
    password = "mySecurePassword123"
    hashed = hash_password(password)
    
    assert verify_password(password, hashed)
    assert not verify_password("wrongpassword", hashed)

def test_create_access_token():
    """Test JWT token creation"""
    data = {"sub": "user_123", "email": "test@example.com"}
    secret = "test-secret-key"
    
    token = create_access_token(data, secret, expires_hours=1)
    
    assert isinstance(token, str)
    assert len(token) > 0

def test_decode_access_token():
    """Test JWT token decoding"""
    data = {"sub": "user_123", "email": "test@example.com"}
    secret = "test-secret-key"
    
    token = create_access_token(data, secret, expires_hours=1)
    decoded = decode_access_token(token, secret)
    
    assert decoded["sub"] == "user_123"
    assert decoded["email"] == "test@example.com"

def test_decode_invalid_token():
    """Test decoding invalid token"""
    secret = "test-secret-key"
    invalid_token = "invalid.token.here"
    
    with pytest.raises(HTTPException) as exc_info:
        decode_access_token(invalid_token, secret)
    
    assert exc_info.value.status_code == 401
