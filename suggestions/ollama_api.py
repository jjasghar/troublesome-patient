import csv
import ollama
import os
import random
import logging
from faker import Faker
from ollama import Client

class Patient:
    def __init__(self, age, level, intensity, name, job, spirits):
        self.age = age
        self.level = level
        self.intensity = intensity
        self.name = name
        self.job = job
        self.spirits = spirits

fake = Faker()
model_name = 'granite3.2:latest'
csv_file = "profiles/adult_patient_profiles.csv"
ollama_host = os.environ.get('OLLAMA_SELF_HOST', '127.0.0.1')

def read_csv(csv_file):
    with open(csv_file, "r") as f:
        data = csv.DictReader(f)
        data_list = []
        for row in data:
            data_list.append(row)
    return data_list

data_list = read_csv(csv_file)
individuals = random.choices(data_list,k=4)

def create_json_content(patient):
        messages = [
{"role": "user", "content": f"""
You are a patient designed for a doctor to practice Motivation Interviewing based off of the following individuals:

{individuals}

"""
},
{"role": "system", "content": f"""
You're name is {patient.name} and are {patient.age} and a professional
 {patient.job} but has some type of {patient.level} health issue, that is inspired from these previous individuals. You
 want to be {patient.intensity} level of attitude to get help and you seem in
 {patient.spirits} level of happiness. Only describe the name and general information about the
 individual you create, you're job is to work with the person asking the
 questions to have them figure out how to have them make healthy choices.
 You {random.choice(["never","sometimes","always"])} want to be addressed with
 your name or nickname, not something completely different.
"""
},
]
        return messages

def create_patient():
    age = random.randrange(21,60)
    level = random.choice(["minor","major","critical"])
    intensity = random.choice(["low","medium","high"])
    name = fake.name()
    job = fake.job()
    spirits = random.choice(["low","medium","high"])

    patient = Patient(age,level, intensity, name, job, spirits)
    return patient

def create_messages(patient):
    messages = create_json_content(patient)
    return messages

def generate_response(user_input, messages, patient):
    logging.basicConfig(
        level=logging.CRITICAL,
        format="%(asctime)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        filename=f"previous_chats/{patient.name}-{patient.age}-{patient.job}.log",
    )
    client = Client(
          host=f'http://{ollama_host}:11434',
    )
    response = client.chat(model=model_name, messages=messages)
    messages.append({"role": "user", "content": user_input})
    logging.critical(f"Me: {user_input}")
    response = client.chat(model=model_name, messages=messages)
    answer = response.message.content
    messages.append({"role": "assistant", "content": answer})
    output_dict = {"content": answer,
                   "name": patient.name,
                   "age": patient.age,
                   "job": patient.job,
                   "spirits": patient.spirits,
                   "help": patient.intensity
                  }
    logging.critical(f"{patient.name}: {answer}")
    return output_dict
