#!/usr/bin/env python3
import weaviate
import weaviate.classes as wvc
import os

from flask import Flask,request,render_template
from flask import make_response, jsonify

# from pysentimiento import create_analyzer

from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True

CLUSTER_URL = os.getenv('CLUSTER_URL')
WEAVIATE_AuthApiKey = os.getenv('WEAVIATE_AuthApiKey')
GPT_KEY1 = os.getenv('GPT_KEY1')
# analyzer = create_analyzer(task="sentiment", lang="en")

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
    
@app.route('/v1/nodes/travelPlanner', methods=['GET'])
def get_result():
    try:
        query = request.args.get('query')
        if not query:
            return make_response(jsonify({'message': 'Query parameter is missing.'}), 400)
        # print(analyzer.predict(query))

        client = weaviate.connect_to_wcs(
                cluster_url=CLUSTER_URL,
                auth_credentials=weaviate.auth.AuthApiKey(WEAVIATE_AuthApiKey),
                headers={
                    "X-OpenAI-Api-Key": GPT_KEY1  # Replace with your inference API key
                }
            )

        questions = client.collections.get("Review7")
        result_all = dict()
        recommended_dict = dict()
        top_k = 2
        place_counter = 0
        multiple_index = 0

        while(place_counter < top_k):
            multiple_index += 1
            print(f"find {multiple_index} times")
            place_counter = 0
            place_description = dict()
            
            if(multiple_index == 4):
                break
            
            response_re = questions.query.near_text(
                query=query,
                limit=5*multiple_index
            )

            questions = client.collections.get("Description")
            
            for result_object in response_re.objects:
                resname_review = result_object.properties["restaurant_name"]
                review_review = result_object.properties["reviews"]

                if resname_review not in recommended_dict.keys():
                    place_counter += 1
                    recommended_dict[resname_review] = []
                recommended_dict[resname_review] += [review_review]

        
        for place in recommended_dict.keys():
            response_des = questions.query.fetch_objects(
                filters=wvc.query.Filter.by_property("restaurant_name").contains_any([place]),
                limit=1
            )

            for o in response_des.objects:
                place_description[place] = o.properties

        for i, place in enumerate(recommended_dict.keys()):
            if (i < top_k):
                result_all[place] = {"Description": place_description[place],
                                     "People also reviews": recommended_dict[place]}
        print(result_all)
            
        return make_response(jsonify({'message': result_all}), 200)
    except weaviate.exceptions.WeaviateGRPCUnavailableError as e:
        return make_response(jsonify({'message': f"Weaviate gRPC connection error: {str(e)}"}), 500)
    except Exception as e:
        return make_response(jsonify({'message': str(e)}), 500)