<div align="center">

<samp>

<h1> COMS 4111: Project 1 - Tennis Tournament Management System</h1>

<h3> Adithya K Krishna: akk2188 <br> Rohit V Gopalakrishnan: rvg2119 </h3>
</samp>   

</div>     



## Database
Our database is stored in postgresql, you can access it with the URI mentioned below
XXX: The URI should be in the format of:

    postgresql://USER:PASSWORD@34.75.94.195/proj1part2

For USER and PASSWORD credentials contact us.


## Directory setup
<!---------------------------------------------------------------------------------------------------------------->
The structure of the repository is as follows: 

- `static/`: Contains the css file used to style the front end.
- `templates/`: Contains html code for common pages like home, layout, player and admin .
- `templates/adminPrivileges`: Contains admin specific pages, features accessible only to admin, such as creating tournament, banning a player, etc.
- `templates/playerPrivileges`: Contains player specific pages, features accessible to player, such as registering for a tournament, 
                                updating information.

---

## Dependencies
- Python 3.7
- Flask
- SQLAlchemy (To generates SQL statements)
- Psycopg2 (databased driver, sends SQL statements to the database. SQLAlchemy depends on psycopg2 to communicate with the database)


To see the Web front end version:
```bash
python server.py
```

Open the code in edit mode
```bash
python server.py --debug 
```

### Running and debugging
```bash
python server.py --help 
```
To see the arguments taken by server.py
Arguments

- debug: To start the server in edit mode (default: False)
- HOST: The server is accesible only from the machine on which its executed, to avoid other users of the application from executing  
        arbitary code on the host system. If the debugger is disabled or trust the users on the network, we can make the server publicly available simply by setting  HOST to 0.0.0.0. This tells your operating system to listen on all public IPs. (default: 0.0.0.0)
- PORT: The port onto which we want to deploy our webpage(default: 8111)

## Contact

For any queries, please contact or [Adithya K Krishna](mailto:adithya.krishnakumar@gmail.com) or [Rohit V Gopalakrishnan](mailto:rohitvg27@gmail.com)
