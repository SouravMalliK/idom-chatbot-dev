# [START custom_class_def]
class Learning(object):
    def __init__(self, user, content_id="", last_content_watched_on="", content_para_1=False, content_para_2=False,
                 content_para_3=False, content_para_4=False,
                 meaning_id="", last_meaning_watched_on="", meaning_para_1=False, meaning_para_2=False,
                 meaning_para_3=False, meaning_para_4=False):
        self.user = user
        self.content_id = content_id
        self.last_conent_watched_on = last_content_watched_on
        self.content_para_1 = content_para_1
        self.content_para_2 = content_para_2
        self.content_para_3 = content_para_3
        self.content_para_4 = content_para_4
        self.meaning_id = meaning_id
        self.last_meaning_watched_on = last_meaning_watched_on
        self.meaning_para_1 = meaning_para_1
        self.meaning_para_2 = meaning_para_2
        self.meaning_para_3 = meaning_para_3
        self.meaning_para_4 = meaning_para_4

    @staticmethod
    def from_dict(source):

        # cities_ref.document(u'BJ').set(
        #     City(u'Beijing', None, u'China', True, 21500000, [u'hebei']).to_dict())

        learning = Learning(source[u'current_studying_content'][u'content_id'],
                            source[u'current_studying_content'][u'last_watched_on'],
                            source[u'current_studying_meaning'][u'meaning_id'],
                            source[u'current_studying_meaning'][u'last_watched_on']
                            )

        if u'para_1' in source[u'current_studying_content'][u'paragraphs']:
            learning.content_para_1 = source[u'current_studying_content'][u'paragraphs'][u'para_1']

        if u'para_2' in source[u'current_studying_content'][u'paragraphs']:
            learning.content_para_2 = source[u'current_studying_content'][u'paragraphs'][u'para_2']

        if u'para_3' in source[u'current_studying_content'][u'paragraphs']:
            learning.content_para_1 = source[u'current_studying_content'][u'paragraphs'][u'para_3']

        if u'para_4' in source[u'current_studying_content'][u'paragraphs']:
            learning.content_para_2 = source[u'current_studying_content'][u'paragraphs'][u'para_4']

        if u'para_1' in source[u'current_studying_meaning'][u'paragraphs']:
            learning.meaning_para_1 = source[u'current_studying_meaning'][u'paragraphs'][u'para_1']

        if u'para_2' in source[u'current_studying_meaning'][u'paragraphs']:
            learning.meaning_para_2 = source[u'current_studying_meaning'][u'paragraphs'][u'para_2']

        if u'para_3' in source[u'current_studying_meaning'][u'paragraphs']:
            learning.meaning_para_3 = source[u'current_studying_meaning'][u'paragraphs'][u'para_3']

        if u'para_4' in source[u'current_studying_meaning'][u'paragraphs']:
            learning.meaning_para_4 = source[u'current_studying_meaning'][u'paragraphs'][u'para_4']

        return learning

    def to_dict(self):
        # [START_EXCLUDE]
        db_dict = {
            "current_studying_content": {
                "last_watched_on": self.last_conent_watched_on,
                "content_id":  self.content_id ,
                # "current_status": {
                #     "para_1": self.content_para_1,
                #     "para_2": self.content_para_2,
                #     "para_3": self.content_para_3,
                #     "para_4": self.content_para_4
                # }
            },
            "current_studying_meaning": {
                "last_watched_on": self.last_meaning_watched_on,
                "meaning_id": self.meaning_id,
                # "paragraphs": {
                #     "para_3": self.meaning_para_4,
                #     "para_4": self.meaning_para_3,
                #     "para_2": self.meaning_para_2,
                #     "para_1": self.meaning_para_1
                # }
            }
        }
        return db_dict
        # [END_EXCLUDE]

    def __repr__(self):
        return (
            u'Learning(user={}, content_id={}, last_conent_watched_on={}, content_para_1={}, content_para_2={},'
            u'content_para_3={}, content_para_4={},'
            u'meaning_id={}, last_meaning_watched_on={}, meaning_para_1={}, meaning_para_2={}, '
            u'meaning_para_3={}, meaning_para_4={})'
                .format(self.user, self.content_id, self.last_conent_watched_on, self.content_para_1,
                        self.content_para_2, self.content_para_3, self.content_para_4,
                        self.meaning_id, self.last_meaning_watched_on, self.meaning_para_1, self.meaning_para_2,
                        self.meaning_para_3, self.meaning_para_4))

# [END custom_class_def]
