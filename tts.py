import os
import platform
import re
import tempfile
import subprocess
import pipes
import logging
import wave
import urllib
import urlparse
import requests
from abc import ABCMeta, abstractmethod

import argparse
import yaml

class AbstractTTSEngine(object):
    """
    Generic parent class for all speakers
    """
    __metaclass__ = ABCMeta

    @classmethod
    def get_config(cls):
        return {}

    @classmethod
    def get_instance(cls):
        config = cls.get_config()
        instance = cls(**config)
        return instance

    @classmethod
    @abstractmethod
    def is_available(cls):
        return diagnose.check_executable('aplay')

    def __init__(self, **kwargs):
        self._logger = logging.getLogger(__name__)

    @abstractmethod
    def say(self, phrase, *args):
        pass

    def play(self, filename):
        # FIXME: Use platform-independent audio-output here
        # See issue jasperproject/jasper-client#188
        cmd = ['aplay', '-D', 'plughw:1,0', str(filename)]
        self._logger.debug('Executing %s', ' '.join([pipes.quote(arg)
                                                     for arg in cmd]))
        with tempfile.TemporaryFile() as f:
            subprocess.call(cmd, stdout=f, stderr=f)
            f.seek(0)
            output = f.read()
            if output:
                self._logger.debug("Output was: '%s'", output)




class MaryTTS(AbstractTTSEngine):
    """
    Uses the MARY Text-to-Speech System (MaryTTS)
    MaryTTS is an open-source, multilingual Text-to-Speech Synthesis platform
    written in Java.
    Please specify your own server instead of using the demonstration server
    (http://mary.dfki.de:59125/) to save bandwidth and to protect your privacy.
    """

    SLUG = "mary-tts"

    def __init__(self, server="mary.dfki.de", port="59125", language="en_GB",
                 voice="dfki-spike"):
        super(self.__class__, self).__init__()
        self.server = server
        self.port = port
        self.netloc = '{server}:{port}'.format(server=self.server,
                                               port=self.port)
        self.language = language
        self.voice = voice
        self.session = requests.Session()

    @property
    def languages(self):
        try:
            r = self.session.get(self._makeurl('/locales'))
            r.raise_for_status()
        except requests.exceptions.RequestException:
            self._logger.critical("Communication with MaryTTS server at %s " +
                                  "failed.", self.netloc)
            raise
        return r.text.splitlines()

    @property
    def voices(self):
        r = self.session.get(self._makeurl('/voices'))
        r.raise_for_status()
        return [line.split()[0] for line in r.text.splitlines()]

    @classmethod
    def get_config(cls):
        # FIXME: Replace this as soon as we have a config module
        config = {}
        # HMM dir
        # Try to get hmm_dir from config
        profile_path = jasperpath.config('profile.yml')
        if os.path.exists(profile_path):
            with open(profile_path, 'r') as f:
                profile = yaml.safe_load(f)
                if 'mary-tts' in profile:
                    if 'server' in profile['mary-tts']:
                        config['server'] = profile['mary-tts']['server']
                    if 'port' in profile['mary-tts']:
                        config['port'] = profile['mary-tts']['port']
                    if 'language' in profile['mary-tts']:
                        config['language'] = profile['mary-tts']['language']
                    if 'voice' in profile['mary-tts']:
                        config['voice'] = profile['mary-tts']['voice']

        return config

    @classmethod
    def is_available(cls):
        return (super(cls, cls).is_available() and
                diagnose.check_network_connection())

    def _makeurl(self, path, query={}):
        query_s = urllib.urlencode(query)
        urlparts = ('http', self.netloc, path, query_s, '')
        return urlparse.urlunsplit(urlparts)

    def say(self, phrase):
        self._logger.debug("Saying '%s' with '%s'", phrase, self.SLUG)
        if self.language not in self.languages:
            raise ValueError("Language '%s' not supported by '%s'"
                             % (self.language, self.SLUG))

        if self.voice not in self.voices:
            raise ValueError("Voice '%s' not supported by '%s'"
                             % (self.voice, self.SLUG))
        query = {'OUTPUT_TYPE': 'AUDIO',
                 'AUDIO': 'WAVE_FILE',
                 'INPUT_TYPE': 'TEXT',
                 'INPUT_TEXT': phrase,
                 'LOCALE': self.language,
                 'VOICE': self.voice}

        r = self.session.get(self._makeurl('/process', query=query))
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
            f.write(r.content)
            tmpfile = f.name
        self.play(tmpfile)
        os.remove(tmpfile)

m = AbstractTTSEngine()
m.say("my name is")
