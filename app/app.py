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
from db import get_user_profile
from db import search_from_results


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
    parameters = request.json["queryResult"]["parameters"]
    intent = request.json["queryResult"]["intent"]["displayName"]
    session = request.json["session"]


    if len(request.json["queryResult"]["intent"]) > 2:
        is_end = request.json["queryResult"]["intent"]["endInteraction"]

        # remove user data if the session is ended
        if is_end == True:
            remove_user_data(session)

            return {
                "fulfillmentText": random.choice([
                    "Thank you for using our service!",
                    "You're welcome, have a nice day!",
                    "Thank you! We're looking forward to assisting you again."
                ])
            }
    # process based on the domain
    if "Attraction-Recommend" in intent:
        return process_attraction(parameters, intent, session)


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


def printout_result(result):

    # PARA = ["address", "area", "entrance fee", "location", "name", "openhours", "phone", "postcode", "pricerange", "type"]
    report = []
    report.append("The {} located in the {} of the Cambridge.\n".format(result['name'].capitalize(), result['area']))
    report.append("There will be {} entrance fee.\n".format(result['entrance fee'] if result['entrance fee'] != 'free' else 'no'))
    return ''.join(report)

def printout_detailed_result_openhour(result):
    report = []
    if result['openhours'] != '?':
        report.append("{}.\n".format(result['openhours'].capitalize()))
    else:
        report.append("Sorry, the openhours of the {} is not available.".format(result['name'].capitalize()))
    return ''.join(report)

def printout_detailed_result(result):

    # PARA = ["address", "area", "entrance fee", "location", "name", "openhours", "phone", "postcode", "pricerange", "type"]
    report = []
    report.append("The number of {} is {}.\n".format(result['name'].capitalize(), result['phone']))
    report.append("The address is {}.".format(result['address']))
    return ''.join(report)

def process_attraction(parameters, intent, session):
    """
    This method handle all requests about attraction
    """
    if intent == "Attraction-Recommend - hour":
        user_results = get_user_profile(session)["results"]["attraction"]

        if not user_results:
            return {
                "fulfillmentText": "Sorry, I'm not sure which one you are asking about. Would you "
                + "mind adding or changing some information? "
                + "Thank you!"
            }
        
        if len(user_results) == 1:
            report = printout_detailed_result_openhour(user_results[0])
            return {
                "fulfillmentText": random.choice([
                    "Got it! {}".format(report),
                    "Found it! {}".format(report)
                ])
            }


    if intent == "Attraction-Recommend - choose":
        user_results = get_user_profile(session)["results"]["attraction"]

        if not user_results:
            return {
                "fulfillmentText": "Sorry, I'm not sure which one you are asking about. Would you "
                + "mind adding or changing some information? "
                + "Thank you!"
            }
        
        if len(user_results) > 1:
            index = 0

            if parameters['index_to_choose'] == '1':
                index = 0
            elif parameters['index_to_choose'] == '2':
                index = 1

            report = printout_detailed_result(user_results[index])
            update_search_results_for_user(user_results, "attraction", session)
            return {
                "fulfillmentText": random.choice([
                    "Cool! {}".format(report),
                    "Nice! {}".format(report)
                ])
            }

    continue_search = False
    if intent == "Attraction-Recommend - refine_search":
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
        user_results = get_user_profile(session)["results"]["attraction"]

        if user_results is None:
            return {
                "fulfillmentText": "Sorry, I'm not sure which one you are asking about. Would you "
                + "mind adding or changing some information? "
                + "Thank you!"
            }

        matched_results = search_from_results(parameters, "attraction", session)

        if len(matched_results) > 1:
            report = []
            # provide them the first two to compare
            report.append("I found two results for you. THE FIRST ONE: \n")
            report.append(printout_result(matched_results[0]))
            report.append("\nTHE SECOND ONE: \n")
            report.append(printout_result(matched_results[1]))
            update_search_results_for_user(matched_results, "attraction", session)
            return {
                "fulfillmentText":"{}\nWhich one do you prefer?".format(" ".join(report))
            }

        if len(matched_results) == 1:
            report = printout_result(matched_results[0])
            update_search_results_for_user(matched_results, "attraction", session)
            return {
                "fulfillmentText": random.choice([
                    "I found it! {}".format(" ".join(report)),
                    "Good news! {}".format(" ".join(report))
                ])
            }

        # prompt the user again if there are no matches
        if len(matched_results) == 0:
            return {
                "fulfillmentText":(
                    "Sorry, I can't find the one you're referring to. Would you mind changing "
                    + "some information so that I can get the one place for you? Thanks!"
                )
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

        # if intent == "Attraction-Recommend":
        #     # we also need to clean any stored results because this is an entirely new request
        #     # 
        #     # UNLESS this logic is called with should_start_search, meaning this block of code
        #     # is used just for the search with the already updated parameters from a different
        #     # intent block
        #     update_search_results_for_user([], "attraction", session)

        # prompt the user again if nothing is changed
        if updated_user_profile is None:
            return {
                "fulfillmentText": random.choice([
                    "Sorry, but you already give all the information. Could you add more?",
                    "Sorry, the information is already given. Would you mind adding some different information?"
                ])
            }

        # get user data
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
            report = printout_result(results[0])
            return {
                "fulfillmentText": random.choice([
                    "I found it! {}".format(report),
                    "Good news! {}".format(report)
                ])
            }

        # report details about the alternatives 
        return {
            "fulfillmentText": random.choice([
                "I found {} attractions for you.".format(len(results)),
                "There are {} attractions that match your needs.".format(len(results))
            ])
        }
    return {
                "fulfillmentText": random.choice([
                    "Sorry, I cannot find you anything. Please try another way.",
                    "Sorry, I am in outer space right now."
                ])
            }

if __name__ == "__main__":
    port = os.environ.get(
        "PORT", int(sys.argv[1]) if len(sys.argv) >= 2 else 5000
    )
    app.run(host="0.0.0.0", port=port)
