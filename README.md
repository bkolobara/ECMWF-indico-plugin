This Indico plugin provides a set of features specific to the ECMWF (European
Centre for Medium-Range Weather Forecasts).

Features:

- Generation of HTML Abstract pages in the ECMWF format.
- Linkifying text inside the registration forms.
- Adding Google analytics js.
- Notifying contacts for registrations.
- Sending out email Visa invitation.
- Sending out email invited speaker reimbursements.
- Adding custom designed templates for homepage, categories, events and event timelines.

TODO:

- Add event creation and edit button to category
- Check all events.ecmwf.int and local instace pages to see if there is any breaking changes
- Move to OAuth
- Write documentation
- Write automatic tests (docker).

# Local development environment

## Database pre-seeding

To get a snapshot of the production database run:

```
./scripts/backup-db.sh
```

This command will download a `postgresql.DATE.sql` into the current folder.
You will need to remove the sections with user and database creation from the file.
This is handeled directly by the postgres docker image.

Now just take down the existing database and spin up a new one:

```
docker-compose down
docker-compose up
```

The postgresql container will automatically find all `*.sql` files in the top level folder
and run them.
