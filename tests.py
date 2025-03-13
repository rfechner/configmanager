import unittest
from ._api import load_config

class SimpleTest(unittest.TestCase):

    def test_json(self):
        configs = load_config('configmanager/tests/data.yaml')
        targets = [{"data": {
                        "name": "jey",
                        "num_classes": 42
                }}]
        
        for d1, d2 in zip(configs, targets):
            self.assertDictEqual(d1.asdict(), d2)

    def test_simple_loading(self):
        
        configs = load_config('configmanager/tests/data.yaml')
        targets = [{"data": {
                        "name": "jey",
                        "num_classes": 42
                }}]
        
        for d1, d2 in zip(configs, targets):
            self.assertDictEqual(d1.asdict(), d2)

    def test_simple_import(self):

        configs = load_config('configmanager/tests/test.yaml')
        targets = [{
                    "THERE": "BUDDY",
                    "hey": {
                        "another": 1,
                        "there": "buddy"
                    },
                    "model": {
                        "hey": {
                            "there": "put"
                        }
                    }
                }]
        for d1, d2 in zip(configs, targets):
            self.assertDictEqual(d1.asdict(), d2)

    def test_sinterp(self):
        configs = load_config('configmanager/tests/sinterpolation.yaml')
        targets = [{
                    "data": {
                        "name": "jey",
                        "num_classes": 42
                    },
                    "model": {
                        "num_classes": 42
                    }
                }]
        for d1, d2 in zip(configs, targets):
            self.assertDictEqual(d1.asdict(), d2)

    def test_sinterp_key(self):
        configs = load_config('configmanager/tests/sinterp_key.yaml')
        targets = [{
                    "defaults": "parameter",
                    "other": {
                        "param": 1
                    },
                    "parameter" : 1,
                    "another" : 1
                }]
        for d1, d2 in zip(configs, targets):
            self.assertDictEqual(d1.asdict(), d2)

    def test_multisinterp(self):
        configs = load_config('configmanager/tests/multi_sinterp.yaml')
        targets = [{
                    "seed" : 0,
                    "data": {
                        "num_classes": 42
                    },
                    "model": {
                        "num_classes": 42,
                        "checkpoint" : "some/where/0/over/the/42/rainbow.equinox"
                    }
                }]
        for d1, d2 in zip(configs, targets):
            self.assertDictEqual(d1.asdict(), d2)

    def test_import_overwrite(self):
        configs = load_config('configmanager/tests/test_overwrite.yaml')
        targets = [{
            "THERE": "BUDDY",
            "hey": {
                "another": 1,
                "there": "put"
            }}]
        
        for d1, d2 in zip(configs, targets):
            self.assertDictEqual(d1.asdict(), d2)

    def test_import_partial_overwrite(self):
        configs = load_config('configmanager/tests/test_partial_overwrite.yaml')
        targets = [{
                    "THERE": "BUDDY",
                    "hey": {
                        "another": 1,
                        "pleasedont": "overwriteme!",
                        "thanks": "!",
                        "there": "put"
                    }
                }]
        
        for d1, d2 in zip(configs, targets):
            self.assertDictEqual(d1.asdict(), d2)


    def test_circular_import(self):
        try:
            _ = load_config('configmanager/tests/circimport_1.yaml') # should fail
            assert False

        except RecursionError:
            pass
        
    def test_grid(self):
        configs = load_config('configmanager/tests/grid.yaml')
        targets = [{
                "model": {
                    "kwargs": {
                        "a": 1,
                        "b": 2
                    }
                },
                "optim": {
                    "kwargs": {
                        "a": 1,
                        "b": 2
                    }
                }
            }, {
                "model": {
                    "kwargs": {
                        "a": 1,
                        "b": 2
                    }
                },
                "optim": {
                    "kwargs": {
                        "a": 3,
                        "b": 4
                    }
                }
            }, {
                "model": {
                    "kwargs": {
                        "hey": {
                            "there": "put"
                        }
                    }
                },
                "optim": {
                    "kwargs": {
                        "a": 1,
                        "b": 2
                    }
                }
            }, {
                "model": {
                    "kwargs": {
                        "hey": {
                            "there": "put"
                        }
                    }
                },
                "optim": {
                    "kwargs": {
                        "a": 3,
                        "b": 4
                    }
                }
            }]
        
        for d1, d2 in zip(configs, targets):
            self.assertDictEqual(d1.asdict(), d2)

    def test_multigrid(self):
        configs = load_config('configmanager/tests/multigrid.yaml')
        targets = [{
                    "model": {
                        "kwargs": {
                            "a": 1,
                            "b": 2
                        }
                    },
                    "optim": {
                        "kwargs": {
                            "a": 1,
                            "b": 2
                        }
                    }
                }, {
                    "model": {
                        "kwargs": {
                            "a": 1,
                            "b": 2
                        }
                    },
                    "optim": {
                        "kwargs": {
                            "a": 1,
                            "b": 2
                        }
                    }
                }, {
                    "model": {
                        "kwargs": {
                            "a": 1,
                            "b": 2
                        }
                    },
                    "optim": {
                        "kwargs": {
                            "a": 3,
                            "b": 4
                        }
                    }
                }, {
                    "model": {
                        "kwargs": {
                            "hey": {
                                "there": "put"
                            }
                        }
                    },
                    "optim": {
                        "kwargs": {
                            "a": 1,
                            "b": 2
                        }
                    }
                }, {
                    "model": {
                        "kwargs": {
                            "hey": {
                                "there": "put"
                            }
                        }
                    },
                    "optim": {
                        "kwargs": {
                            "a": 1,
                            "b": 2
                        }
                    }
                }, {
                    "model": {
                        "kwargs": {
                            "hey": {
                                "there": "put"
                            }
                        }
                    },
                    "optim": {
                        "kwargs": {
                            "a": 3,
                            "b": 4
                        }
                    }
                }]
        for d1, d2 in zip(configs, targets):
            self.assertDictEqual(d1.asdict(), d2)

    def test_force_overwrite(self):
        """testing forced overwrite when specified in configuration."""

        configs = load_config('configmanager/tests/test_force_overwrite.yaml')
        targets = [{
            "THERE": "BUDDY",
            "hey": {
                "iwantsomething": "completetly_different!"
            }
        }]

        for d1, d2 in zip(configs, targets):
            self.assertDictEqual(d1.asdict(), d2)

if __name__ == '__main__':
    unittest.main()