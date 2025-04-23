from app import create_app
import sys
import os

# NOTE: THIS IS USED FOR DEVELOPMENT MODE
env = sys.argv[1] if len(sys.argv) > 1 else "development"
# Create the app
app = create_app(env)

if __name__ == "__main__":
    print(f"Running Flask app in {env} mode")
    app.run(
        host="0.0.0.0",
        port=int(os.getenv("VITE_APP_DEVELOPMENT_BACKEND_PORT")),
        debug=(env == "development"),
    )  # DEVELOPMENT mode
