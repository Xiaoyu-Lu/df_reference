"""
This file has all the functionality that works with database.
Everything interaction with the database happens here.

The current working directory is the project root.
Please do not write any code that runs in the app folder.
"""

import json
import copy
import os

# load data files
attraction_db_file = open('attraction_db.json')

# create user db if it does not exist
if not os.path.isfile('user_db.json'):
    with open('user_db.json', "w+") as user_db_file:
        json.dump([], user_db_file, indent=4)
user_db_file = open('user_db.json')

ATTRACTION_DB = json.load(attraction_db_file)
USER_DB = json.load(user_db_file)

attraction_db_file.close()
user_db_file.close()

# build dict for more structured logic
DATATYPE_TO_DB = {
    "attraction": ATTRACTION_DB,
    "user": USER_DB
}


def get_user_profile(session):
    """
    Get the user profile for the current session.
    If it does not exit, create one and store it into the database.
    """

    global DATATYPE_TO_DB

    result = None

    # create one if it does not exist
    for document in DATATYPE_TO_DB["user"]:
        if document["session"] == session:
            result = document
            break
    if result is None:
        new_user_profile = {
            "session": session,
            # results will store the previously matched documents
            # and it is a dict, where the key is the data type
            # and the value is the matched documents.
            # If the value is None, it means:
            # 1) there was no match
            # 2) there are too many matched documents currently
            "results": {
                "attraction": None,
            },
            # stores all parameters that the user has given
            # regardless of data type.
            "parameters": dict(),
        }
        DATATYPE_TO_DB["user"].append(new_user_profile)

        # write to the database
        with open('user_db.json', "w+") as user_db_file:
            json.dump(DATATYPE_TO_DB["user"], user_db_file, indent=4)

        result = new_user_profile

    # use deep copy to prevent unwanted update of DB file
    return copy.deepcopy(result)

def update_user_parameters(dialogflow_parameters, session, ignore_empty=True):
    """
    Update the stored parameters for the current user.

    Entity matches with empty results will be ignored. Every non-empty 
    parameter will overwrite what are in the database. Unless specified
    with option

    Return the updated user profile. Return None if nothing is updated since:
    1) everything given by the request is the same as what is in the DB
    2) no entity was matched for the current sentence said by the user
    """

    global DATATYPE_TO_DB

    # get the user profile and also make sure 
    # there exists a user profile to update
    user_profile = get_user_profile(session)

    # update non-empty parameters
    has_anything_new = False
    for entity_name in dialogflow_parameters:
        if (
            entity_name not in user_profile["parameters"]
            or (
                (not ignore_empty or len(dialogflow_parameters[entity_name].strip()) > 0)
                and dialogflow_parameters[entity_name] != user_profile["parameters"][entity_name]
            )
        ): 
            user_profile["parameters"][entity_name] = dialogflow_parameters[entity_name]
            has_anything_new = True

    # no need to update the databse if nothing is new
    if not has_anything_new:
        return None

    # search and update the document in database
    for index, document in enumerate(DATATYPE_TO_DB["user"]):
        if document["session"] == session:
            DATATYPE_TO_DB["user"][index] = user_profile
            break

    # rewrite the databse file
    with open('user_db.json', "w+") as user_db_file:
        json.dump(DATATYPE_TO_DB["user"], user_db_file, indent=4)

    return user_profile


def remove_user_data(session):
    """
    After the conversation ends, delete the stored profile
    for the current user.
    """

    # get the user profile
    user_profile = get_user_profile(session)

    DATATYPE_TO_DB["user"].remove(user_profile)

    # rewrite the db file
    with open('user_db.json', "w+") as user_db_file:
        json.dump(DATATYPE_TO_DB["user"], user_db_file, indent=4)
