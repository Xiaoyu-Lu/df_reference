import os
import sys
import json
import random
import string
import copy
from flask import Flask
from flask import request
from db import update_user_parameters
from db import update_search_results_for_user
from db import remove_user_data
from db import search

app = Flask(__name__)

def is_browser(ua_string):
    return ua_string.split("/")[0].lower() == "mozilla"

@app.route("/", methods=["POST", "GET"])
def process_dialogflow_request():
    # show welcome message if viewing from a broswer
    msg_content = "This is the webhook of Dom&Loewi."
    if is_browser(request.headers["User-Agent"]):
        return "<html><body><h1>{}</body></html>".format(msg_content)

    # process request
    query_text = request.json["queryResult"]["queryText"]
    parameters = request.json["queryResult"]["parameters"]
    intent = request.json["queryResult"]["intent"]["displayName"]
    session = request.json["session"]

    # process based on the domain
    if "Attraction" in intent:
        return process_attraction(query_text, parameters, intent, session)

    if len(request.json["queryResult"]["intent"]) > 2:
        is_end = request.json["queryResult"]["intent"]["endInteraction"]

    # remove user data if the session is ended
    if intent == is_end:
        remove_user_data(session)

        return {
            "fulfillmentText": random.choice([
                "Thank you for using our service!",
                "You're welcome, have a nice day!",
                "Thank you! We're looking forward to assisting you again."
            ])
        }
    
    # the code reaches here when webhook is enabled on an intent
    # but this intent is not yet included in our backend
    return json.dumps(
        {
            "fulfillmentText": "Sorry, there is something wrong."
        }
    )


def is_empty_parameter_dict(parameters):
    """
    Check if the current parameter dict is empty.

    If the user does not give any information, we need to prompt 
    the user to give more
    """

    for entity_name in parameters:
        # if anything is not empty, the entire dict is not empty
        if len(parameters[entity_name].strip()) > 0:
            return False
    
    return True


def process_attraction(query_text, parameters, intent, session):
    """
    This method handle all requests about attraction
    """

    # continue_search = False
    if intent == "Attraction-Recommend":
        # update parameters
        updated_user_profile = update_user_parameters(parameters, session, ignore_empty=True)
        # print('user_profile :',updated_user_profile)
        if not updated_user_profile:
            # suggest parameters that the user has not yet given
            return json.dumps(
                {
                    "fulfillmentText": random.choice(
                        [
                            "Sorry, but the information you gave is already"
                            + " in the request. Would you mind adding another"
                            + " piece of information?",
                            "The information is already given. Mind adding"
                            + " some other information?",
                            "Sorry, but the information is already given. "
                            + "Could you add some other information?",
                        ]
                    )

                
                }
            )

        # get new user data
        user_parameters = updated_user_profile["parameters"]
        # print('user_parameters',user_parameters)
        # if no parameter present, ask the user to give some
        if is_empty_parameter_dict(user_parameters):
            return {
                "fulfillmentText": random.choice([
                    "Sure! Can you tell me more?",
                    "My pleasure! Can you tell me more?"
                ])
            }

        # otherwise start search and return results
        results = search(user_parameters, "attraction")
        print('get %d results'%len(results))
        if len(results) == 0:
            return {
                "fulfillmentText": random.choice([
                    "Unfortunately, I couldn't find any matching attraction for you. Could you try something different?",
                    "Sorry, but I wasn't able to find a matching attraction for you. Can you change some of your requests?"
                ])
            }

        # update search results here because we need to store them for the next interaction
        # so that we know what was there previously
        print('update!!!')
        update_search_results_for_user(results, "attraction", session)

        # too many results
        if len(results) > 2:
            print('cool')
            return {
                "fulfillmentText": random.choice([
                    "Sure! But I found {} attractions that match your needs. Can you add more information to help narrow it down?".format(len(results)),
                    "No problem! But I found {} attractions that match your needs. Could you help narrow it down with more information?".format(len(results)),
                ])
            }

        if len(results) == 1:
            return {
                "fulfillmentText": random.choice([
                    "I found it! Do you want more information about it now?",
                    "Good news! I found the attraction. Do you want the address and phone number now?"
                ])
            }

        # report details about the alternatives 
        return {
            "fulfillmentText": random.choice([
                "I found {} attractions for you.".format(len(results)),
                "There are {} attractions that match your needs.".format(len(results))
            ])
        }

if __name__ == "__main__":
    port = os.environ.get(
        "PORT", int(sys.argv[1]) if len(sys.argv) >= 2 else 5000
    )
    app.run(host="0.0.0.0", port=port)
