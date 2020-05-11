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
attraction_db_file = open('app/attraction_db.json')

# create user db if it does not exist
if not os.path.isfile('app/user_db.json'):
    with open('app/user_db.json', "w+") as user_db_file:
        json.dump([], user_db_file, indent=4)
user_db_file = open('app/user_db.json')

ATTRACTION_DB = json.load(attraction_db_file)
USER_DB = json.load(user_db_file)

attraction_db_file.close()
user_db_file.close()

# build dict for more structured logic
DATATYPE_TO_DB = {
    "attraction": ATTRACTION_DB,
    "user": USER_DB
}



def update_the_order_in_results(results, session, chose_index):
    global DATATYPE_TO_DB

    # length of user_results > 1
    tmp = results.pop(chose_index) 
    results.insert(0, tmp)

    # get the user profile 
    user_profile = get_user_profile(session)

    # update profile
    user_profile["results"]["attraction"] = results

    # search and update the database
    for index, document in enumerate(DATATYPE_TO_DB["user"]):
        if document["session"] == session:
            DATATYPE_TO_DB["user"][index] = user_profile

    # rewrite the db file with new results
    with open('app/user_db.json', "w+") as user_db_file:
        json.dump(DATATYPE_TO_DB["user"], user_db_file, indent=4)

    return results


def search_it_from_results(parameters, data_type, session):
    """
    Choose the first result if there is any.
    """

    user_results = get_user_profile(session)["results"][data_type]
    if not user_results:
        return None
    return [user_results[0]]

def search_name_from_results(parameters, data_type, session):
    """
    Use the parameters to find matching documents by name in user's database.
    """

    global DATATYPE_TO_DB

    # results = []

    # get the user results and also make sure 
    # there exists a user profile to update
    user_results = get_user_profile(session)["results"][data_type]

    if not user_results:
        return None

    # if len(user_results) == 1:
    #     return user_results

    chose_index = -1

    for document in user_results:
        chose_index += 1
        if document['name'] == parameters['name']:
            # results.append(document)
            break
            
    # force it to check the whole corpus
    if chose_index == -1:
        return None

    tmp = user_results.pop(chose_index) 
    user_results.insert(0, tmp)

    # get the user profile 
    user_profile = get_user_profile(session)

    # update profile
    user_profile["results"]["attraction"] = user_results

    # search and update the database
    for index, document in enumerate(DATATYPE_TO_DB["user"]):
        if document["session"] == session:
            DATATYPE_TO_DB["user"][index] = user_profile

    # rewrite the db file with new results
    with open('app/user_db.json', "w+") as user_db_file:
        json.dump(DATATYPE_TO_DB["user"], user_db_file, indent=4)

    return user_results

def search_name_from_database(parameters, data_type, session):
    """
    Use the parameters to find matching documents by namee in database.
    """

    global DATATYPE_TO_DB

    results = []
    if not 'name' in parameters:
        return None
    entity_name = parameters['name']
    for document in DATATYPE_TO_DB[data_type]:
        if document['name'] == entity_name:
            results.append(document)
            break

    user_profile = get_user_profile(session)
    user_profile["results"][data_type] = results if len(results) > 0 else None
    user_profile["parameters"]["name"] = entity_name
    # search and update the database
    for index, document in enumerate(DATATYPE_TO_DB["user"]):
        if document["session"] == session:
            DATATYPE_TO_DB["user"][index] = user_profile

    # rewrite the db file with new results
    with open('app/user_db.json', "w+") as user_db_file:
        json.dump(DATATYPE_TO_DB["user"], user_db_file, indent=4)

    return results

def search(parameters, data_type):
    """
    Use the parameters to find matching documents. 

    Please make sure that the keys in parameters have the same name
    in the database. Entity names are DIFFERENT from databse field names.

    Also, parameters with empty values will be IGNORED.

    Just remember, process the parameters given by Dialogflow before passing
    it to this search method.
    """

    global DATATYPE_TO_DB

    results = []

    # delete empty parameters
    non_empty_parameters = dict()
    for field in parameters:
        if len(parameters[field].strip()) > 0:
            non_empty_parameters[field] = parameters[field]

    for document in DATATYPE_TO_DB[data_type]:
        # skip if any parameter does not match
        is_not_a_match = False
        for field in non_empty_parameters:
            if document[field] != non_empty_parameters[field]:
                is_not_a_match = True
                break

        if is_not_a_match:
            continue
        
        results.append(document)

    return results

def search_from_results(parameters, data_type, session):
    """
    Use the parameters to search within the matched results of a user.
    
    Please make sure that the keys in parameters have the same name
    in the database. Entity names are DIFFERENT from databse field names.

    Also, parameters with empty values will be IGNORED.

    Just remember, process the parameters given by Dialogflow before passing
    it to this search method.
    """

    global DATATYPE_TO_DB

    results = []

    # get the user results and also make sure 
    # there exists a user profile to update
    user_results = get_user_profile(session)["results"][data_type]

    # delete empty parameters
    non_empty_parameters = dict()
    for field in parameters:
        if len(parameters[field].strip()) > 0:
            non_empty_parameters[field] = parameters[field]

    for document in user_results:
        # skip if any parameter does not match
        is_not_a_match = False
        for field in non_empty_parameters:
            if document[field] != non_empty_parameters[field]:
                is_not_a_match = True
                break

        if is_not_a_match:
            continue
        
        results.append(document)

    return results

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
        with open('app/user_db.json', "w+") as user_db_file:
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
    # print('user_profile',user_profile)
    # update non-empty parameters
    has_anything_new = False
    for entity_name in dialogflow_parameters:
        # print('entity_name', entity_name)
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
    with open('app/user_db.json', "w+") as user_db_file:
        json.dump(DATATYPE_TO_DB["user"], user_db_file, indent=4)

    return user_profile

def update_search_results_for_user(results, data_type, session):
    """
    Update matched results for the specified user.

    results is a list of documents from the database.
    (i.e. what's returned from search() method in this file)

    data_type is one of the following:
    1) "attraction"


    Return True if succeed. Return False sinece:
    1) nothing is updated
    """

    global DATATYPE_TO_DB

    # get the user profile and also make sure 
    # there exists a user profile to update
    user_profile = get_user_profile(session)

    # no need to update anything if nothing is changed
    if (
        user_profile["results"][data_type] is not None
        and user_profile["results"][data_type] == results
    ):
        return None
    # print('update')
    # update profile
    user_profile["results"][data_type] = results if len(results) > 0 else None

    # search and update the database
    for index, document in enumerate(DATATYPE_TO_DB["user"]):
        if document["session"] == session:
            DATATYPE_TO_DB["user"][index] = user_profile

    # rewrite the db file with new results
    with open('app/user_db.json', "w+") as user_db_file:
        json.dump(DATATYPE_TO_DB["user"], user_db_file, indent=4)

def remove_user_data(session):
    """
    After the conversation ends, delete the stored profile
    for the current user.
    """

    # get the user profile
    user_profile = get_user_profile(session)

    DATATYPE_TO_DB["user"].remove(user_profile)

    # rewrite the db file
    with open('app/user_db.json', "w+") as user_db_file:
        json.dump(DATATYPE_TO_DB["user"], user_db_file, indent=4)
