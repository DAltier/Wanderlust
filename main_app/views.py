import bcrypt
from django.contrib import messages
from django.shortcuts import render, redirect, HttpResponse
from datetime import date, datetime, timedelta
import requests
import os

from .models import *

def index(request):
    if "uuid" in request.session:
        return redirect("/events")

    return render(request, "index.html")

def register_view(request):
    return render(request, "register.html")

def register(request):
    errors = Member.objects.registration_validator(request.POST)

    if len(errors) > 0:
        for key, value in errors.items():
            messages.error(request, value)

        return redirect("/register_view")
    else:
        hash_slinging_slasher = bcrypt.hashpw(request.POST['password'].encode(), bcrypt.gensalt()).decode()
        new_member = Member.objects.create(
            first_name = request.POST['first_name'],
            last_name = request.POST['last_name'],
            email = request.POST['email'],
            birth_date = request.POST['birth_date'],
            password = hash_slinging_slasher,
        )

        request.session['uuid'] = new_member.id

        return redirect("/events")

def register_event_view(request, id):
    request.session['event_id'] = id
    return redirect ('/register_view')

def login_view(request):
    if "uuid" in request.session:
        return redirect("/events")
    return render(request, "login.html")

def login(request):
    errors = Member.objects.login_validator(request.POST)

    if len(errors) > 0:
        for key, value in errors.items():
            messages.error(request, value)

        return redirect("/login_view")
    else:
        member = Member.objects.get(email = request.POST['email'])

        request.session['uuid'] = member.id

        return redirect("/events")

def login_event_view(request, id):
    request.session['event_id'] = id
    return redirect ('/login_view')

def logout(request):
    del request.session['uuid']
    request.session.clear()
    # del request.session['event_id']

    return redirect("/")

def events(request):
    if "uuid" not in request.session:
        return redirect("/")
    #if "event_id" in request.session:
        #return redirect(f"/events/{request.session['event_id']}")

    logged_in_member = Member.objects.get(id = request.session['uuid'])
    logged_in_member_events = Event.objects.all().filter(creator=logged_in_member).order_by("date", "time") | Event.objects.all().filter(members=logged_in_member).order_by("date", "time")
    all_other_events = Event.objects.all().exclude(creator = logged_in_member).exclude(members=logged_in_member).order_by("date", "time")

    # new list:
    logged_in_member_events_future = []
    all_other_events_future = []

    #filter out the those events that have passed
    today = datetime.now()
    for event in logged_in_member_events:
        if event.date > today.date():
            logged_in_member_events_future.append(event)
    
    for event in all_other_events:
        if event.date > today.date():
            all_other_events_future.append(event)

    context = {
        "logged_in_member": logged_in_member,
        # combine list of events created and joined by logged in member:
        "logged_in_member_events": logged_in_member_events_future,
        "all_members": Member.objects.all(),
        "all_other_events" : all_other_events_future,
    }

    return render(request, "events.html", context)

# ************************************** CRUD for Events

# for looping through all of the categories
all_categories = ['Hiking', 'Biking', 'Camping', 'Running', 'Rock Climbing', "Paddleboarding", 'Kayaking', 'Scuba Diving']

def new(request):
    context = {
        'member' : Member.objects.get(id = request.session['uuid'])
    }
    return render(request, "new_event.html", context)

def create(request, id):
    errors = Event.objects.event_validator(request.POST)

    if len(errors) > 0:
        for key, value in errors.items():
            messages.error(request, value)
        
        return redirect("/events/new")
    else:
        logged_in_member = Member.objects.get(id = request.session['uuid'])
        
        new_event = Event.objects.create(
            creator = logged_in_member,
            title = request.POST['title'],
            address = request.POST['address'],
            city = request.POST['city'],
            state = request.POST['state'],
            zipcode = request.POST['zipcode'],
            time = request.POST['time'],
            date = request.POST['date'],
            category = request.POST['category'],
            description = request.POST['description'],
            picture_id = request.POST['demo'],
        )
        return redirect("/events")

