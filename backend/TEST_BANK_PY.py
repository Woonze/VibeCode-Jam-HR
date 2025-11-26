TEST_BANK_PY = {

    # EASY
    "py-easy-1": {
        "visible": [
            {"input": [1, 2], "expected": 3},
            {"input": [-1, 5], "expected": 4},
            {"input": [0, 0], "expected": 0},
        ],
        "hidden": [
            {"input": [100, 200], "expected": 300},
            {"input": [-7, -8], "expected": -15},
        ]
    },

    "py-easy-2": {
        "visible": [
            {"input": [3, 7], "expected": 7},
            {"input": [10, 5], "expected": 10},
            {"input": [-1, -9], "expected": -1},
        ],
        "hidden": [
            {"input": [1000, -1], "expected": 1000},
            {"input": [42, 42], "expected": 42},
        ]
    },

    "py-easy-3": {
        "visible": [
            {"input": ["hello"], "expected": 2},
            {"input": ["aaa"], "expected": 3},
            {"input": ["xyz"], "expected": 0},
        ],
        "hidden": [
            {"input": ["привет"], "expected": 2},
            {"input": ["aeiou"], "expected": 5},
        ]
    },

    "py-easy-4": {
        "visible": [
            {"input": ["level"], "expected": True},
            {"input": ["abba"], "expected": True},
            {"input": ["hello"], "expected": False},
        ],
        "hidden": [
            {"input": ["А роза упала на лапу Азора".lower().replace(" ", "")], "expected": True},
            {"input": ["abcba"], "expected": True},
        ]
    },

    "py-easy-5": {
        "visible": [
            {"input": [[1, 2, 3]], "expected": 6},
            {"input": [[0, 0, 0]], "expected": 0},
            {"input": [[5]], "expected": 5},
        ],
        "hidden": [
            {"input": [[10, -5, 2]], "expected": 7},
            {"input": [[100, 100]], "expected": 200},
        ]
    },

    "py-easy-6": {
        "visible": [
            {"input": ["abc"], "expected": "cba"},
            {"input": ["a"], "expected": "a"},
            {"input": [""], "expected": ""},
        ],
        "hidden": [
            {"input": ["racecar"], "expected": "racecar"},
            {"input": ["привет"], "expected": "тевирп"},
        ]
    },

    "py-easy-7": {
        "visible": [
            {"input": [[1, 2, 2, 3]], "expected": [1, 2, 3]},
            {"input": [[1, 1, 1]], "expected": [1]},
            {"input": [[3, 2, 1]], "expected": [3, 2, 1]},
        ],
        "hidden": [
            {"input": [[5, 5, 4, 4, 3]], "expected": [5, 4, 3]},
            {"input": [[10, 9, 10, 8]], "expected": [10, 9, 8]},
        ]
    },

    "py-easy-8": {
        "visible": [
            {"input": [5], "expected": 120},
            {"input": [1], "expected": 1},
            {"input": [0], "expected": 1},
        ],
        "hidden": [
            {"input": [6], "expected": 720},
            {"input": [3], "expected": 6},
        ]
    },

    "py-easy-9": {
        "visible": [
            {"input": [4], "expected": "even"},
            {"input": [5], "expected": "odd"},
            {"input": [0], "expected": "even"},
        ],
        "hidden": [
            {"input": [-2], "expected": "even"},
            {"input": [-3], "expected": "odd"},
        ]
    },

    "py-easy-10": {
        "visible": [
            {"input": [[3, 1, 4]], "expected": 1},
            {"input": [[10, 0, 20]], "expected": 0},
            {"input": [[-5, -1, -10]], "expected": -10},
        ],
        "hidden": [
            {"input": [[100, 200, 300]], "expected": 100},
            {"input": [[9, 9, 9]], "expected": 9},
        ]
    },

    # MEDIUM
    "py-med-1": {
        "visible": [
            {"input": [5], "expected": 5},
            {"input": [0], "expected": 0},
            {"input": [10], "expected": 55},
        ],
        "hidden": [
            {"input": [8], "expected": 21},
            {"input": [15], "expected": 610},
        ]
    },

    "py-med-2": {
        "visible": [
            {"input": [[1,2,3]], "expected": [3,2,1]},
            {"input": [[1]], "expected": [1]},
            {"input": [[1,2]], "expected": [2,1]},
        ],
        "hidden": [
            {"input": [[5,4,3,2]], "expected": [2,3,4,5]},
            {"input": [[10,20,30]], "expected": [30,20,10]},
        ]
    },

    "py-med-3": {
        "visible": [
            {"input": ["a b a"], "expected": {"a":2,"b":1}},
            {"input": ["hello world"], "expected": {"hello":1,"world":1}},
            {"input": ["x x x"], "expected": {"x":3}},
        ],
        "hidden": [
            {"input": ["one two two one"], "expected": {"one":2,"two":2}},
            {"input": ["hi hi HI"], "expected": {"hi":2,"HI":1}},
        ]
    },

    "py-med-4": {
        "visible": [
            {"input": [[1,[2,[3]]]], "expected": [1,2,3]},
            {"input": [[[]]], "expected": []},
            {"input": [[1,2,3]], "expected": [1,2,3]},
        ],
        "hidden": [
            {"input": [[1,[2,[3,[4]]]]], "expected": [1,2,3,4]},
            {"input": [[[1],[2,[3]]]], "expected": [1,2,3]},
        ]
    },

    "py-med-5": {
        "visible": [
            {"input": ["listen","silent"], "expected": True},
            {"input": ["abc","cba"], "expected": True},
            {"input": ["a","b"], "expected": False},
        ],
        "hidden": [
            {"input": ["night","thing"], "expected": True},
            {"input": ["hello","helloo"], "expected": False},
        ]
    },

    "py-med-6": {
        "visible": [
            {"input": [[1,2,2,3,1]], "expected": [1,2,3]},
            {"input": [[1,1,1]], "expected": [1]},
            {"input": [[3,2,1]], "expected": [3,2,1]},
        ],
        "hidden": [
            {"input": [[5,5,4,4,3]], "expected": [5,4,3]},
            {"input": [[9,8,9,7]], "expected": [9,8,7]},
        ]
    },

    "py-med-7": {
        "visible": [
            {"input": [[2,7,11,15],9], "expected": [0,1]},
            {"input": [[1,2,3],4], "expected": [0,2]},
            {"input": [[3,3],6], "expected": [0,1]},
        ],
        "hidden": [
            {"input": [[5,75,25],100], "expected": [1,2]},
            {"input": [[10,20,10,40],50], "expected": [1,3]},
        ]
    },

    "py-med-8": {
        "visible": [
            {"input": [{"a":1},{"b":2}], "expected": {"a":1,"b":2}},
            {"input": [{"x":1},{"x":2}], "expected": {"x":2}},
            {"input": [{},{}], "expected": {}},
        ],
        "hidden": [
            {"input": [{"a":1,"b":2},{"b":3}], "expected": {"a":1,"b":3}},
            {"input": [{"z":5},{"a":1}], "expected": {"z":5,"a":1}},
        ]
    },

    "py-med-9": {
        "visible": [
            {"input": ["([])"], "expected": True},
            {"input": ["()[]{}"], "expected": True},
            {"input": ["([)]"], "expected": False},
        ],
        "hidden": [
            {"input": ["((()))"], "expected": True},
            {"input": ["([{}{}])"], "expected": True},
        ]
    },

    "py-med-10": {
        "visible": [
            {"input": [[{"t":1},{"t":2},{"t":1}], "t"], "expected": {1:[{"t":1},{"t":1}], 2:[{"t":2}]}},
            {"input": [[{"a":1},{"a":1}], "a"], "expected": {1:[{"a":1},{"a":1}]}},
            {"input": [[{"x":5}], "x"], "expected": {5:[{"x":5}]}},
        ],
        "hidden": [
            {"input": [[{"t":3},{"t":3},{"t":2}], "t"], "expected": {3:[{"t":3},{"t":3}], 2:[{"t":2}]}},
        ]
    },

    # HARD
    "py-hard-1": {
        "visible": [
            {"input": [], "expected": "LRU basic test"},
        ],
        "hidden": []
    },

    "py-hard-2": {
        "visible": [
            {"input": [{"A":["B"],"B":["C"],"C":[]}, "A","C"], "expected": True},
            {"input": [{"A":["B"],"B":[]}, "B","A"], "expected": False},
        ],
        "hidden": [
            {"input": [{"A":["B","C"],"B":[],"C":["D"],"D":[]}, "A","D"], "expected": True},
        ]
    },

    "py-hard-3": {
        "visible": [
            {"input": [[3,1,2]], "expected": [1,2,3]},
            {"input": [[5,4,3,2,1]], "expected": [1,2,3,4,5]},
        ],
        "hidden": [
            {"input": [[10,9,8]], "expected": [8,9,10]},
        ]
    },

    "py-hard-4": {"visible":[{"input":[],"expected":"MiniORM basic"}],"hidden":[]},
    "py-hard-5": {"visible":[{"input":[],"expected":"BST basic"}],"hidden":[]},
    "py-hard-6": {"visible":[{"input":[],"expected":"LRU TTL basic"}],"hidden":[]},
    "py-hard-7": {
        "visible": [
            {"input": [[3,1,5,2,4], 2], "expected": [5,4]},
        ],
        "hidden": [
            {"input": [[10,9,8,7], 3], "expected": [10,9,8]},
        ]
    },
    "py-hard-8": {
        "visible": [
            {"input": [{"A":{"B":1},"B":{"C":2},"C":{}}, "A"], "expected": {"A":0,"B":1,"C":3}},
        ],
        "hidden": []
    },
    "py-hard-9": {
        "visible": [
            {"input": ["1+2*3"], "expected": 7},
            {"input": ["(2+3)*4"], "expected": 20},
        ],
        "hidden": []
    },
    "py-hard-10": {
        "visible": [
            {"input": [], "expected": "Emitter basic"},
        ],
        "hidden": []
    },
}
