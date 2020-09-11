# [START custom_class_def]
class Users(object):
    def __init__(self, user_id, first_name="", last_name="", session_started=False, last_login="",
                 user_created="", locale=""):
        self.user = user_id
        self.first_name = first_name
        self.last_name = last_name
        self.session_started = session_started
        self.last_login = last_login
        self.user_created = user_created
        self.locale = locale

    @staticmethod
    def from_dict(source):

        users = Users(      source[u'user_id'],
                            source[u'first_name'],
                            source[u'last_name'],
                            source[u'session_started'],
                            source[u'user_created'],
                            source[u'last_login'],
                            source[u'locale']
                            )
        return users

    def to_dict(self):
        # [START_EXCLUDE]
        db_dict = {
                "first_name": self.first_name,
                "last_name":  self.last_name ,
                "session_started": self.session_started,
                "user_created": self.user_created,
                "last_login": self.last_login,
                "locale": self.locale
            }
        return db_dict
        # [END_EXCLUDE]

    def __repr__(self):
        return (
            u'Users(user={}, first_name={}, last_name={}, session_started={}, user_created={},' u'last_login={}'
                .format(self.user, self.first_name, self.last_name, self.session_started,
                        self.user_created, self.last_login, self.locale))

# [END custom_class_def]
