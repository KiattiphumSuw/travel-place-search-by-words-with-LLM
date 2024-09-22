import os
import weaviate
import weaviate.classes as wvc
from dotenv import load_dotenv
from flask import Flask, jsonify, make_response, render_template, request
from weaviate.classes.init import Auth

load_dotenv()
app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True

GPT_KEY1 = os.getenv("GPT_KEY1")
headers = {"X-OpenAI-Api-Key": GPT_KEY1}
weaviate_url = os.getenv("CLUSTER_URL")
weaviate_api_key = os.getenv("WEAVIATE_AuthApiKey")
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


@app.route("/v1/nodes/recommend", methods=["GET"])
def get_recommend():
    query = request.args.get("query")
    result_all = {"activities": {}, "accommodations": {}}
    print(query)
    try:
        # Query for Activity recommendations
        activity_response = client.graphql_raw_query(
            f"""
            {{
                Get {{
                    Activity_Embedded(
                        nearText: {{
                            concepts: ["{query}"]
                        }},
                        limit: 5
                    ) {{
                        activity_name
                        about_and_tags
                        reviews
                    }}
                }}
            }}
            """
        )
        # print(activity_response.__dict__["get"]["Activity_Embedded"])
        for activity in activity_response.__dict__["get"]["Activity_Embedded"]:
            activity_name = activity.get("activity_name", "Unknown Activity")
            about_and_tags = activity.get("about_and_tags", "Description not available")
            reviews = activity.get("reviews", [])
            result_all["activities"][activity_name] = {
                "Description": about_and_tags,
                "People also reviews": reviews if reviews else ["No reviews available"],
            }
        # print(result_all)

        # Query for Accommodation recommendations
        accommodation_response = client.graphql_raw_query(
            f"""
            {{
                Get {{
                    Accommodation_Embedded(
                        nearText: {{
                            concepts: ["{query}"]
                        }},
                        limit: 5
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
            reviews = accommodation.get("reviews", [])
            result_all["accommodations"][accommodation_name] = {
                "Description": about_and_tags,
                "People also reviews": reviews if reviews else ["No reviews available"],
            }

        return make_response(jsonify({"message": result_all}), 200)

    except weaviate.exceptions.WeaviateGRPCUnavailableError as e:
        return make_response(
            jsonify({"message": f"Weaviate gRPC connection error: {str(e)}"}), 500
        )
    except Exception as e:
        return make_response(jsonify({"message": str(e)}), 500)


@app.route("/v1/nodes/QA", methods=["GET"])
def get_QA():
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


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
    # close the connection only when the app is closed
    client.close()
