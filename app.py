print(">>> Running backend/app.py <<<")
from flask import Flask, render_template
import os

# Get the project root directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Create Flask app
app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "frontend", "templates"),
    static_folder=os.path.join(BASE_DIR, "frontend", "static")
)
#home route
@app.route("/")
def home():
    print("✅ Home route executed")
    return render_template("index.html")

# Run the application
if __name__ == "__main__":
    app.run(debug=True)