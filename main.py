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
    # returns an iterator
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
    courses_cursor = courses.find(query, {'chapters': 0, '_id': 0}).sort(sort_field, direction)
# return the courses in a list not iterator
    return list(courses_cursor)

@app.get('/courses/{course_id}')
def get_course_by_id(course_id: str):
    course = courses.find_one({'_id': ObjectId(course_id)}, {'_id':0, 'chapters': 0})
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    try:
        course['rating'] = course['rating']['total']
    except (KeyError, TypeError):
        course['rating'] = "Not rated yet"
    return course

# Get Specific Chapter Information Endpoint
@app.get('/courses/{course_id}/{chapter_in}')
def get_chapter_by_id(course_id: str, chapter_in: str, rating:int):
    course = courses.find_one({'_id': ObjectId(course_id)}, {'_id':0})
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    chapters = course.get('chapters', [])
    try:
        chapter = chapters[int(chapter_in)]
    except (KeyError, IndexError, ValueError) as e:
        raise HTTPException(status_code=404, detail="chapter not exist") from e
    return chapter


@app.post('/courses/{course_id}/{chapter_in}')
def rate_chapter(course_id: str, chapter_in: str, rating:int = Query(...,gt=-2, lt=5)):
    course = courses.find_one({'_id': ObjectId(course_id)}, {'_id':0})
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    chapters = course.get('chapters', [])
    try:
        chapter = chapters[int(chapter_in)]
    except (KeyError, IndexError, ValueError) as e:
        raise HTTPException(status_code=404, detail="chapter not exist") from e
    try:
        chapter['rating']['total'] += rating
        chapter['rating']['count'] += 1
    except:
        chapter['rating'] = {'total': rating, 'count': 1}
    
    courses.update_one({'_id': ObjectId(course_id)}, {'$set': {'chapters': chapters}})
    return chapter




