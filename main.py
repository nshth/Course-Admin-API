import contextlib
from fastapi import FastAPI, HTTPException, Query
from pymongo import MongoClient
from bson import ObjectId
from fastapi.encoders import jsonable_encoder

app = FastAPI()
client = MongoClient("mongodb://localhost:27017/")
db = client['course-db']
courses = db['courses']


@app.get('/courses')
def get_course(sort_by: str = 'date', domain: str = None):
    # set the rating.total and rating.count to all the courses based on the sum of the chapters rating
    for course in courses.find():
        total = 0
        count = 0
        for chapter in course['chapters']:
            with contextlib.suppress(KeyError):
                total += chapter['rating']['total']
                count += chapter['rating']['count']
        courses.update_one({'_id': course['_id']}, {'$set': {'rating': {'total':total, 'count':count}}})

    # sort_by == 'date' [DESCENDING]
    if sort_by == 'date':
        sort_field = 'date'
        direction = -1
    # sort_by == 'rating' [DESCENDING]
    if sort_by == 'rating':
        sort_field = 'rating'
        direction = -1
# sort_by == 'alphabetical' [ASCENDING]
    if sort_by == 'alphabetical':
        sort_field = 'name'
        direction = 1
# set query
    query = {}
    if domain:
        query['domain'] = domain
# queries the MongoDB database to retrieve the relevant course information
    course = courses.find(query, {'chapters': 0, '_id': 0}).sort(sort_field, direction)
# return the courses in a list
    return list(courses)
