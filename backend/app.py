from flaskr import create_app
from flaskr.config import ProductionConfig
app = create_app(ProductionConfig())

if __name__ == "__main__":
    app.run(debug=True, port=5000)
