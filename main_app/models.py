from django.db import models
import bcrypt
from datetime import datetime, date
import re

class MemberManager(models.Manager):
  def registration_validator(self, post_data):
    errors = {}

    if len(post_data['first_name']) < 2:
      errors['first_name'] = "First name must be at least 2 characters."
    if len(post_data['last_name']) < 2:
      errors['last_name'] = "Last name must be at least 2 characters."


    # Validate birthday data
    today = date.today()
    if len(post_data['birth_date']) < 1:
      errors['birth_date'] = "Your birthday should be a valid date."
    else:
      if datetime.strptime(post_data['birth_date'], '%Y-%m-%d') > datetime.today():
        errors['birth_date'] = "Your birthday should be in the past"
      else :
        age = today.year - datetime.strptime(post_data['birth_date'], '%Y-%m-%d').year - ((today.month, today.day) < (datetime.strptime(post_data['birth_date'], '%Y-%m-%d').month,datetime.strptime(post_data['birth_date'], '%Y-%m-%d').day))
        if age < 18:
          errors['birth_date'] = "You should be at least 18 years old"

    # validate the email:
    EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
    if not EMAIL_REGEX.match(post_data['email']):    # test whether a field matches the pattern
      errors['email'] = "Invalid email address!"

    # make sure email is unique
      # filter returns an array
    email = Member.objects.filter(email = post_data['email'])
    if len(email) > 1:
      errors['unique_email'] = "This email is already taken"

    # validate the password:
    if len(post_data['password']) < 8:
      errors['password'] = "Password must be at least 8 characters"
    #  validate the confirm_password:
    if post_data['password'] != post_data['confirm_password']:
      errors['confirm_password'] = "Password and confirm password must match"

    return errors
    
  # this one compares (with less info from user)
  # every function should just do one thing, so this second one is necessary
  def login_validator(self, post_data):
    errors = {}

    user_list = Member.objects.filter(email = post_data['email'])
    if len(user_list) > 0:
      user = user_list[0]
      if not bcrypt.checkpw(post_data['password'].encode(), user.password.encode()):
        errors['password'] = "Invalid Credentials"
    else:
      errors['email'] = "Invalid Credentials"

    return errors


class Member(models.Model):
  first_name = models.CharField(max_length = 255)
  last_name = models.CharField(max_length = 255)
  birth_date = models.CharField(max_length = 255)
  email = models.CharField(max_length = 255)
  password = models.CharField(max_length = 255)
  created_at = models.DateTimeField(auto_now_add = True)
  updated_at = models.DateTimeField(auto_now = True)
  objects = MemberManager()
  # event_created
  # events

class EventManager(models.Manager):
  def event_validator(self, post_data):
    errors = {}

    # validate the title
    if len(post_data['title']) < 3:
      errors['title'] = "Title must be at least 3 characters."
    
    # validate the address
    if post_data['address'] == "" :
      errors['address'] = "Address cannot be empty."
    # elif :
    #     errors['address'] = "Address must be in the correct format."
    
    # validate the city
    if post_data['city'] == "" :
      errors['city'] = "City cannot be empty."
    elif len(post_data['city']) < 3 :
      errors['city'] = "City must be at least 3 letters."
    
    # validate the state
    if post_data['state'] == "" :
      errors['state'] = "State cannot be empty."
    elif len(post_data['state']) != 2:
      errors['state'] = "State must be 2 letters."
    
    # validate the zipcode
    if post_data['zipcode'] == "" :
      errors['zipcode'] = "Zipcode cannot be empty."
    elif len(post_data['zipcode']) != 5:
      errors['zipcode'] = "Zipcode must be 5 digits."
    
    # validate the date:
    input_date = post_data['date']
    print(input_date)
    if (input_date != ""): # some date is inputted
      future_date = datetime.strptime(input_date, "%Y-%m-%d") # converts string to a date
      today = datetime.now()
      if future_date.date() < today.date():
        errors['date'] = "Date must be in the future."
    else:
      errors['date'] = "Date cannot be empty."
    
    # no need to validate time. can be anytime, but must enter a time.
    if (post_data['time'] == ""):
      errors['time'] = "Time cannot be empty."
    
    # validate the description
    if len(post_data['description']) < 3:
      errors['description'] = "Description must be at least 3 characters."
    
    # validate the category
    if (post_data['category'] == "0"):
      errors['category'] = "Must choose a category for the event."

    return errors


class Event(models.Model):
  creator = models.ForeignKey(Member, related_name = "event_created", on_delete = models.CASCADE)
  members = models.ManyToManyField(Member, related_name = "events")
  title = models.CharField(max_length = 255)
  address = models.CharField(max_length = 255)
  city = models.CharField(max_length = 255)
  state = models.CharField(max_length = 255)
  zipcode = models.CharField(max_length = 255)
  time = models.TimeField()
  date = models.DateField()
  category = models.CharField(max_length = 255)
  description = models.TextField()
  picture_id = models.CharField(max_length=255)
  created_at = models.DateTimeField(auto_now_add = True)
  updated_at = models.DateTimeField(auto_now = True)
  objects = EventManager()
