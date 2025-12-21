# Listen on all interfaces, port 8000
bind = "0.0.0.0:8083"
# bind = "localhost:8083"

# Sync worker is fine for Bottle / classic WSGI
worker_class = "gthread"
threads = 4
workers = 1

# Auto-reload on code changes (great for development, turn off in prod)
reload = True

# Logging
loglevel = "debug"
accesslog = "-"   
errorlog = "-"
access_log_format = '%(h)s %({Host}i)s "%(r)s" %(s)s %({Referer}i)s "%(a)s"'