def show_event(request, id):
    # variables needed for the weather api
    this_event = Event.objects.get(id = id)
    zip_code = this_event.zipcode
    members_of_this_event = this_event.members.all()
    WEATHER_API_KEY = os.getenv('WEATHER_API_KEY')
    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')

    
    #variables needed for the geocoding_api:
    formatted_address = this_event.address.replace(" ","+")
    formatted_city = this_event.city.replace(" ","+")
    address = formatted_address + ",+" + formatted_city + ",+" + this_event.state # {address} needs to be in format: {1600+Amphitheatre+Parkway,+Mountain+View,+CA}

    # api calls for weather
    data_forecast = requests.get(f'http://api.openweathermap.org/data/2.5/forecast?zip={zip_code},us&appid={WEATHER_API_KEY}&units=imperial')
    data_today = requests.get(f'http://api.openweathermap.org/data/2.5/weather?zip={zip_code},us&appid={WEATHER_API_KEY}&units=imperial') 
    
    # api call for Geocoding (need to get long and lang)
        # from geocoding_api get the latitude and longitude
    geocoding_api = requests.get(f'https://maps.googleapis.com/maps/api/geocode/json?address={address}&key={GOOGLE_API_KEY}').json()
    print("Geocoding API", geocoding_api)
    latitude = geocoding_api['results'][0]['geometry']['location']['lat']
    longitude = geocoding_api['results'][0]['geometry']['location']['lng']

    # for weather forecast
    today = datetime.now()
    next_five_days = []
    sorted_weather_arr =[]
    count = 0

    # get the next five days
    base = date.today()
    for x in range(1, 5):
        next_five_days.append(str(base + timedelta(x)))

    api_data_forecast = data_forecast.json()
    print(api_data_forecast)
    for weather in api_data_forecast['list']:
        count = count + 1 
        if '00:00:00' in weather['dt_txt']: # find the next midnight data => next day
            break


    for day in range (0, 5):
        for index in range (count+2, count+6):  # use the count from above to append to sorted_weather_arr
            sorted_weather_arr.append(api_data_forecast['list'][index]['main']['temp'])
        count = count + 4

    
    context = {
        'logged_in_member' : Member.objects.get(id = request.session['uuid']),
        'this_event' : this_event,
        'count_of_members_of_this_event' : len(members_of_this_event),
        'api_weather_today' : data_today.json(),
        'coordinates' : {
            'lat' : latitude,
            'lng' : longitude,
        },
        'today' : today.date(),
        'next_five_days' : next_five_days,
        'api_data_forecast' : sorted_weather_arr,   # array of 25 temperatures at 5 times over 5 days
    }

    return render(request, "event_page.html", context)

def edit(request, id):
    this_event = Event.objects.get(id = id)
    print(this_event.time)
    context = {
        "this_event" : Event.objects.get(id = id),
        "all_categories" : all_categories,
    }
    return render(request, "edit_event.html", context)

def update(request, id):
    edited_event = Event.objects.get(id = id)
    edited_event.title = request.POST['title']
    edited_event.address = request.POST['address']
    edited_event.city = request.POST['city']
    edited_event.state = request.POST['state']
    edited_event.zipcode = request.POST['zipcode']
    edited_event.date = request.POST['date']
    edited_event.time = request.POST['time']
    edited_event.category = request.POST['category']
    edited_event.description = request.POST['description']
    edited_event.picture_id = request.POST['demo']
    edited_event.save()
    return redirect("/events")

def destroy(request, id):
    event_to_be_deleted = Event.objects.get(id = id)
    event_to_be_deleted.delete()
    return redirect("/events")

# ****************************************** pages for individual categories

def hiking(request):
  if "uuid" not in request.session:
    context = {
        "all_members": Member.objects.all(),
        "all_events" : Event.objects.filter(category="Hiking"),
    }
  else:
    logged_in_member = Member.objects.get(id = request.session['uuid'])
    context = {
      "logged_in_member": logged_in_member,
      "all_members": Member.objects.all(),
      "all_events" : Event.objects.filter(category="Hiking"),
      "all_other_events": Event.objects.all().exclude(creator = logged_in_member).exclude(members=logged_in_member).order_by("date", "time"),
    }
  return render(request, "all_hiking.html", context)

def biking(request):
  if "uuid" not in request.session:
    context = {
        "all_members": Member.objects.all(),
        "all_events" : Event.objects.filter(category="Biking"),
    }
  else:
    logged_in_member = Member.objects.get(id = request.session['uuid'])
    context = {
      "logged_in_member": logged_in_member,
      "all_members": Member.objects.all(),
      "all_events" : Event.objects.filter(category="Biking"),
      "all_other_events": Event.objects.all().exclude(creator = logged_in_member).exclude(members=logged_in_member).order_by("date", "time"),
    }
  return render(request, "all_biking.html", context)

