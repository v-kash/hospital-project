from  rest_framework.views import exception_handler
def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        print(f"Status Code: {response.status_code}")
        print(f"Response Data: {response.data}")

        if response.status_code == 400:
            response.data = {
                'error': "There was an issue with your request.",
                'details': response.data
            }
        elif response.status_code == 404:
            response.data = {
                'error': "Resource not found.",
                'details': response.data
            }
 
    return response
