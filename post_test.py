import requests

# URL вашого FastAPI додатку
url = "http://127.0.0.1:8080/contacts/"

# Дані для нового контакту
new_contact_data = {
    "first_name": "John",
    "last_name": "Doe",
    "email": "john.doe@example.com",
    "phone_number": "123456789",
    "birthday": "1990-01-01",
    "additional_info": "Some additional info"
}

# Виконання HTTP-запиту POST
response = requests.post(url, json=new_contact_data)

# Перевірка статус-коду відповіді
if response.status_code == 200:
    print("Contact created successfully!")
    print("Response:", response.json())
else:
    print("Failed to create contact.")
    print("Status code:", response.status_code)
    print("Response:", response.text)
