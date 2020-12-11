# -*- coding: utf-8 -*-

import json
import requests


class Client(object):

    """
    Client to interact with the Robo-CJK back-end.
    Usage:
        c = Client(host, username, password)
        data = c.projects_list()
    """

    @classmethod
    def _if_int(cls, value):
        return value if isinstance(value, int) else None


    @classmethod
    def _if_json(cls, value):
        return json.dumps(value) if isinstance(value, dict) else cls._if_str(value)


    @classmethod
    def _if_str(cls, value):
        return value if isinstance(value, str) else None


    def __init__(self, host, username, password):
        """
        Initialize a new Robo-CJK API client using the given credentials,
        then authentication is automatically managed by the client, no need to do anything.
        """
        self._host = host # 'http://164.90.229.235'
        self._username = username
        self._password = password
        self._auth_token = None


    def _api_call(self, view_name, params=None):
        """
        Call an API method by its 'view-name' passing the given params.
        """
        # get api absolute url
        url = self._api_url(view_name)
        # clean request post data (remove empty entries)
        data = params or {}
        keys = list(data.keys())
        for key in keys:
            val = data.get(key, None)
            if val is None or val == '' or val == [] or val == {}:
                del data[key]
        # build request headers
        headers = {}
        if self._auth_token:
            headers['Authorization'] = 'Bearer {}'.format(self._auth_token)
        headers['Cache-Control'] = 'no-cache'
        headers['Pragma'] = 'no-cache'
        # request options
        options = {
            'data': data,
            'headers': headers,
            'verify': self._host.startswith('https://'),
        }
        # send post request
        response = requests.post(url, **options)
        if response.status_code == 401:
            # unauthorized - request a new auth token
            auth_response = self.auth_token()
            self._auth_token = auth_response.get('data', {}).get('auth_token', None)
            if self._auth_token:
                return self._api_call(view_name, params)
        # read response json data and return dict
        response_data = response.json()
        return response_data


    def _api_url(self, view_name):
        """
        Build API absolute url for the given method.
        """
        view_names = {
            # Auth (jwt token)
            'auth_token': '/api/auth/token/',

            # Users
            'user_list': '/api/user/list/',
            'user_me': '/api/user/me/',

            # Project
            'project_list': '/api/project/list/',
            'project_get': '/api/project/get/',

            # Font
            'font_list': '/api/font/list/',
            'font_get': '/api/font/get/',
            'font_update': '/api/font/update/',

            # All glif (Atomic Element + Deep Component + Character Glyph)
            'glif_list': '/api/glif/list/',

            # Atomic Element
            'atomic_element_list': '/api/atomic-element/list/',
            'atomic_element_get': '/api/atomic-element/get/',
            'atomic_element_create': '/api/atomic-element/create/',
            'atomic_element_update': '/api/atomic-element/update/',
            'atomic_element_update_status': '/api/atomic-element/update-status/',
            'atomic_element_delete': '/api/atomic-element/delete/',
            'atomic_element_lock': '/api/atomic-element/lock/',
            'atomic_element_unlock': '/api/atomic-element/unlock/',
            'atomic_element_layer_create': '/api/atomic-element/layer/create/',
            'atomic_element_layer_rename': '/api/atomic-element/layer/rename/',
            'atomic_element_layer_update': '/api/atomic-element/layer/update/',
            'atomic_element_layer_delete': '/api/atomic-element/layer/delete/',

            # Deep Component
            'deep_component_list': '/api/deep-component/list/',
            'deep_component_get': '/api/deep-component/get/',
            'deep_component_create': '/api/deep-component/create/',
            'deep_component_update': '/api/deep-component/update/',
            'deep_component_update_status': '/api/deep-component/update-status/',
            'deep_component_delete': '/api/deep-component/delete/',
            'deep_component_lock': '/api/deep-component/lock/',
            'deep_component_unlock': '/api/deep-component/unlock/',

            # Character Glyph
            'character_glyph_list': '/api/character-glyph/list/',
            'character_glyph_get': '/api/character-glyph/get/',
            'character_glyph_create': '/api/character-glyph/create/',
            'character_glyph_update': '/api/character-glyph/update/',
            'character_glyph_update_status': '/api/character-glyph/update-status/',
            'character_glyph_delete': '/api/character-glyph/delete/',
            'character_glyph_lock': '/api/character-glyph/lock/',
            'character_glyph_unlock': '/api/character-glyph/unlock/',
            'character_glyph_layer_create': '/api/character-glyph/layer/create/',
            'character_glyph_layer_rename': '/api/character-glyph/layer/rename/',
            'character_glyph_layer_update': '/api/character-glyph/layer/update/',
            'character_glyph_layer_delete': '/api/character-glyph/layer/delete/',
        }
        url = view_names.get(view_name)
        abs_url = '{}{}'.format(self._host, url)
        return abs_url


    def auth_token(self):
        """
        Get an authorization token for the current user.
        """
        params = {
            'username': self._username,
            'password': self._password,
        }
        return self._api_call('auth_token', params)


    # def auth_refresh_token(self, token):
    #    # TODO
    #    raise NotImplementedError()


    def user_list(self):
        """
        Get the list of all Users.
        """
        return self._api_call('user_list')


    def user_me(self):
        """
        Get the data of the current User.
        """
        return self._api_call('user_me')


    def project_list(self):
        """
        Get the list of all Projects.
        """
        return self._api_call('project_list')


    def project_get(self, project_uid):
        """
        Get the data of a specific Project.
        """
        params = {
            'project_uid': project_uid,
        }
        return self._api_call('project_get', params)


    def font_list(self, project_uid):
        """
        Get the list of all Fonts.
        """
        params = {
            'project_uid': project_uid,
        }
        return self._api_call('font_list', params)


    def font_get(self, font_uid):
        """
        Get the data of a specific Font.
        """
        params = {
            'font_uid': font_uid,
        }
        return self._api_call('font_get', params)


    def font_update(self, font_uid, fontlib=None, glyphs_composition=None):
        """
        Update the fontlib or the glyphs-composition of a specific Font.
        """
        params = {
            'font_uid': font_uid,
            'fontlib': self._if_json(fontlib),
            'glyphs_composition': self._if_json(glyphs_composition),
        }
        return self._api_call('font_update', params)


    def glif_list(self,
            font_uid, status=None,
            is_locked_by_current_user=None, is_locked=None, is_empty=None,
            has_variation_axis=None, has_outlines=None, has_components=None, has_unicode=None):
        """
        Get the lists of Atomic Elements / Deep Components / Character Glyphs of a Font according to the given filters.
        """
        params = {
            'font_uid': font_uid,
            'status': status,
            'is_locked_by_current_user': is_locked_by_current_user,
            'is_locked': is_locked,
            'is_empty': is_empty,
            'has_variation_axis': has_variation_axis,
            'has_outlines': has_outlines,
            'has_components': has_components,
            'has_unicode': has_unicode,
        }
        return self._api_call('glif_list', params)


    def atomic_element_list(self,
            font_uid, status=None,
            is_locked_by_current_user=None, is_locked=None, is_empty=None,
            has_variation_axis=None, has_outlines=None, has_components=None, has_unicode=None):
        """
        Get the list of Atomic Elements of a Font according to the given filters.
        """
        params = {
            'font_uid': font_uid,
            'status': status,
            'is_locked_by_current_user': is_locked_by_current_user,
            'is_locked': is_locked,
            'is_empty': is_empty,
            'has_variation_axis': has_variation_axis,
            'has_outlines': has_outlines,
            'has_components': has_components,
            'has_unicode': has_unicode,
        }
        return self._api_call('atomic_element_list', params)


    def atomic_element_get(self, font_uid, atomic_element_id):
        """
        Get the data of an Atomic Element.
        """
        params = {
            'font_uid': font_uid,
            'id': self._if_int(atomic_element_id),
            'name': self._if_str(atomic_element_id),
        }
        return self._api_call('atomic_element_get', params)


    def atomic_element_create(self, font_uid, atomic_element_data):
        """
        Create a new Atomic Element with the specified glif data.
        """
        params = {
            'font_uid': font_uid,
            'data': atomic_element_data,
        }
        return self._api_call('atomic_element_create', params)


    def atomic_element_update(self, font_uid, atomic_element_id, atomic_element_data):
        """
        Update the glif data of an Atomic Element.
        """
        params = {
            'font_uid': font_uid,
            'id': self._if_int(atomic_element_id),
            'name': self._if_str(atomic_element_id),
            'data': atomic_element_data,
        }
        return self._api_call('atomic_element_update', params)


    def atomic_element_update_status(self, font_uid, atomic_element_id, atomic_element_status):
        """
        Update the status of an Atomic Element.
        Status value must be one of the following: 'todo', 'wip', 'checking-1', 'checking-2', 'checking-3', 'done'.
        """
        params = {
            'font_uid': font_uid,
            'id': self._if_int(atomic_element_id),
            'name': self._if_str(atomic_element_id),
            'status': atomic_element_status,
        }
        return self._api_call('atomic_element_update_status', params)


    def atomic_element_delete(self, font_uid, atomic_element_id):
        """
        Delete an Atomic Element (and all its layers).
        """
        params = {
            'font_uid': font_uid,
            'id': self._if_int(atomic_element_id),
            'name': self._if_str(atomic_element_id),
        }
        return self._api_call('atomic_element_delete', params)


    def atomic_element_lock(self, font_uid, atomic_element_id):
        """
        Lock an Atomic Element by the current user.
        """
        params = {
            'font_uid': font_uid,
            'id': self._if_int(atomic_element_id),
            'name': self._if_str(atomic_element_id),
        }
        return self._api_call('atomic_element_lock', params)


    def atomic_element_unlock(self, font_uid, atomic_element_id):
        """
        Unlock an Atomic Element by the current user.
        """
        params = {
            'font_uid': font_uid,
            'id': self._if_int(atomic_element_id),
            'name': self._if_str(atomic_element_id),
        }
        return self._api_call('atomic_element_unlock', params)


    def atomic_element_layer_create(self, font_uid, atomic_element_id, layer_name, layer_data):
        """
        Create a new Atomic Element Layer with the provided layer glif data.
        """
        params = {
            'font_uid': font_uid,
            'atomic_element_id': self._if_int(atomic_element_id),
            'atomic_element_name': self._if_str(atomic_element_id),
            'group_name': layer_name,
            'data': layer_data,
        }
        return self._api_call('atomic_element_layer_create', params)


    def atomic_element_layer_rename(self, font_uid, atomic_element_id, layer_id, layer_new_name):
        """
        Rename an Atomic Element Layer with a new name.
        """
        params = {
            'font_uid': font_uid,
            'atomic_element_id': self._if_int(atomic_element_id),
            'atomic_element_name': self._if_str(atomic_element_id),
            'id': self._if_int(layer_id),
            'group_name': self._if_str(layer_id),
            'new_group_name': layer_new_name,
        }
        return self._api_call('atomic_element_layer_rename', params)


    def atomic_element_layer_update(self, font_uid, atomic_element_id, layer_id, layer_data):
        """
        Update an Atomic Element Layer glif data.
        """
        params = {
            'font_uid': font_uid,
            'atomic_element_id': self._if_int(atomic_element_id),
            'atomic_element_name': self._if_str(atomic_element_id),
            'id': self._if_int(layer_id),
            'group_name': self._if_str(layer_id),
            'data': layer_data,
        }
        return self._api_call('atomic_element_layer_update', params)


    def atomic_element_layer_delete(self, font_uid, atomic_element_id, layer_id):
        """
        Delete an Atomic Element Layer.
        """
        params = {
            'font_uid': font_uid,
            'atomic_element_id': self._if_int(atomic_element_id),
            'atomic_element_name': self._if_str(atomic_element_id),
            'id': self._if_int(layer_id),
            'group_name': self._if_str(layer_id),
        }
        return self._api_call('atomic_element_layer_delete', params)


    def deep_component_list(self,
            font_uid, status=None,
            is_locked_by_current_user=None, is_locked=None, is_empty=None,
            has_variation_axis=None, has_outlines=None, has_components=None, has_unicode=None):
        """
        Get the list of Deep Components of a Font according to the given filters.
        """
        params = {
            'font_uid': font_uid,
            'status': status,
            'is_locked_by_current_user': is_locked_by_current_user,
            'is_locked': is_locked,
            'is_empty': is_empty,
            'has_variation_axis': has_variation_axis,
            'has_outlines': has_outlines,
            'has_components': has_components,
            'has_unicode': has_unicode,
        }
        return self._api_call('deep_component_list', params)


    def deep_component_get(self, font_uid, deep_component_id):
        """
        Get the data of a Deep Component.
        """
        params = {
            'font_uid': font_uid,
            'id': self._if_int(deep_component_id),
            'name': self._if_str(deep_component_id),
        }
        return self._api_call('deep_component_get', params)


    def deep_component_create(self, font_uid, deep_component_data):
        """
        Create a new Deep Component with the specified glif data.
        """
        params = {
            'font_uid': font_uid,
            'data': deep_component_data,
        }
        return self._api_call('deep_component_create', params)


    def deep_component_update(self, font_uid, deep_component_id, deep_component_data):
        """
        Update the data of a Deep Component.
        """
        params = {
            'font_uid': font_uid,
            'id': self._if_int(deep_component_id),
            'name': self._if_str(deep_component_id),
            'data': deep_component_data,
        }
        return self._api_call('deep_component_update', params)


    def deep_component_update_status(self, font_uid, deep_component_id, deep_component_status):
        """
        Update the status of a Deep Component.
        Status value must be one of the following: 'todo', 'wip', 'checking-1', 'checking-2', 'checking-3', 'done'.
        """
        params = {
            'font_uid': font_uid,
            'id': self._if_int(deep_component_id),
            'name': self._if_str(deep_component_id),
            'status': deep_component_status,
        }
        return self._api_call('deep_component_update_status', params)


    def deep_component_delete(self, font_uid, deep_component_id):
        """
        Delete a Deep Component.
        """
        params = {
            'font_uid': font_uid,
            'id': self._if_int(deep_component_id),
            'name': self._if_str(deep_component_id),
        }
        return self._api_call('deep_component_delete', params)


    def deep_component_lock(self, font_uid, deep_component_id):
        """
        Lock a Deep Component by the current user.
        """
        params = {
            'font_uid': font_uid,
            'id': self._if_int(deep_component_id),
            'name': self._if_str(deep_component_id),
        }
        return self._api_call('deep_component_lock', params)


    def deep_component_unlock(self, font_uid, deep_component_id):
        """
        Unlock a Deep Component by the current user.
        """
        params = {
            'font_uid': font_uid,
            'id': self._if_int(deep_component_id),
            'name': self._if_str(deep_component_id),
        }
        return self._api_call('deep_component_unlock', params)


    def character_glyph_list(self,
            font_uid, status=None,
            is_locked_by_current_user=None, is_locked=None, is_empty=None,
            has_variation_axis=None, has_outlines=None, has_components=None, has_unicode=None):
        """
        Get the list of Character Glyphs of a Font according to the given filters.
        """
        params = {
            'font_uid': font_uid,
            'status': status,
            'is_locked_by_current_user': is_locked_by_current_user,
            'is_locked': is_locked,
            'is_empty': is_empty,
            'has_variation_axis': has_variation_axis,
            'has_outlines': has_outlines,
            'has_components': has_components,
            'has_unicode': has_unicode,
        }
        return self._api_call('character_glyph_list', params)


    def character_glyph_get(self, font_uid, character_glyph_id):
        """
        Get the data of a Character Glyph.
        """
        params = {
            'font_uid': font_uid,
            'id': self._if_int(character_glyph_id),
            'name': self._if_str(character_glyph_id),
        }
        return self._api_call('character_glyph_get', params)


    def character_glyph_create(self, font_uid, character_glyph_data):
        """
        Create a new Character Glyph with the specified glif data.
        """
        params = {
            'font_uid': font_uid,
            'data': character_glyph_data,
        }
        return self._api_call('character_glyph_create', params)


    def character_glyph_update(self, font_uid, character_glyph_id, character_glyph_data):
        """
        Update the data of a Character Glyph.
        """
        params = {
            'font_uid': font_uid,
            'id': self._if_int(character_glyph_id),
            'name': self._if_str(character_glyph_id),
            'data': character_glyph_data,
        }
        return self._api_call('character_glyph_update', params)


    def character_glyph_update_status(self, font_uid, character_glyph_id, character_glyph_status):
        """
        Update the status of a Character Glyph.
        Status value must be one of the following: 'todo', 'wip', 'checking-1', 'checking-2', 'checking-3', 'done'.
        """
        params = {
            'font_uid': font_uid,
            'id': self._if_int(character_glyph_id),
            'name': self._if_str(character_glyph_id),
            'status': character_glyph_status,
        }
        return self._api_call('character_glyph_update_status', params)


    def character_glyph_delete(self, font_uid, character_glyph_id):
        """
        Delete a Character Glyph (and all its layers).
        """
        params = {
            'font_uid': font_uid,
            'id': self._if_int(character_glyph_id),
            'name': self._if_str(character_glyph_id),
        }
        return self._api_call('character_glyph_delete', params)


    def character_glyph_lock(self, font_uid, character_glyph_id):
        """
        Lock a Character Glyph by the current user.
        """
        params = {
            'font_uid': font_uid,
            'id': self._if_int(character_glyph_id),
            'name': self._if_str(character_glyph_id),
        }
        return self._api_call('character_glyph_lock', params)


    def character_glyph_unlock(self, font_uid, character_glyph_id):
        """
        Unlock a Character Glyph by the current user.
        """
        params = {
            'font_uid': font_uid,
            'id': self._if_int(character_glyph_id),
            'name': self._if_str(character_glyph_id),
        }
        return self._api_call('character_glyph_unlock', params)


    def character_glyph_layer_create(self, font_uid, character_glyph_id, layer_name, layer_data):
        """
        Create a new Character Glyph Layer with the provided layer glif data.
        """
        params = {
            'font_uid': font_uid,
            'character_glyph_id': self._if_int(character_glyph_id),
            'character_glyph_name': self._if_str(character_glyph_id),
            'group_name': layer_name,
            'data': layer_data,
        }
        return self._api_call('character_glyph_layer_create', params)


    def character_glyph_layer_rename(self, font_uid, character_glyph_id, layer_id, layer_new_name):
        """
        Rename a Character Glyph Layer with a new name.
        """
        params = {
            'font_uid': font_uid,
            'character_glyph_id': self._if_int(character_glyph_id),
            'character_glyph_name': self._if_str(character_glyph_id),
            'id': self._if_int(layer_id),
            'group_name': self._if_str(layer_id),
            'new_group_name': layer_new_name,
        }
        return self._api_call('character_glyph_layer_rename', params)


    def character_glyph_layer_update(self, font_uid, character_glyph_id, layer_id, layer_data):
        """
        Update a Character Glyph Layer glif data.
        """
        params = {
            'font_uid': font_uid,
            'character_glyph_id': self._if_int(character_glyph_id),
            'character_glyph_name': self._if_str(character_glyph_id),
            'id': self._if_int(layer_id),
            'group_name': self._if_str(layer_id),
            'data': layer_data,
        }
        return self._api_call('character_glyph_layer_update', params)


    def character_glyph_layer_delete(self, font_uid, character_glyph_id, layer_id):
        """
        Delete a Character Glyph Layer.
        """
        params = {
            'font_uid': font_uid,
            'character_glyph_id': self._if_int(character_glyph_id),
            'character_glyph_name': self._if_str(character_glyph_id),
            'id': self._if_int(layer_id),
            'group_name': self._if_str(layer_id),
        }
        return self._api_call('character_glyph_layer_delete', params)

