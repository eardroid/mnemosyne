import os
import sys

from demo.web_dashboard import app, api_reset

with app.test_request_context('/api/reset', method='POST'):
    try:
        response = api_reset()
        print(response.get_json())
    except Exception as e:
        import traceback
        traceback.print_exc()
