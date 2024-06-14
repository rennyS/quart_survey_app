from functools import wraps
from quart import g, redirect, url_for

def admin_required(f):
    @wraps(f)
    async def decorated_function(*args, **kwargs):
        if not g.user or not g.user.is_admin:
            return redirect(url_for('auth.login'))
        return await f(*args, **kwargs)
    return decorated_function
