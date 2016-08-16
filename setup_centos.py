# Below commands are specific to Centos platform

CELERY_C_FORCE_COMMAND = "export C_FORCE_ROOT='true'"

CMD_LIST_SYSTEM_DEP_CENTOS = (
 #   ("Install Python 2.7 (may take a while)",
 #    "yum install python2.7"),
 #   ("Install Python dev (may take a while)",
 #    "yum install python-dev"),
 #   ("Install Python libpq dev (may take a while)",
 #    "yum install libpq-dev"),
    ("Install Python pip (may take a while, ignore if errors)",
     'curl "https://bootstrap.pypa.io/get-pip.py" -o "get-pip.py";python get-pip.py'),
    ("Install Postgresql and dependencies(may take a while)",
     "yum -y localinstall http://yum.postgresql.org/9.3/redhat/rhel-6-x86_64/pgdg-centos93-9.3-1.noarch.rpm",),
    ("postgres-",
     "yum -y install postgresql93-server postgresql93-contrib",),
    ("setup initdb-",
      "/usr/pgsql-9.3/bin/postgresql93-setup initdb",),
    ("start postgres-",
     "systemctl start postgresql-9.3",),
    ("enable postgres-",
     "systemctl enable postgresql-9.3",),
    ("Install mod_wsgi-",
     "yum -y install mod_wsgi",),
    ("Install RabbitMQ and dependencies(may take a while, ignore errors)",
     "yum -y install wget;wget https://packages.erlang-solutions.com/erlang-solutions-1.0-1.noarch.rpm",),
    ("rpm for erlang(ignore errors)",
      "rpm -Uvh erlang-solutions-1.0-1.noarch.rpm",),
    ("erlang(ignore errors)",
      "yum -y install erlang",),
    ("esl-erlang(ignore errors)",
      "yum -y install esl-erlang",),
    ("rpm for rabbitmq-server",
     "rpm --import http://www.rabbitmq.com/rabbitmq-signing-key-public.asc",),
    ("rabbitmq-server",
     "rpm -Uvh http://www.rabbitmq.com/releases/rabbitmq-server/v3.6.0/rabbitmq-server-3.6.0-1.noarch.rpm",),
    ("rabbitmq init script",
     "chkconfig rabbitmq-server on",),
    ("start rabbitmq",
     "/etc/init.d/rabbitmq-server start",),
)

RABBITMQ_SERVER_RESTART_CENTOS = "/etc/init.d/rabbitmq-server restart"


REQUIREMTENS_CENTOS = (
                  ("Installing pip(ignore errors)",
                    'curl "https://bootstrap.pypa.io/get-pip.py" -o "get-pip.py";python get-pip.py',),
                  ("Installing dependency for pycrypto devel",
                    "yum -y install python-devel"),
                  ("Installing dependency for pycrypto development tools(may take a while)",
                    'yum -y groupinstall "Development tools"'),
                  ("Installing psycopg2 dependency)",
                    'yum -y install postgresql-devel'),
                      )
                       

YUM_UPDATE = (
              ("Updating yum(ignore if errors)",
               "yum -y update"),
             )
