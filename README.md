# E-JUST Wathcing Premier League
#### Video Demo:  <URL https://youtu.be/28U4U3ml6S4>
#### Description:
Since last year, the number of students has been increasing, and there is only one place to watch the Premier League for free. This place has become extremely crowded as it can only accommodate 50 people, and too many people were fighting for these spots. These incidents occurred when I was taking CS50x. At that time, I thought about creating a webpage to manage such a situation.
#### Features 
1- Account Creation and Authentication:
* Users can create an account with their name and university ID. The ID is validated using regular expressions to ensure it conforms to the university's format, preventing the creation of duplicate accounts
* Users choose their favorite team during account creation.
* Passwords are hashed and salted using bcrypt before storing them in the database. 
  
2-Login:
* Users can log in with their ID and password. Password verification is handled by the verify_password function.

3- Match Registration:
* Users can register for the matches of their favorite team. There are only 50 spots available, so it operates on a first-come, first-served basis.
* Users can view how many people are registered for the current week's matches.

4-Viewing Current Week's Matches:
* Users can see the matches scheduled for the current week and the number of registered users for each match. This helps them gauge the availability of spots before registering.

5-Database Structure:

Three tables: users, games, and registers.
* users table: Contains id, username, team, and password.
* games table: Stores date, time, home_team, away_team, and game_id.
* registers table: Tracks user registrations with foreign keys user_id and game_id.

[GIF Demo](Animation.gif)