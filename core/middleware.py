"""
Cloudflare optimization middleware for Django and Wagtail.
Handles client IP restoration, admin cache prevention, and media edge caching.
"""


class CloudflareMiddleware:
    """
    Middleware optimized for Cloudflare integration:
    1. Extracts real visitor IP from Cloudflare's CF-Connecting-IP header for accurate
       logging, security checks, and Wagtail user audit trails.
    2. Ensures Wagtail and Django admin endpoints always carry 'no-store, private'
       Cache-Control headers to prevent edge proxies (Cloudflare) from caching sensitive backend pages.
    3. Adds edge cache headers for media files (/media/*) so Cloudflare caches uploaded assets,
       dramatically reducing Python process memory and file streaming overhead.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        cf_ip = request.META.get("HTTP_CF_CONNECTING_IP")
        if cf_ip:
            # First IP if multiple are passed
            real_ip = cf_ip.split(",")[0].strip()
            request.META["REMOTE_ADDR"] = real_ip

        response = self.get_response(request)

        path = request.path_info

        # 1. Safeguard: prevent Cloudflare from ever caching admin and authenticated areas
        if (
            path.startswith("/admin/")
            or path.startswith("/django-admin/")
            or "preview" in path
        ):
            response["Cache-Control"] = "private, no-cache, no-store, must-revalidate, max-age=0"
            response["Pragma"] = "no-cache"

        # 2. Allow Cloudflare to cache media files at the edge to save server RAM/CPU
        elif path.startswith("/media/") and response.status_code == 200:
            if "Cache-Control" not in response or "private" not in response.get("Cache-Control", ""):
                response["Cache-Control"] = "public, max-age=2592000, stale-while-revalidate=86400"

        return response
