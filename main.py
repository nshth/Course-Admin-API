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
    for course in courses['courses']:
        total = 0
        count = 0
        for chapter in course['chapters']:
            with contextlib.suppress(KeyError):
                total += chapter['rating']['total']
                count += total + chapter['rating']['count']
        courses.update_one({'_id': course['_id']}, {'$set': {'rating': {'total':total, 'count':count}}})
