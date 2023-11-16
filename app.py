from fastapi import FastAPI, Form, Request
from fastapi.responses import JSONResponse
import re
from datetime import datetime
app = FastAPI()
import pymongo
client = pymongo.MongoClient("mongodb://mongo:27017/")
db = client["mydatabase"]
collection = db["mycollection"]

# Example test database
templates = [
    {
        "name": "MyForm",
        "user_name": "text",
        "order_date": "date"
    },
    {
        "name": "OrderForm",
        "lead_email": "email",
        "number": "phone",
    }
]
collection.insert_many(templates)
# db.insert_multiple(templates)

def validate_date(value):
    date_formats = ['%Y-%m-%d', '%d.%m.%Y']

    for date_format in date_formats:
        try:
            # Пытаемся преобразовать строку в объект datetime
            datetime.strptime(value, date_format)
            return True
        except ValueError:
            # Если возникает ошибка, пробуем следующий формат
            pass

    # Если ни один из форматов не подходит
    return False

def validate_phone(value):
    result = re.match(r'^(\+7|7|8)?[\s\-]?\(?[489][0-9]{2}\)?[\s\-]?[0-9]{3}[\s\-]?[0-9]{2}[\s\-]?[0-9]{2}$', value)
    return bool(result)

def validate_email(value):
    return bool(re.match(r'(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)', value))

def validate_fields(data):
    if validate_date(data):
        return 'data'
    if validate_phone(data):
        return 'phone'
    if validate_email(data):
        return 'email'
    return 'text'

def get_template_matching_fields(input_fields):
    set1 = set(input_fields.keys())
    db = collection.find()
    for template in db:
        template_fields = template.copy()
        template_name = template_fields.pop('name')
        tmp = template_fields.pop('_id')
        print(template_name)
        set2 = set(template_fields.keys())
        print(set2)
        res = False
        if set2.issubset(set1):
            for elem in set1:
                if template_fields[elem] == 'phone':
                    print("PHONE")
                    res = validate_phone(input_fields[elem])
                if template_fields[elem] == 'date':
                    print("DATE")
                    res = validate_date(input_fields[elem])
                if template_fields[elem] == 'email':
                    print("EMAIL")
                    res = validate_email(input_fields[elem])
                if res == False:
                    break
            if res:
                return template_name
    resp = {}
    for elem in set1:
        resp[elem] = validate_fields(input_fields[elem])
    return resp


@app.post("/get_form")
async def get_form(request: Request):
    result = get_template_matching_fields(dict(request.query_params))

    if isinstance(result, dict):
        return result
    else:
        return JSONResponse(content=result)
