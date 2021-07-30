from django.urls import path
from . import views

urlpatterns = [
    path('', views.index),
    # register routes used if signing in from root route
    path('register_view', views.register_view),
    path('register', views.register),
    # register routes used if signing in from a specific event page
    path('register_event_view/<int:id>', views.register_event_view),
    # login routes used if logging in from root route
    path('login_view', views.login_view),
    path('login', views.login),
    # login routes used if logging in from a specific event page
    path('login_event_view/<int:id>', views.login_event_view),
    path('logout', views.logout),
    # once logged in (CRUD):
    path('events/new', views.new), # Create
    path('events/create/<int:id>', views.create), # Create
    path('events/<int:id>', views.show_event), # Read one
    path('events', views.events), # Read all
    path('events/<int:id>/edit', views.edit), # Update
    path('events/<int:id>/update', views.update),  # Update
    path('events/<int:id>/destroy', views.destroy), # Delete
    # all events by category:
    path('events/hiking', views.hiking),
    path('events/biking', views.biking),
    path('events/camping', views.camping),
    path('events/running', views.running),
    path('events/rock_climbing', views.rock_climbing),
    path('events/paddleboarding', views.paddleboarding),
    path('events/kayaking', views.kayaking),
    path('events/scuba_diving', views.scuba_diving),
    #
    path('events/join/<int:id>', views.join),
    path('events/cancel/<int:id>', views.cancel),
    path('weather', views.weather), # just to see that it works (this is HttpResponse)
]