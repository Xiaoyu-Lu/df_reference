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
    if intent == "Attraction-Recommend":
        return {
                "fulfillmentText": random.choice([
                    "testing testing",
                    "great! go and find the bug"
                ])
            }
    continue_search = False
    if intent == "Attraction-Recommend - update parameters":
        # update parameters
        # since this is updating information
        # we should only update parameters that are NOT EMPTY
        updated_user_profile = update_user_parameters(parameters, session, ignore_empty=True)

        # If we can't update anything new. Prompt the user to try again.
        if updated_user_profile is None:
            return {
                "fulfillmentText": random.choice([
                    "Sorry, I couldn't find anything new from what you just said. Would you mind trying again?",
                    "I'm sorry that I couldn't get anything new from what you just said. Could you try again?"
                ])
            }

        # only continue search with the updated parameters if there is anything new
        # given by the user
        continue_search = True

    if intent == "Attraction-Recommend" or continue_search:
        if intent == "Attraction-Recommend":
            # update parameters
            # since this is the beginning of the conversation
            # we should not ignore empty parameters because that is the user's initial request
            # 
            # UNLESS this logic is called with should_start_search, meaning this block of code
            # is used just for the search with the already updated parameters from a different
            # intent block
            updated_user_profile = update_user_parameters(parameters, session, ignore_empty=False)

        # prompt the user to give more information if nothing is given
        if is_empty_parameter_dict(parameters):
            return {
                "fulfillmentText": random.choice([
                    "Sure! Can you tell me more?",
                    "My pleasure! Can you tell me more?"
                ])
            }

        if intent == "Attraction-Recommend":
            # we also need to clean any stored results because this is an entirely new request
            # 
            # UNLESS this logic is called with should_start_search, meaning this block of code
            # is used just for the search with the already updated parameters from a different
            # intent block
            update_search_results_for_user([], "attraction", session)

        # prompt the user again if nothing is changed
        if updated_user_profile is None:
            return {
                "fulfillmentText": random.choice([
                    "Sorry, but you already give all the information. Could you add more?",
                    "Sorry, the information is already given. Would you mind adding some different information?"
                ])
            }

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
        # print('get %d results'%len(results))
        if len(results) == 0:
            return {
                "fulfillmentText": random.choice([
                    "Unfortunately, I couldn't find any matching attraction for you. Could you try something different?",
                    "Sorry, but I wasn't able to find a matching attraction for you. Can you change some of your requests?"
                ])
            }

        # update search results here because we need to store them for the next interaction
        # so that we know what was there previously
        # print('update!!!')
        update_search_results_for_user(results, "attraction", session)

        # too many results
        if len(results) > 2:
            # print('cool')
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
