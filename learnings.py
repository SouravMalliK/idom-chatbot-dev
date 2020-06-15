# [START custom_class_def]
class Learning(object):
    def __init__(self, user, content_id, meaning_id, question_id, introduction_status=False,
                 story_status=False, meaning_status=False, example_status=False):
        self.user = user
        self.content_id = content_id
        self.meaning_id = meaning_id
        self.question_id = question_id
        self.introduction_status = introduction_status
        self.story_status = story_status
        self.meaning_status = meaning_status
        self.exaple_status = example_status

    @staticmethod
    def from_dict(source):
        learning = Learning(source[u'content_id'], source[u'meaning_id'], source[u'question_id'])

        if u'introduction_status' in source:
            learning.introduction_status = source[u'introduction_status']

        if u'story_status' in source:
            learning.story_status = source[u'story_status']

        if u'meaning_status' in source:
            learning.meaning_status = source[u'meaning_status']

        if u'example_status' in source:
            learning.example_status = source[u'example_status']

        return learning

    def to_dict(self):
        # [START_EXCLUDE]
        dest = {
            u'content_id': self.content_id,
            u'meaning_id': self.meaning_id,
            u'question_id': self.question_id
        }

        if self.introduction_status:
            dest[u'capital'] = self.capital

        if self.population:
            dest[u'population'] = self.population

        if self.regions:
            dest[u'regions'] = self.regions

        return dest
        # [END_EXCLUDE]

    def __repr__(self):
        return(
            u'City(name={}, country={}, population={}, capital={}, regions={})'
            .format(self.name, self.country, self.population, self.capital,
                    self.regions))
# [END custom_class_def]