from indico.modules.events.abstracts.controllers.base import RHAbstractsBase
from indico.modules.events.abstracts.models.abstracts import AbstractState
from indico.modules.events.contributions.models.persons import AuthorType
from flask_pluginengine import render_plugin_template
from pprint import pprint

from datetime import datetime

class ECMWFAbstracts(RHAbstractsBase):
    """Displays the book of abstracts specifically formatted for ECMWF"""

    def _process(self):
        abstracts = []
        
        for abstract in self.event.abstracts:
            if abstract.state != AbstractState.accepted:
                continue
            authors = []
            affiliations = []
            for pl in abstract.person_links:
                person = pl.person
                affiliation = person.affiliation
                if affiliation == "":
                    primary = (pl.author_type == AuthorType.primary)
                    authors.append({'full_name': person.full_name, 'affiliation_index': '', 'primary': primary})
                    continue
                try:
                    affiliation_index = affiliations.index(affiliation) + 1
                    primary = (pl.author_type == AuthorType.primary)
                    authors.append({'full_name': person.full_name, 'affiliation_index': affiliation_index, 'primary': primary})
                except ValueError:
                    affiliation_index = len(affiliations) + 1
                    primary = (pl.author_type == AuthorType.primary)
                    authors.append({'full_name': person.full_name, 'affiliation_index': affiliation_index, 'primary': primary})
                    affiliations.append(affiliation)
            timetable_entry = abstract.contribution.timetable_entry
            abstracts.append({
                'title': abstract.title,
                'description': abstract.description,
                'authors': authors,
                'affiliations': affiliations,
                'start_dt': timetable_entry.start_dt if timetable_entry is not None else datetime.utcfromtimestamp(0),
                'starting': timetable_entry.start_dt.strftime('Starts at %H:%M on %d %b.') if timetable_entry is not None else None
            })
        abstracts.sort(key=lambda a: a['start_dt'].replace(tzinfo=None))
        return render_plugin_template('abstracts.html', abstracts=abstracts, event=self.event)
        