**Multi-user Blog**
=======
#### Live version: sh-

Barebones blogging platform with open user registration.

#### To run:

* Authentication requires a file in the root directory named `secrets.py` with the following format:

* ```
	class Secret():
		local_auth_secret = "string"
		cookie_secret = "string"
```
---
####
This app is powered by Google App Engine. This project is a component of the [Udacity](http://www.udacity.com/) Full Stack Web Development Nanodegree.