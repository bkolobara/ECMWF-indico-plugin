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
- Write automatic tests (elixir + docker + local pgsql?).

## Update steps

- Upgrade Indico to 2.2 following instructions
- Update extension
- Delete theme
- _Do manual text changes on the category section to match reference website_
