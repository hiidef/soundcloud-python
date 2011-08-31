from __future__ import with_statement

import os
import urllib2
import itertools
from textwrap import dedent
import pkg_resources
import logging
from unittest import TestCase

from configobj import ConfigObj
from validate import Validator


import soundcloud

logger = logging.getLogger("soundcloud.tests")

api_logger = logging.getLogger("soundcloud")


class soundcloudTests(TestCase):

    CONFIG_NAME = "test.ini"
    CLIENT_ID = None
    CLIENT_SECRET = None
    TOKEN_URI = None
    REDIRECT_URI = None
    API_HOST = None 
    RUN_INTERACTIVE_TESTS = False
    RUN_LONG_TESTS = False
    TOKEN = None
    
    def setUp(self):
        self._load_config()
        assert pkg_resources.resource_exists("soundcloud.tests.soundcloud_tests", "knaster.mp3")
        self.data = pkg_resources.resource_stream("soundcloud.tests.soundcloud_tests", "knaster.mp3")
        self.artwork_data = pkg_resources.resource_stream("soundcloud.tests.soundcloud_tests", "spam.jpg")


    CONFIGSPEC=dedent("""
    [api]
    api_host=string(default=api.soundcloud.com)
    client_id=string
    client_secret=string
    token_uri=string
    redirect_uri=string
    access_token=string
    
    [proxy]
    use_proxy=boolean(default=false)
    proxy=string(default=http://127.0.0.1:10000/)

    [logging]
    test_logger=string(default=ERROR)
    api_logger=string(default=ERROR)

    [test]
    run_interactive_tests=boolean(default=false)
    """)


    def _load_config(self):
        """
        Loads the configuration by looking from

         - the environment variable soundcloud_CONFIG
         - the installation location upwards until it finds test.ini
         - the current working directory upwards until it finds test.ini

        Raises an error if there is no config found
        """
        config_name = self.CONFIG_NAME

        name = None

        if "soundcloud_CONFIG" in os.environ:
            if os.path.exists(os.environ["soundcloud_CONFIG"]):
                name = os.environ["soundcloud_CONFIG"]

        def search_for_config(current):
            while current:
                name = os.path.join(current, config_name)
                if os.path.exists(name):
                    return name
                new_current = os.path.dirname(current)
                if new_current == current:
                    return
                current = new_current

        if name is None:
            name = search_for_config(os.path.dirname(__file__))
        if name is None:
            name = search_for_config(os.getcwd())

        if not name:
            raise Exception("No test configuration file found!")

        parser = ConfigObj(name, configspec=self.CONFIGSPEC.split("\n"))
        val = Validator()
        if not parser.validate(val):
            raise Exception("Config file validation error")

        api = parser['api']
        self.API_HOST = api.get('api_host')
        self.CLIENT_ID = api.get('client_id')
        self.CLIENT_SECRET = api.get('client_secret')
        self.TOKEN_URI = api.get('token_uri')
        self.REDIRECT_URI = api.get('redirect_uri')
        self.TOKEN = api.get('access_token')

        if "proxy" in parser and parser["proxy"]["use_proxy"]:
            soundcloud.USE_PROXY = True
            soundcloud.PROXY = parser["proxy"]["proxy"]

        if "logging" in parser:
            logger.setLevel(getattr(logging, parser["logging"]["test_logger"]))
            api_logger.setLevel(getattr(logging, parser["logging"]["api_logger"]))

        self.RUN_INTERACTIVE_TESTS = parser["test"]["run_interactive_tests"]
        

    @property
    def root(self):
        """
        Return the properly configured root-scope.
        """
        if self.TOKEN is None:
            raise Exception("You haven't entered an access_token in your test.ini yet. Please run bootstrap_test.py first!")

        authenticator = soundcloud.OAuth2Authenticator( self.CLIENT_ID,
                                                        self.CLIENT_SECRET,
                                                        self.REDIRECT_URI,
                                                        self.TOKEN)
        connector = soundcloud.ApiConnector(authenticator)

        return soundcloud.Scope(connector)


    def test_connect(self):
        """
        test_connect

        Tries to connect & performs some read-only operations.
        """
        sca = self.root
    #     quite_a_few_users = list(itertools.islice(sca.users(), 0, 127))

    #     logger.debug(quite_a_few_users)
    #     assert isinstance(quite_a_few_users, list) and isinstance(quite_a_few_users[0], soundcloud.User)
        user = sca.me()
        logger.debug(user)
        assert isinstance(user, soundcloud.User)
        contacts = list(user.contacts())
        assert isinstance(contacts, list)
        if contacts:
            assert isinstance(contacts[0], soundcloud.User)
            logger.debug(contacts)
        tracks = list(user.tracks())
        assert isinstance(tracks, list)
        if tracks:
            assert isinstance(tracks[0], soundcloud.Track)
            logger.debug(tracks)

    def test_track_creation(self):
        sca = self.root
        track = sca.Track.new(title='bar', asset_data=self.data)
        assert isinstance(track, soundcloud.Track)


    def test_track_update(self):
        sca = self.root
        track = sca.Track.new(title='bar', asset_data=self.data)
        assert isinstance(track, soundcloud.Track)
        track.title='baz'
        track = sca.Track.get(track.id)
        assert track.title == "baz"


    def test_scoped_track_creation(self):
        sca = self.root
        user = sca.me()
        track = user.tracks.new(title="bar", asset_data=self.data)
        assert isinstance(track, soundcloud.Track)


    def test_upload(self):
        sca = self.root
        sca = self.root
        track = sca.Track.new(title='bar', asset_data=self.data)
        assert isinstance(track, soundcloud.Track)


    def test_contact_list(self):
        sca = self.root
        user = sca.me()
        contacts = list(user.contacts())
        assert isinstance(contacts, list)
        if contacts:
            assert isinstance(contacts[0], soundcloud.User)


    def test_permissions(self):
        sca = self.root
        user = sca.me()
        tracks = itertools.islice(user.tracks(), 1)
        for track in tracks:
            permissions = list(track.permissions())
            logger.debug(permissions)
            assert isinstance(permissions, list)
            if permissions:
                assert isinstance(permissions[0], soundcloud.User)


    def test_setting_permissions(self):
        sca = self.root
        me = sca.me()
        track = sca.Track.new(title='bar', sharing="private", asset_data=self.data)
        assert track.sharing == "private"
        users = itertools.islice(sca.users(), 10)
        users_to_set = [user  for user in users if user != me]
        assert users_to_set, "Didn't find any suitable users"
        track.permissions = users_to_set
        assert set(track.permissions()) == set(users_to_set)


    def test_setting_comments(self):
        sca = self.root
        user = sca.me()
        track = sca.Track.new(title='bar', sharing="private", asset_data=self.data)
        comment = sca.Comment.create(body="This is the body of my comment", timestamp=10)
        track.comments = comment
        assert track.comments().next().body == comment.body


    def test_setting_comments_the_way_shawn_says_its_correct(self):
        sca = self.root
        track = sca.Track.new(title='bar', sharing="private", asset_data=self.data)
        cbody = "This is the body of my comment"
        track.comments.new(body=cbody, timestamp=10)
        assert list(track.comments())[0].body == cbody


    def test_contact_add_and_removal(self):
        sca = self.root
        me = sca.me()
        for user in sca.users():
            if user != me:            
                user_to_set = user
                break

        contacts = list(me.contacts())
        if user_to_set in contacts:
            me.contacts.remove(user_to_set)

        me.contacts.append(user_to_set)

        contacts = list(me.contacts() )
        assert user_to_set.id in [c.id for c in contacts]

        me.contacts.remove(user_to_set)

        contacts = list(me.contacts() )
        assert user_to_set not in contacts


    def test_favorites(self):
        sca = self.root
        me = sca.me()

        favorites = list(me.favorites())
        assert favorites == [] or isinstance(favorites[0], soundcloud.Track)

        track = None
        for user in sca.users():
            if user == me:
                continue
            for track in user.tracks():
                break
            if track is not None:
                break

        me.favorites.append(track)

        favorites = list(me.favorites())
        assert track in favorites

        me.favorites.remove(track)

        favorites = list(me.favorites())
        assert track not in favorites


    def test_large_list(self):
        if not self.RUN_LONG_TESTS:
            return
        
        sca = self.root
        
        tracks = list(sca.tracks())
        if len(tracks) < soundcloud.ApiConnector.LIST_LIMIT:
            for i in xrange(soundcloud.ApiConnector.LIST_LIMIT):
                sca.Track.new(title='test_track_%i' % i, asset_data=self.data)
        all_tracks = sca.tracks()
        assert not isinstance(all_tracks, list)
        all_tracks = list(all_tracks)
        assert len(all_tracks) > soundcloud.ApiConnector.LIST_LIMIT



    def test_filtered_list(self):
        if not self.RUN_LONG_TESTS:
            return
        
        sca = self.root
    
        tracks = list(sca.tracks(params={
            "bpm[from]" : "180",
            }))
        if len(tracks) < soundcloud.ApiConnector.LIST_LIMIT:
            for i in xrange(soundcloud.ApiConnector.LIST_LIMIT):
                sca.Track.new(title='test_track_%i' % i, asset_data=self.data)
        all_tracks = sca.tracks()
        assert not isinstance(all_tracks, list)
        all_tracks = list(all_tracks)
        assert len(all_tracks) > soundcloud.ApiConnector.LIST_LIMIT


    def test_me_having_stress(self):
        sca = self.root
        for _ in xrange(20):
            self.setUp()
            sca.me()


    def test_non_global_api(self):
        root = self.root
        me = root.me()
        assert isinstance(me, soundcloud.User)

        # now get something *from* that user
        list(me.favorites())


    def test_playlists(self):
        sca = self.root
        playlists = list(itertools.islice(sca.playlists(), 0, 127))
        for playlist in playlists:
            tracks = playlist.tracks
            if not isinstance(tracks, list):
                tracks = [tracks]
            for trackdata in tracks:
                print trackdata
                #user = trackdata.user
                #print user
                #print user.tracks()
            print playlist.user
            break




    def test_playlist_creation(self):
        sca = self.root
        sca.Playlist.new(title="I'm so happy, happy, happy, happy!")
        


    def test_groups(self):
        if not self.RUN_LONG_TESTS:
            return
        
        sca = self.root
        groups = list(itertools.islice(sca.groups(), 0, 127))
        for group in groups:
            users = group.users()
            for user in users:
                pass


    def test_track_creation_with_email_sharers(self):
        sca = self.root
        emails = [dict(address="hans+sctest@hiidef.com")]
        track = sca.Track.new(title='bar', asset_data=self.data,
                              shared_to=dict(emails=emails)
                              )
        assert isinstance(track, soundcloud.Track)



    def test_track_creation_with_artwork(self):
        sca = self.root
        track = sca.Track.new(title='bar',
                              asset_data=self.data,
                              artwork_data=self.artwork_data,
                              )
        assert isinstance(track, soundcloud.Track)

        track.title = "foobarbaz"
        


    def test_oauth_get_signing(self):
        sca = self.root

        url = "http://api.soundcloud.dev/oauth/test_request"
        params = dict(foo="bar",
                      baz="padamm",
                      )
        url += sca._create_query_string(params)
        signed_url = sca.oauth_sign_get_request(url)

        
        res = urllib2.urlopen(signed_url).read()
        assert "oauth_nonce" in res


    def test_streaming(self):
        sca = self.root

        track = sca.tracks(params={
            "filter" : "streamable",
            }).next()

        
        assert isinstance(track, soundcloud.Track)

        stream_url = track.stream_url

        signed_url = track.oauth_sign_get_request(stream_url)

        
    def test_downloadable(self):
        sca = self.root

        track = sca.tracks(params={
            "filter" : "downloadable",
            }).next()

        
        assert isinstance(track, soundcloud.Track)

        download_url = track.download_url

        signed_url = track.oauth_sign_get_request(download_url)

        data = urllib2.urlopen(signed_url).read()
        assert data



    def test_modifying_playlists(self):
        sca = self.root

        me = sca.me()
        my_tracks = list(me.tracks())

        assert my_tracks

        playlist = me.playlists().next()
        # playlist = sca.Playlist.get(playlist.id)

        assert isinstance(playlist, soundcloud.Playlist)

        pl_tracks = playlist.tracks

        playlist.title = "foobarbaz"



    def test_track_deletion(self):
        sca = self.root
        track = sca.Track.new(title='bar', asset_data=self.data,
                              )

        sca.tracks.remove(track)

        

    def test_track_creation_with_updated_artwork(self):
        sca = self.root
        track = sca.Track.new(title='bar',
                              asset_data=self.data,
                              )
        assert isinstance(track, soundcloud.Track)

        track.artwork_data = self.artwork_data

    def test_update_own_description(self):
        sca = self.root
        me = sca.me()
        
        new_description = "This is my new description"
        old_description = "This is my old description"
        
        if me.description == new_description:
          change_to_description = old_description
        else:
          change_to_description = new_description
        
        me.description = change_to_description
        
        user = sca.User.get(me.id)
        assert user.description == change_to_description
