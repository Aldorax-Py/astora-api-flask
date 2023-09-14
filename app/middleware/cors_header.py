def add_cors_headers(response):
    frontend_domain = 'http://localhost:3000'
    response.headers['Access-Control-Allow-Origin'] = frontend_domain
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS, PATCH'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    return response
