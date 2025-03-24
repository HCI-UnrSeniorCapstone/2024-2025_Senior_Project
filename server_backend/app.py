from flask import Flask, make_response, request, jsonify, render_template
from app import create_app
from flask_wtf.csrf import CSRFProtect
from flask import current_app

# Create the app
app = create_app()

# Initialize CSRF protection
# csrf = CSRFProtect(app)


# Ensure CSRF token is available on every page via cookie
@app.before_request
def before_request():
    if request.endpoint and not request.is_xhr:
        # Generate CSRF token
        csrf_token = app.csrf.generate_csrf()

        # Set the CSRF token as a cookie to be used on the frontend
        response = make_response()  # Empty response as we don't render any HTML
        response.set_cookie("XSRF-TOKEN", csrf_token)  # Send CSRF token in cookies
        return response


@app.after_request
def after_request(response):
    # Optional: you can also set the CSRF token as a response header for the frontend
    # response.headers["X-CSRF-TOKEN"] = csrf.generate_csrf()
    return response


if __name__ == "__main__":
    # CHANGE THE HOST AND DEBUG WHEN PRODUCTION TIME
    app.run(host="0.0.0.0", debug=True)
