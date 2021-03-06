#
# Copyright (c) 2019 Nightwatch Cybersecurity.
#
# This file is part of truegaze
# (see https://github.com/nightwatchcybersecurity/truegaze).
#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
#
import io, plistlib, re
from zipfile import ZipFile, ZipInfo

from truegaze.utils import ANDROID_MANIFEST, TruegazeUtils


# Tests for utils.get_version()
class TestUtilsGetVersion(object):
    def test_format_valid(self):
        pattern = re.compile(r'^(\d+\.)?(\d+\.)?(\*|\d+)$')
        assert pattern.match(TruegazeUtils.get_version()) is not None


# Tests for utils.open_file_as_zip()
class TestUtilsOpenFileAsZip(object):
    def test_not_found(self):
        assert TruegazeUtils.open_file_as_zip('blablabla') is None

    def test_invalid_empty(self):
        assert TruegazeUtils.open_file_as_zip(io.BytesIO()) is None

    def test_invalid_not_zip(self):
        assert TruegazeUtils.open_file_as_zip(io.StringIO('foobar data')) is None

    def test_valid_zip(self):
        zip_buffer = io.BytesIO()
        zip_file = ZipFile(zip_buffer, 'a')
        zip_file.writestr('testfile', 'testdata')
        zip_file.close()
        assert TruegazeUtils.open_file_as_zip(zip_buffer) is not None


# Tests for utils.get_android_manifest()
class TestUtilsGetAndroidManifest(object):
    def test_empty(self):
        zip_file = ZipFile(io.BytesIO(), 'a')
        assert TruegazeUtils.get_android_manifest(zip_file) is None

    def test_not_empty(self):
        zip_file = ZipFile(io.BytesIO(), 'a')
        zip_file.writestr("test", 'testdata')
        assert TruegazeUtils.get_android_manifest(zip_file) is None

    def test_empty_manifest(self):
        zip_file = ZipFile(io.BytesIO(), 'a')
        zip_file.writestr(ANDROID_MANIFEST, '')
        assert TruegazeUtils.get_android_manifest(zip_file) is None

    def test_wrong_directory(self):
        zip_file = ZipFile(io.BytesIO(), 'a')
        zip_file.writestr('assets/' + ANDROID_MANIFEST, 'manifest data')
        assert TruegazeUtils.get_android_manifest(zip_file) is None

    def test_directory_with_right_name(self):
        info = ZipInfo('assets/' + ANDROID_MANIFEST)
        info.external_attr = 16
        zip_file = ZipFile(io.BytesIO(), 'a')
        zip_file.writestr(info, '')
        assert TruegazeUtils.get_android_manifest(zip_file) is None

    def test_valid(self):
        zip_file = ZipFile(io.BytesIO(), 'a')
        zip_file.writestr(ANDROID_MANIFEST, 'manifest data')
        assert TruegazeUtils.get_android_manifest(zip_file) == ANDROID_MANIFEST


