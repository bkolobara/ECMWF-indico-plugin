from indico.modules.events.abstracts.controllers.base import RHAbstractsBase
from indico.modules.events.abstracts.models.abstracts import AbstractState
from indico.modules.events.contributions.models.persons import AuthorType
from flask_pluginengine import render_plugin_template
from pprint import pprint

class ECMWFAbstracts(RHAbstractsBase):
    """Displays the book of abstracts specifically formatted for ECMWF"""

    def _process(self):
        # pprint(vars(self.event.abstracts[1].person_links[0]))
        abstracts = []
        for abstract in self.event.abstracts:
            if abstract.state != AbstractState.accepted:
                continue
            authors = []
            affiliations = []
            for pl in abstract.person_links:
                person = pl.person
                affiliation = person.affiliation
                try:
                    affiliation_index = affiliations.index(affiliation)
                    primary = (pl.author_type == AuthorType.primary)
                    authors.append({'full_name': person.full_name, "affiliation_index": affiliation_index, 'primary': primary})
                except ValueError:
                    affiliation_index = len(affiliations)
                    primary = (pl.author_type == AuthorType.primary)
                    authors.append({'full_name': person.full_name, "affiliation_index": affiliation_index, 'primary': primary})
                    affiliations.append(affiliation)
            abstracts.append({
                'title': abstract.title,
                'description': abstract.description,
                'authors': authors,
                'affiliations': affiliations
            })
        return render_plugin_template('abstracts.html', abstracts=abstracts)
        