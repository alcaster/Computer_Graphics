from flask import Flask, render_template, Blueprint, request, jsonify
from flask_restplus import Api, Resource, fields
from io import BytesIO
from PIL import Image
import numpy as np
import base64

from src.image_processing import process_image

app = Flask(__name__)
blueprint = Blueprint('api', __name__, url_prefix='/api')
api = Api(blueprint)

app.register_blueprint(blueprint)


@app.route('/')
def hello_world():
    return render_template('index.html')


photo_fields = api.model('Test', {
    'img': fields.String(required=True, description='Image to process'),
    'mode': fields.String(required=True, description='Selected operation on image', example='inverse'),
    'n': fields.Float(required=False, description='Optional parameter for some operations', example='1.2'),
    'k': fields.Float(required=False, description='Optional parameter for some operations', example='1.2'),
})


@api.route('/process_photo')
class ProcessPhoto(Resource):
    @api.expect(fields=photo_fields)
    def post(self):
        all_params = request.get_json()
        processed = process_image(all_params)
        transformed = Image.fromarray(processed)
        if transformed.mode != 'RGB':
            transformed = transformed.convert('RGB')

        buffered = BytesIO()
        transformed.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
        data = {
            "img": img_str,
        }
        return jsonify(data)


if __name__ == '__main__':
    app.run(debug=True)
