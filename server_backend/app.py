from app import create_app

# Create the app
app = create_app()

if __name__ == "__main__":
    # CHANGE THE HOST AND DEBUG WHEN PRODUCTION TIME
    app.run(host="0.0.0.0", debug=True)
