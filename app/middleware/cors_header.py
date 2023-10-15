def add_cors_headers(response):
    # Replace with your frontend domain
    frontend_domain = 'http://localhost:3000'
    # frontend_domain = 'https://www.enetworksagencybanking.com.ng'
    response.headers['Access-Control-Allow-Origin'] = frontend_domain
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS, PATCH'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    return response