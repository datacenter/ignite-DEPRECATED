# Below commands are specific to Ubuntu platform

CMD_LIST_SYSTEM_DEP_UBUNTU = (
    ("Install Python 2.7 (may take a while)",
     "apt-get install python2.7"),
    ("Install Python dev (may take a while)",
     "apt-get install python-dev"),
    ("Install Python libpq dev (may take a while)",
     "apt-get install libpq-dev"),
    ("Install Python pip (may take a while)",
     "apt-get install python-pip"),
    ("Install Postgresql(may take a while)",
     "apt-get install postgresql-9.3 postgresql-common"),
    ("Install mod_wsgi (may take a while)",
     "apt-get install libapache2-mod-wsgi"),
    ("Install RabbitMQ (may take a while)",
     "apt-get install rabbitmq-server"),
)

PSYCOPG2 = "psycopg2==2.6"

RABBITMQ_SERVER_RESTART_UBUNTU = "service rabbitmq-server restart"
