### WanderLust

WanderLust is a web app where users can create outdoor events.
It is a Full Stack Web Application developed using Python, Django, and MySQL.
 
Home page:

<img src="https://github.com/DAltier/Wanderlust/blob/main/images/home.png" width="800">

The user can select a category of activities to see the existing events. 
A user who is not logged in will not be able to join an event or have access to details regarding the events.

<img src="https://github.com/DAltier/Wanderlust/blob/main/images/not_logged_in.png" width="800">

Registration form using validations and bcrypt for password security:

<img src="https://github.com/DAltier/Wanderlust/blob/main/images/registration.png" width="800">

Login form using validations and bcrypt for password security:

<img src="https://github.com/DAltier/Wanderlust/blob/main/images/login.png" width="800">

Once logged in, the user is directed to the dashboard, where all future events are displayed. 
The top table shows all the events that the current user has created or joined. 
The bottom table shows all the other events that the current user can join. 

<img src="https://github.com/DAltier/Wanderlust/blob/main/images/dashboard.png" width="800">

The logged in user is able to create new events, and can use the drag-and-drop feature to associate any of the images in the gallery with their event.

<img src="https://github.com/DAltier/Wanderlust/blob/main/images/new_event.png" width="800">

They have the option of editing or deleting any of the events they have created, as well as cancelling any events that they've joined.
They also have the option of joining any event created by another user.

<img src="https://github.com/DAltier/Wanderlust/blob/main/images/join.png" width="800">

If the logged in user selects an event category, they will have the access to a detailed view of any of the events, as well as the actions available on the dashboard.

<img src="https://github.com/DAltier/Wanderlust/blob/main/images/logged_in_view.png" width="800">

When selecting a specific event, the current user will have acces to all the information regarding that event, including the number of people who joined the event, 
the weather forecast at that address for the current date and the next four day, as well as a map pinpointing the event's location.

<img src="https://github.com/DAltier/Wanderlust/blob/main/images/event_page.png" width="800">
