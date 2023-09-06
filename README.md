## Database installation

To create the database, run `flask db upgrade` (needs `Flask-Migrate` to be installed).

## Email server
export MAIL_SERVER=localhost
export MAIL_PORT=8025
python -m smtpd -n -c DebuggingServer localhost:8025