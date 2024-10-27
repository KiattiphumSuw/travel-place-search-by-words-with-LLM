import os
import weaviate
import weaviate.classes as wvc
from dotenv import load_dotenv
from flask import Flask, jsonify, make_response, render_template, request
from weaviate.classes.init import Auth
# from intent_chatbot import Intent_Model, Answer_Model
from muti_purpose_chatbot import Chatbot
from weaviate.classes.query import Rerank, MetadataQuery


load_dotenv()
app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True

GPT_KEY1 = os.getenv("OPENAI_APIKEY")
COHERE_KEY = os.getenv("COHERE_KEY")
headers = {"X-OpenAI-Api-Key": GPT_KEY1, "X-Cohere-Api-Key": COHERE_KEY}
weaviate_url = os.getenv("WEAVIATE_URL")
weaviate_api_key = os.getenv("WEAVIATE_API_KEY")
client = weaviate.connect_to_weaviate_cloud(
    cluster_url=weaviate_url,
    auth_credentials=Auth.api_key(weaviate_api_key),
    headers=headers,
)


@app.route("/")
def hello():
    return render_template("hello.html")


@app.route("/test", methods=["GET"])
def test():
    return make_response(jsonify({"message": "test route"}), 200)


@app.route("/recommend/", methods=["GET"])
def get_user():
    """
    get data from frontend then sent free text into llm for generate recommended places.
    """
    try:
        return make_response(jsonify({"message": "succeed"}), 200)
    except Exception as e:
        return make_response(jsonify({"message": e}), 500)

    # @app.route("/v1/nodes/QA", methods=["GET"])
    # def get_QA():
    query = request.args.get("query")
    result_all = {"activities": {}, "accommodations": {}}

    try:
        # Query for Activities
        activity_response = client.graphql_raw_query(
            f"""
            {{
                Get {{
                    Activity_Embedded(
                        ask: {{
                            question: "{query}",
                            properties: ["activity_name"]
                        }},
                        limit: 1
                    ) {{
                        activity_name
                        about_and_tags
                    }}
                }}
            }}
            """
        )

        # Processing activity response
        for activity in activity_response.__dict__["get"]["Activity_Embedded"]:
            activity_name = activity.get("activity_name", "Unknown Activity")
            about_and_tags = activity.get("about_and_tags", "Description not available")
            result_all["activities"][activity_name] = {
                "Description": about_and_tags,
            }

        # Query for Accommodations
        accommodation_response = client.graphql_raw_query(
            f"""
            {{
                Get {{
                    Accommodation_Embedded(
                        ask: {{
                            question: "{query}",
                            properties: ["accommodation_name"]
                        }},
                        limit: 1
                    ) {{
                        accommodation_name
                        about_and_tags
                        reviews
                    }}
                }}
            }}
            """
        )

        # Processing accommodation response
        for accommodation in accommodation_response.__dict__["get"][
            "Accommodation_Embedded"
        ]:
            accommodation_name = accommodation.get(
                "accommodation_name", "Unknown accommodation"
            )
            about_and_tags = accommodation.get(
                "about_and_tags", "Description not available"
            )
            result_all["accommodations"][accommodation_name] = {
                "Description": about_and_tags,
            }

        return make_response(jsonify({"message": result_all}), 200)

    except weaviate.exceptions.WeaviateGRPCUnavailableError as e:
        return make_response(
            jsonify({"message": f"Weaviate gRPC connection error: {str(e)}"}), 500
        )
    except Exception as e:
        return make_response(jsonify({"message": str(e)}), 500)


@app.route("/classify-intent", methods=["POST"])
def classify_intent():
    try:
        data = request.get_json()
        query = data.get("query")
        print(query)
        if not query:
            return jsonify({"error": "No query provided"}), 400

        # Classify intent
        # intent_result = intent_model.classify_intent(query)
        intent_result = chatbot.classify_intent(query)
        print(intent_result)
        # If the intent is "Recommended", get recommendations
        if "Recommended" in intent_result:
            print("Recommended")
            return get_recommend(query)
        else:
            print("Not recommended")
            return get_answer(query)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


def get_answer(query):
    try:
        # Classify intent
        result_all = {"etc": {}}
        # answer_result = answer_model.classify_intent(query)
        answer_result = chatbot.answer_etc(query)
        result_all["etc"][query] = answer_result
        return make_response(jsonify({"message": result_all}), 200)

    except Exception as e:
        return make_response(jsonify({"message": str(e)}), 500)


def get_recommend(query):
    result_all = {"activities": {}, "accommodations": {}, "etc": {}}

    try:
        Activityclient = client.collections.get("Activity_Embedded")
        # Activity Hybrid Search with Rerank
        activity_response = Activityclient.query.hybrid(
            query=query,
            limit=3,
            rerank=Rerank(prop="activity_name", query=query),
            return_metadata=MetadataQuery(score=True),
        )
        # print(activity_response)

        # Process the activity results
        for a in activity_response.objects:
            activity = a.properties
            activity_name = activity.get("activity_name", "Unknown Activity")
            about_and_tags = activity.get("about_and_tags", "Description not available")
            reviews = activity.get("reviews", [])
            # Extract score from rerank if available
            score = a.metadata.rerank_score

            if activity_name in result_all["activities"]:
                # append reviews
                result_all["activities"][activity_name]["People also reviews"].append(
                    reviews
                )
            else:
                result_all["activities"][activity_name] = {
                    "Description": about_and_tags,
                    "People also reviews": (
                        reviews if reviews else ["No reviews available"]
                    ),
                    "Score": score,  # Add the score
                }

        Accommodationclient = client.collections.get("Accommodation_Embedded")
        # Accommodation Hybrid Search with Rerank
        accommodation_response = Accommodationclient.query.hybrid(
            query=query,
            limit=3,
            rerank=Rerank(prop="accommodation_name", query=query),
            return_metadata=MetadataQuery(score=True),
        )

        # Process the accommodation results
        for a in accommodation_response.objects:
            accommodation = a.properties
            # print(accommodation)
            accommodation_name = accommodation.get(
                "accommodation_name", "Unknown accommodation"
            )
            about_and_tags = accommodation.get(
                "about_and_tags", "Description not available"
            )
            reviews = accommodation.get("reviews", [])
            # Extract score from rerank if available
            score = a.metadata.rerank_score
            # print(accommodation.keys())
            # print(score)

            if accommodation_name in result_all["accommodations"]:
                # append reviews
                result_all["accommodations"][accommodation_name][
                    "People also reviews"
                ].append(reviews)
            else:
                result_all["accommodations"][accommodation_name] = {
                    "Description": about_and_tags,
                    "People also reviews": (
                        reviews if reviews else ["No reviews available"]
                    ),
                    "Score": score,  # Add the score
                }
            summarize = chatbot.summarization(result_all["activities"], query).content
            
            result_all["etc"][query] = summarize
        return make_response(jsonify({"message": result_all}), 200)
    except Exception as e:
        return make_response(jsonify({"message": str(e)}), 500)


if __name__ == "__main__":
    chatbot = Chatbot()
    app.run(debug=True, host="0.0.0.0")
    client.close()
