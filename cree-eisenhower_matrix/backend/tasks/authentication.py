"""
Supabase JWT authentication backend for Django REST Framework.
"""
import jwt
import os
from rest_framework import authentication
from rest_framework import exceptions
from django.contrib.auth.models import User


class SupabaseAuthentication(authentication.BaseAuthentication):
    """
    Custom authentication class that validates Supabase JWT tokens.
    """
    
    def authenticate(self, request):
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            return None
            
        try:
            # Extract token from "Bearer <token>"
            token = auth_header.split(' ')[1]
            
            # Get Supabase JWT secret (anon key for client tokens)
            supabase_jwt_secret = os.getenv('SUPABASE_ANON_KEY')
            
            if not supabase_jwt_secret:
                raise exceptions.AuthenticationFailed('Supabase configuration missing')
            
            # Decode and verify the JWT token
            payload = jwt.decode(
                token,
                supabase_jwt_secret,
                algorithms=['HS256'],
                audience='authenticated',
                options={"verify_signature": True}
            )
            
            # Extract user ID from token
            user_id = payload.get('sub')
            email = payload.get('email')
            
            if not user_id:
                raise exceptions.AuthenticationFailed('Invalid token payload')
            
            # Get or create Django user for this Supabase user
            # We use the Supabase UUID as the username
            user, created = User.objects.get_or_create(
                username=user_id,
                defaults={
                    'email': email or '',
                    'is_active': True,
                }
            )
            
            # Update email if it changed
            if email and user.email != email:
                user.email = email
                user.save()
            
            return (user, token)
            
        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed('Token has expired')
        except jwt.InvalidTokenError:
            raise exceptions.AuthenticationFailed('Invalid token')
        except IndexError:
            raise exceptions.AuthenticationFailed('Invalid authorization header format')
        except Exception as e:
            raise exceptions.AuthenticationFailed(f'Authentication failed: {str(e)}')
    
    def authenticate_header(self, request):
        return 'Bearer'