def camping(request):
  if "uuid" not in request.session:
    context = {
        "all_members": Member.objects.all(),
        "all_events" : Event.objects.filter(category="Camping"),
    }
  else:
    logged_in_member = Member.objects.get(id = request.session['uuid'])
    context = {
      "logged_in_member": logged_in_member,
      "all_members": Member.objects.all(),
      "all_events" : Event.objects.filter(category="Camping"),
      "all_other_events": Event.objects.all().exclude(creator = logged_in_member).exclude(members=logged_in_member).order_by("date", "time"),
    }
  return render(request, "all_camping.html", context)

def running(request):
  if "uuid" not in request.session:
    context = {
        "all_members": Member.objects.all(),
        "all_events" : Event.objects.filter(category="Running"),
    }
  else:
    logged_in_member = Member.objects.get(id = request.session['uuid'])
    context = {
      "logged_in_member": logged_in_member,
      "all_members": Member.objects.all(),
      "all_events" : Event.objects.filter(category="Running"),
      "all_other_events": Event.objects.all().exclude(creator = logged_in_member).exclude(members=logged_in_member).order_by("date", "time"),
    }
  return render(request, "all_running.html", context)

def rock_climbing(request):
  if "uuid" not in request.session:
    context = {
        "all_members": Member.objects.all(),
        "all_events" : Event.objects.filter(category="Rock Climbing"),
    }
  else:
    logged_in_member = Member.objects.get(id = request.session['uuid'])
    context = {
      "logged_in_member": logged_in_member,
      "all_members": Member.objects.all(),
      "all_events" : Event.objects.filter(category="Rock Climbing"),
      "all_other_events": Event.objects.all().exclude(creator = logged_in_member).exclude(members=logged_in_member).order_by("date", "time"),
    }
  return render(request, "all_rock_climbing.html", context)

def paddleboarding(request):
  if "uuid" not in request.session:
    context = {
        "all_members": Member.objects.all(),
        "all_events" : Event.objects.filter(category="Paddleboarding"),
    }
  else:
    logged_in_member = Member.objects.get(id = request.session['uuid'])
    context = {
      "logged_in_member": logged_in_member,
      "all_members": Member.objects.all(),
      "all_events" : Event.objects.filter(category="Paddleboarding"),
      "all_other_events": Event.objects.all().exclude(creator = logged_in_member).exclude(members=logged_in_member).order_by("date", "time"),
    }
  return render(request, "all_paddleboarding.html", context)

def kayaking(request):
  if "uuid" not in request.session:
    context = {
        "all_members": Member.objects.all(),
        "all_events" : Event.objects.filter(category="Kayaking"),
    }
  else:
    logged_in_member = Member.objects.get(id = request.session['uuid'])
    context = {
      "logged_in_member": logged_in_member,
      "all_members": Member.objects.all(),
      "all_events" : Event.objects.filter(category="Kayaking"),
      "all_other_events": Event.objects.all().exclude(creator = logged_in_member).exclude(members=logged_in_member).order_by("date", "time"),
    }
  return render(request, "all_kayaking.html", context)

def scuba_diving(request):
  if "uuid" not in request.session:
    context = {
        "all_members": Member.objects.all(),
        "all_events" : Event.objects.filter(category="Scuba Diving"),
    }
  else:
    logged_in_member = Member.objects.get(id = request.session['uuid'])
    context = {
      "logged_in_member": logged_in_member,
      "all_members": Member.objects.all(),
      "all_events" : Event.objects.filter(category="Scuba Diving"),
      "all_other_events": Event.objects.all().exclude(creator = logged_in_member).exclude(members=logged_in_member).order_by("date", "time"),
    }
  return render(request, "all_scuba_diving.html", context)

#
def join(request, id):
    member = Member.objects.get(id = request.session['uuid'])
    event = Event.objects.get(id = id)
    member.events.add(event)
    event.members.add(member)
    return redirect("/events")

def cancel(request, id):
    member = Member.objects.get(id = request.session['uuid'])
    event = Event.objects.get(id = id)
    member.events.remove(event)
    return redirect("/events")

# API!!!
def weather(request):
    data = requests.get('http://api.openweathermap.org/data/2.5/forecast?zip=93111,us&appid=49e20116f7a2742952b883c75a1ec1ab&units=imperial')
    print(data['list']['main'])
    # data = requests.get(f'http://api.openweathermap.org/data/2.5/weather?zip={zip_code},us&appid=8fd981d465951e4cedaf6b0c75187037&units=imperial')
    return HttpResponse(data)