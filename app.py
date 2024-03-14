#!/usr/bin/env python3
import weaviate
import weaviate.classes as wvc
import os
import requests
import json

from flask import Flask,request,render_template
from flask import make_response, jsonify
from json import loads,dumps,load

from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True

CLUSTER_URL = os.getenv('CLUSTER_URL')
WEAVIATE_AuthApiKey = os.getenv('WEAVIATE_AuthApiKey')
GPT_KEY1 = os.getenv('GPT_KEY1')

@app.route('/')
def hello():
    return render_template('hello.html')

@app.route('/test', methods=['GET'])
def test():
    return make_response(jsonify({'message': 'test route'}), 200)

@app.route('/recommend/', methods=['GET'])
def get_user():
    '''
        get data from frontend then sent free text into llm for generate recommended places.
    '''
    try:
        return make_response(jsonify({'message': 'succeed'}), 200)
    except Exception as e:
        return make_response(jsonify({'message': e}), 500)
    
@app.route('/v1/nodes/Question2', methods=['GET'])
def get_result():
    try:
        query = request.args.get('query')
        if not query:
            return make_response(jsonify({'message': 'Query parameter is missing.'}), 400)

        client = weaviate.connect_to_wcs(
            cluster_url=CLUSTER_URL,
            auth_credentials=weaviate.auth.AuthApiKey(WEAVIATE_AuthApiKey),
            headers={
                "X-OpenAI-Api-Key": GPT_KEY1
            }
        )

        questions = client.collections.get("Question2")

        response = questions.query.near_text(
            query=query,
            limit=2
        )

        result = response.objects[0].properties
        client.close()
        return make_response(jsonify({'message': result}), 200)
    except weaviate.exceptions.WeaviateGRPCUnavailableError as e:
        return make_response(jsonify({'message': f"Weaviate gRPC connection error: {str(e)}"}), 500)
    except Exception as e:
        return make_response(jsonify({'message': str(e)}), 500)