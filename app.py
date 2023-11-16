from fastapi import FastAPI, Form, Request
from fastapi.responses import JSONResponse
from tinydb import TinyDB, Query
import re
from datetime import datetime
app = FastAPI()
db = TinyDB('database.json')

# Example test database
templates = [
    {
        "name": "MyForm",
        "user_name": "text",
        "order_date": "date"
    },
    {
        "name": "OrderForm",
        "user_name": "text",
        "lead_email": "email",
        "number": "phone",
    }
]

db.insert_multiple(templates)

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

def get_template_matching_fields(input_fields):
    for template in db:
        template_fields = template.copy()
        template_name = template_fields.pop('name')

        if all(field_name in input_fields and
               input_fields[field_name] and
               (field_type := template_fields.get(field_name)) and
               (field_type == 'date' and validate_date(input_fields[field_name]) or
                field_type == 'phone' and validate_phone(input_fields[field_name]) or
                field_type == 'email' and validate_email(input_fields[field_name]) or
                field_type == 'text')
               for field_name in template_fields):
            return template_name

        typed_fields = {field_name: 'date' if validate_date(value) else
                                  'phone' if validate_phone(value) else
                                  'email' if validate_email(value) else
                                  'text'
                    for field_name, value in input_fields.items()}

    # for field_name in input_fields:
    #     fieled_type = template_fields.get(field_name)
    #     if fieled_type == 'date' and validate_date(input_fields[field_name])
        

    return typed_fields

@app.post("/get_form")
async def get_form(request: Request):
    print(dict(request.query_params))
    print(type(request.query_params))
    result = get_template_matching_fields(dict(request.query_params))

    if isinstance(result, dict):
        return result
    else:
        return JSONResponse(content=result)