# Tests for utils.get_ios_manifest()
class TestUtilsGetiOSManifest(object):
    @staticmethod
    def make_ios_manifest():
        data = dict(
            CFBundleDisplayName='some app',
            CFBundleIdentifier='com.example.app',
            CFBundleShortVersionString='1.0'
        )
        buffer = io.BytesIO()
        plistlib.dump(data, buffer)
        return buffer.getvalue()

    def test_empty(self):
        zip_file = ZipFile(io.BytesIO(), 'a')
        assert TruegazeUtils.get_ios_manifest(zip_file) is None

    def test_not_empty(self):
        zip_file = ZipFile(io.BytesIO(), 'a')
        zip_file.writestr("test", 'testdata')
        assert TruegazeUtils.get_ios_manifest(zip_file) is None

    def test_wrong_directory1(self):
        zip_file = ZipFile(io.BytesIO(), 'a')
        zip_file.writestr('Info.plist', TestUtilsGetiOSManifest.make_ios_manifest())
        assert TruegazeUtils.get_ios_manifest(zip_file) is None

    def test_wrong_directory2(self):
        zip_file = ZipFile(io.BytesIO(), 'a')
        zip_file.writestr('Payload/Info.plist', TestUtilsGetiOSManifest.make_ios_manifest())
        assert TruegazeUtils.get_ios_manifest(zip_file) is None

    def test_wrong_directory3(self):
        zip_file = ZipFile(io.BytesIO(), 'a')
        zip_file.writestr('Payload/Testapp/Info.plist', TestUtilsGetiOSManifest.make_ios_manifest())
        assert TruegazeUtils.get_ios_manifest(zip_file) is None

    def test_empty_manifest(self):
        zip_file = ZipFile(io.BytesIO(), 'a')
        zip_file.writestr('Payload/Test.app/Info.plist', '')
        assert TruegazeUtils.get_ios_manifest(zip_file) is None

    def test_junk_manifest(self):
        zip_file = ZipFile(io.BytesIO(), 'a')
        zip_file.writestr('Payload/Test.app/Info.plist', '<junk></junk>')
        assert TruegazeUtils.get_ios_manifest(zip_file) is None

    def test_manifest_with_no_keys(self):
        buffer = io.BytesIO()
        plistlib.dump({}, buffer)
        zip_file = ZipFile(io.BytesIO(), 'a')
        zip_file.writestr('Payload/Test.app/Info.plist', buffer.getvalue())
        assert TruegazeUtils.get_ios_manifest(zip_file) is None

    def test_manifest_with_some_keys1(self):
        buffer = io.BytesIO()
        plistlib.dump(dict(CFBundleDisplayName='some app'), buffer)
        zip_file = ZipFile(io.BytesIO(), 'a')
        zip_file.writestr('Payload/Test.app/Info.plist', buffer.getvalue())
        assert TruegazeUtils.get_ios_manifest(zip_file) is None

    def test_manifest_with_some_keys2(self):
        buffer = io.BytesIO()
        plistlib.dump(dict(CFBundleIdentifier='some app'), buffer)
        zip_file = ZipFile(io.BytesIO(), 'a')
        zip_file.writestr('Payload/Test.app/Info.plist', buffer.getvalue())
        assert TruegazeUtils.get_ios_manifest(zip_file) is None

    def test_manifest_with_some_keys3(self):
        buffer = io.BytesIO()
        plistlib.dump(dict(CFBundleShortVersionString='some app'), buffer)
        zip_file = ZipFile(io.BytesIO(), 'a')
        zip_file.writestr('Payload/Test.app/Info.plist', buffer.getvalue())
        assert TruegazeUtils.get_ios_manifest(zip_file) is None

    def test_valid(self):
        zip_file = ZipFile(io.BytesIO(), 'a')
        zip_file.writestr('Payload/Test.app/Info.plist', TestUtilsGetiOSManifest.make_ios_manifest())
        assert TruegazeUtils.get_ios_manifest(zip_file) == 'Payload/Test.app/Info.plist'


# Tests for utils.get_matching_paths_from_zip()
class TestUtilsGetMatchingPathsFromZipFile(object):
    def test_empty(self):
        zip_file = ZipFile(io.BytesIO(), 'a')
        paths = TruegazeUtils.get_matching_paths_from_zip(zip_file, re.compile(r'.*'))
        assert len(paths) == 0

    def test_valid_one_file(self):
        zip_file = ZipFile(io.BytesIO(), 'a')
        zip_file.writestr('test', '')
        paths = TruegazeUtils.get_matching_paths_from_zip(zip_file, re.compile(r'.*'))
        assert len(paths) == 1
        assert paths[0] == 'test'

    def test_valid_three_files(self):
        zip_file = ZipFile(io.BytesIO(), 'a')
        zip_file.writestr('test1.txt', '')
        zip_file.writestr('test/test2.doc', '')
        zip_file.writestr('test/test/test3.md', '')
        paths = TruegazeUtils.get_matching_paths_from_zip(zip_file, re.compile(r'.*est/test.*\..*'))
        assert len(paths) == 2
        assert paths[0] == 'test/test2.doc'
        assert paths[1] == 'test/test/test3.md'

    def test_valid_file_in_directory(self):
        zip_file = ZipFile(io.BytesIO(), 'a')
        zip_file.writestr('test/test.txt', 'testdata')
        paths = TruegazeUtils.get_matching_paths_from_zip(zip_file, re.compile(r'.*est.*\.txt'))
        assert len(paths) == 1
        assert paths[0] == 'test/test.txt'
