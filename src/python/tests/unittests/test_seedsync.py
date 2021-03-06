# Copyright 2017, Inderpreet Singh, All rights reserved.

import unittest
import sys
import copy

from common import overrides, Config
from seedsync import Seedsync


class TestSeedsync(unittest.TestCase):
    @overrides(unittest.TestCase)
    def setUp(self):
        # Make a copy of the sys argv
        self.sys_argv_orig = copy.deepcopy(sys.argv)

    @overrides(unittest.TestCase)
    def tearDown(self):
        # Restore the original sys argv
        sys.argv = self.sys_argv_orig

    def test_args_config(self):
        sys.argv.append("-c")
        sys.argv.append("/path/to/config")
        sys.argv.append("--html")
        sys.argv.append("/path/to/html")
        sys.argv.append("--scanfs")
        sys.argv.append("/path/to/scanfs")
        args = Seedsync._parse_args()
        self.assertIsNotNone(args)
        self.assertEqual("/path/to/config", args.config_dir)

        sys.argv = sys.argv[:-6]
        sys.argv.append("--config_dir")
        sys.argv.append("/path/to/config")
        sys.argv.append("--html")
        sys.argv.append("/path/to/html")
        sys.argv.append("--scanfs")
        sys.argv.append("/path/to/scanfs")
        args = Seedsync._parse_args()
        self.assertIsNotNone(args)
        self.assertEqual("/path/to/config", args.config_dir)

        sys.argv = sys.argv[:-6]
        with self.assertRaises(SystemExit):
            Seedsync._parse_args()

    def test_args_html(self):
        sys.argv.append("-c")
        sys.argv.append("/path/to/config")
        sys.argv.append("--scanfs")
        sys.argv.append("/path/to/scanfs")
        sys.argv.append("--html")
        sys.argv.append("/path/to/html")
        args = Seedsync._parse_args()
        self.assertIsNotNone(args)
        self.assertEqual("/path/to/html", args.html)

    def test_args_scanfs(self):
        sys.argv.append("-c")
        sys.argv.append("/path/to/config")
        sys.argv.append("--html")
        sys.argv.append("/path/to/html")
        sys.argv.append("--scanfs")
        sys.argv.append("/path/to/scanfs")
        args = Seedsync._parse_args()
        self.assertIsNotNone(args)
        self.assertEqual("/path/to/scanfs", args.scanfs)

    def test_args_logdir(self):
        sys.argv.append("-c")
        sys.argv.append("/path/to/config")
        sys.argv.append("--logdir")
        sys.argv.append("/path/to/logdir")
        sys.argv.append("--html")
        sys.argv.append("/path/to/html")
        sys.argv.append("--scanfs")
        sys.argv.append("/path/to/scanfs")
        args = Seedsync._parse_args()
        self.assertIsNotNone(args)
        self.assertEqual("/path/to/logdir", args.logdir)

        sys.argv = sys.argv[:-8]
        sys.argv.append("-c")
        sys.argv.append("/path/to/config")
        sys.argv.append("--html")
        sys.argv.append("/path/to/html")
        sys.argv.append("--scanfs")
        sys.argv.append("/path/to/scanfs")
        args = Seedsync._parse_args()
        self.assertIsNotNone(args)
        self.assertIsNone(args.logdir)

    def test_args_debug(self):
        sys.argv.append("-c")
        sys.argv.append("/path/to/config")
        sys.argv.append("--html")
        sys.argv.append("/path/to/html")
        sys.argv.append("--scanfs")
        sys.argv.append("/path/to/scanfs")
        sys.argv.append("-d")
        args = Seedsync._parse_args()
        self.assertIsNotNone(args)
        self.assertTrue(args.debug)

        sys.argv = sys.argv[:-7]
        sys.argv.append("-c")
        sys.argv.append("/path/to/config")
        sys.argv.append("--debug")
        sys.argv.append("--html")
        sys.argv.append("/path/to/html")
        sys.argv.append("--scanfs")
        sys.argv.append("/path/to/scanfs")
        args = Seedsync._parse_args()
        self.assertIsNotNone(args)
        self.assertTrue(args.debug)

        sys.argv = sys.argv[:-7]
        sys.argv.append("-c")
        sys.argv.append("/path/to/config")
        sys.argv.append("--html")
        sys.argv.append("/path/to/html")
        sys.argv.append("--scanfs")
        sys.argv.append("/path/to/scanfs")
        args = Seedsync._parse_args()
        self.assertIsNotNone(args)
        self.assertFalse(args.debug)

    def test_default_config(self):
        config = Seedsync._create_default_config()
        # Test that default config doesn't have any uninitialized values
        config_dict = config.as_dict()
        for section, inner_config in config_dict.items():
            for key in inner_config:
                self.assertIsNotNone(inner_config[key],
                                     msg="{}.{} is uninitialized".format(section, key))

        # Test that default config is a valid config
        config_dict = config.as_dict()
        config2 = Config.from_dict(config_dict)
        config2_dict = config2.as_dict()
        self.assertEqual(config_dict, config2_dict)

    def test_detect_incomplete_config(self):
        # Test a complete config
        config = Seedsync._create_default_config()
        incomplete_value = config.lftp.remote_address
        config.lftp.remote_address = "value"
        config.lftp.remote_username = "value"
        config.lftp.remote_path = "value"
        config.lftp.local_path = "value"
        config.lftp.remote_path_to_scan_script = "value"
        self.assertFalse(Seedsync._detect_incomplete_config(config))

        # Test incomplete configs
        config.lftp.remote_address = incomplete_value
        self.assertTrue(Seedsync._detect_incomplete_config(config))
        config.lftp.remote_address = "value"

        config.lftp.remote_username = incomplete_value
        self.assertTrue(Seedsync._detect_incomplete_config(config))
        config.lftp.remote_username = "value"

        config.lftp.remote_path = incomplete_value
        self.assertTrue(Seedsync._detect_incomplete_config(config))
        config.lftp.remote_path = "value"

        config.lftp.local_path = incomplete_value
        self.assertTrue(Seedsync._detect_incomplete_config(config))
        config.lftp.local_path = "value"

        config.lftp.remote_path_to_scan_script = incomplete_value
        self.assertTrue(Seedsync._detect_incomplete_config(config))
        config.lftp.remote_path_to_scan_script = "value"
